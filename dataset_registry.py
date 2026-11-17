"""Loaders and input descriptions shared by the dataset commands."""

from ckd_loader import load_ckd
from dataset_loaders import load_cleveland, load_pima
from ilpd_loader import load_ilpd


DATASETS = {
    "cleveland": (load_cleveland, "UCI processed.cleveland.data"),
    "pima": (load_pima, "OpenML #37 diabetes.arff"),
    "ilpd": (load_ilpd, "UCI #225 Indian Liver Patient Dataset (ILPD).csv"),
    "ckd": (load_ckd, "UCI #336 data.csv"),
}
