import numpy as np

# ============ TIỀN XỬ LÝ ============
class StandardScalerScratch:
    def fit(self, X):
        self.mean_ = np.mean(X, axis=0)
        self.std_ = np.std(X, axis=0) + 1e-9
        return self
    def transform(self, X):
        return (X - self.mean_) / self.std_
    def fit_transform(self, X):
        return self.fit(X).transform(X)

def train_test_split_scratch(X, y, test_size=0.2, random_state=42):
    rng = np.random.RandomState(random_state)
    n = len(X)
    indices = rng.permutation(n)
    n_test = int(n * test_size)
    test_idx, train_idx = indices[:n_test], indices[n_test:]
    return X[train_idx], X[test_idx], y[train_idx], y[test_idx]

# ============ METRICS ============
def confusion_matrix_scratch(y_true, y_pred):
    return {
        'TP': int(np.sum((y_true == 1) & (y_pred == 1))),
        'TN': int(np.sum((y_true == 0) & (y_pred == 0))),
        'FP': int(np.sum((y_true == 0) & (y_pred == 1))),
        'FN': int(np.sum((y_true == 1) & (y_pred == 0)))
    }

def accuracy_score_scratch(y_true, y_pred):
    return float(np.mean(y_true == y_pred))

def precision_score_scratch(y_true, y_pred):
    tp = np.sum((y_true == 1) & (y_pred == 1))
    fp = np.sum((y_true == 0) & (y_pred == 1))
    return float(tp / (tp + fp)) if (tp + fp) > 0 else 0.0

def recall_score_scratch(y_true, y_pred):
    tp = np.sum((y_true == 1) & (y_pred == 1))
    fn = np.sum((y_true == 1) & (y_pred == 0))
    return float(tp / (tp + fn)) if (tp + fn) > 0 else 0.0

def f1_score_scratch(y_true, y_pred):
    p, r = precision_score_scratch(y_true, y_pred), recall_score_scratch(y_true, y_pred)
    return 2 * p * r / (p + r) if (p + r) > 0 else 0.0

# ============ 1. LOGISTIC REGRESSION ============
class LogisticRegressionScratch:
    def __init__(self, lr=0.1, epochs=300):
        self.lr = lr; self.epochs = epochs
        self.weights = None; self.bias = None; self.loss_history = []
    def _sigmoid(self, z):
        return 1 / (1 + np.exp(-np.clip(z, -500, 500)))
    def fit(self, X, y):
        n, m = X.shape
        self.weights = np.zeros(m); self.bias = 0.0
        for _ in range(self.epochs):
            z = X @ self.weights + self.bias
            y_pred = self._sigmoid(z)
            dw = (1 / n) * (X.T @ (y_pred - y))
            db = (1 / n) * np.sum(y_pred - y)
            self.weights -= self.lr * dw
            self.bias -= self.lr * db
            loss = -np.mean(y * np.log(y_pred + 1e-9) + (1 - y) * np.log(1 - y_pred + 1e-9))
            self.loss_history.append(float(loss))
        return self
    def predict_proba(self, X):
        return self._sigmoid(X @ self.weights + self.bias)
    def predict(self, X):
        return (self.predict_proba(X) >= 0.5).astype(int)

# ============ 2. K-NEAREST NEIGHBORS ============
class KNNScratch:
    def __init__(self, k=5):
        self.k = k; self.X_train = None; self.y_train = None
    def fit(self, X, y):
        self.X_train = X; self.y_train = y; return self
    def predict_proba(self, X):
        probs = []
        for x in X:
            distances = np.sqrt(np.sum((self.X_train - x) ** 2, axis=1))
            k_idx = np.argsort(distances)[:self.k]
            probs.append(float(np.mean(self.y_train[k_idx])))
        return np.array(probs)
    def predict(self, X):
        return (self.predict_proba(X) >= 0.5).astype(int)

# ============ 3. GAUSSIAN NAIVE BAYES ============
class GaussianNBScratch:
    def fit(self, X, y):
        self.classes = np.unique(y)
        self.means, self.vars, self.priors = {}, {}, {}
        for c in self.classes:
            X_c = X[y == c]
            self.means[c] = X_c.mean(axis=0)
            self.vars[c] = X_c.var(axis=0) + 1e-9
            self.priors[c] = len(X_c) / len(X)
        return self
    def _gaussian_pdf(self, x, mean, var):
        return np.exp(-((x - mean) ** 2) / (2 * var)) / np.sqrt(2 * np.pi * var)
    def predict_proba(self, X):
        probs = []
        for x in X:
            posteriors = []
            for c in self.classes:
                prior = np.log(self.priors[c])
                likelihood = np.sum(np.log(self._gaussian_pdf(x, self.means[c], self.vars[c])))
                posteriors.append(prior + likelihood)
            posteriors = np.array(posteriors)
            posteriors = np.exp(posteriors - np.max(posteriors))
            posteriors = posteriors / np.sum(posteriors)
            probs.append(float(posteriors[1]))
        return np.array(probs)
    def predict(self, X):
        return (self.predict_proba(X) >= 0.5).astype(int)

