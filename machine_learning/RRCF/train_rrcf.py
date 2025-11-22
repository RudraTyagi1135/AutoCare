import pickle
import numpy as np
from rrcf import RCTree


def train_rrcf_for(dataset_path, save_path, ntrees=40, size=256):
    X = np.load(dataset_path)

    forest = []
    for _ in range(ntrees):
        idx = np.random.choice(len(X), size=size, replace=False)
        tree = RCTree(X[idx])
        forest.append(tree)

    pickle.dump(forest, open(save_path, "wb"))


train_rrcf_for(
    "machine_learning/training/diabetes/.../train.npy",
    "machine_learning/RRCF/diabetes_rrcf.pkl"
)

train_rrcf_for(
    "machine_learning/training/heart/.../train.npy",
    "machine_learning/RRCF/heart_rrcf.pkl"
)

train_rrcf_for(
    "machine_learning/training/stroke/.../train.npy",
    "machine_learning/RRCF/stroke_rrcf.pkl"
)
