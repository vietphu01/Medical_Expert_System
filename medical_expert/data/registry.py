"""Loaders and input descriptions shared by the dataset commands."""

from medical_expert.data.ckd import load_ckd
from medical_expert.data.loaders import load_cleveland, load_pima
from medical_expert.data.ilpd import load_ilpd


DATASETS = {
    "cleveland": (load_cleveland, "UCI processed.cleveland.data"),
    "pima": (load_pima, "OpenML #37 diabetes.arff"),
    "ilpd": (load_ilpd, "UCI #225 Indian Liver Patient Dataset (ILPD).csv"),
    "ckd": (load_ckd, "UCI #336 data.csv"),
}