# ============ 4. DECISION TREE (ID3 / Entropy) ============
class DecisionTreeScratch:
    def __init__(self, max_depth=4, min_samples_split=5, criterion='entropy'):
        self.max_depth = max_depth
        self.min_samples_split = min_samples_split
        self.criterion = criterion
        self.tree = None
    def _impurity(self, y):
        if len(y) == 0: return 0.0
        p = np.bincount(y) / len(y)
        p = p[p > 0]
        if self.criterion == 'entropy':
            return float(-np.sum(p * np.log2(p)))
        return float(1 - np.sum(p ** 2))
    def _info_gain(self, y, y_l, y_r):
        n = len(y)
        if n == 0: return 0.0
        return self._impurity(y) - (len(y_l) / n) * self._impurity(y_l) - (len(y_r) / n) * self._impurity(y_r)
    def _best_split(self, X, y):
        best = (-1, None, None)
        for f in range(X.shape[1]):
            for t in np.unique(X[:, f]):
                mask = X[:, f] <= t
                if mask.sum() == 0 or (~mask).sum() == 0: continue
                gain = self._info_gain(y, y[mask], y[~mask])
                if gain > best[0]:
                    best = (gain, f, t)
        return best
    def _build(self, X, y, depth=0):
        dist = np.bincount(y, minlength=2).tolist() if len(y) > 0 else [0, 0]
        if depth >= self.max_depth or len(np.unique(y)) == 1 or len(y) < self.min_samples_split:
            return {'leaf': True, 'class': int(np.argmax(dist)), 'dist': dist, 'n': len(y)}
        gain, f, t = self._best_split(X, y)
        if f is None or gain <= 0:
            return {'leaf': True, 'class': int(np.argmax(dist)), 'dist': dist, 'n': len(y)}
        mask = X[:, f] <= t
        return {
            'leaf': False, 'feature': f, 'threshold': float(t), 'gain': float(gain),
            'left': self._build(X[mask], y[mask], depth + 1),
            'right': self._build(X[~mask], y[~mask], depth + 1)
        }
    def fit(self, X, y):
        self.tree = self._build(X, y); return self
    def _walk(self, x, node):
        if node['leaf']: return node['dist']
        return self._walk(x, node['left']) if x[node['feature']] <= node['threshold'] else self._walk(x, node['right'])
    def predict_proba(self, X):
        probs = []
        for x in X:
            d = self._walk(x, self.tree)
            total = sum(d) if sum(d) > 0 else 1
            probs.append(float(d[1] / total))
        return np.array(probs)
    def predict(self, X):
        return (self.predict_proba(X) >= 0.5).astype(int)
    def export_rules(self, feature_names):
        rules = []
        def _ext(node, path):
            if node['leaf']:
                rules.append(f"IF {' AND '.join(path) if path else 'TRUE'} THEN Class={node['class']} (n={node['n']})")
                return
            fname = feature_names[node['feature']]
            _ext(node['left'], path + [f"{fname} <= {node['threshold']:.2f}"])
            _ext(node['right'], path + [f"{fname} > {node['threshold']:.2f}"])
        _ext(self.tree, [])
        return "\n".join(rules)

# ============ 5. ENSEMBLE VOTING ============
class EnsembleVotingScratch:
    def __init__(self, models):
        self.models = models
    def fit(self, X, y):
        for m in self.models: m.fit(X, y)
        return self
    def predict_proba(self, X):
        return np.mean([m.predict_proba(X) for m in self.models], axis=0)
    def predict(self, X):
        return (self.predict_proba(X) >= 0.5).astype(int)

# ============ CROSS-VALIDATION ============
def k_fold_cv_scratch(model_factory, X, y, k=5, random_state=42):
    rng = np.random.RandomState(random_state)
    idx = rng.permutation(len(X))
    fold = len(X) // k
    scores = []
    for i in range(k):
        s, e = i * fold, (i + 1) * fold if i < k - 1 else len(X)
        test_idx = idx[s:e]
        train_idx = np.concatenate([idx[:s], idx[e:]])
        model = model_factory()
        model.fit(X[train_idx], y[train_idx])
        y_pred = model.predict(X[test_idx])
        scores.append(accuracy_score_scratch(y[test_idx], y_pred))
    return float(np.mean(scores)), float(np.std(scores))