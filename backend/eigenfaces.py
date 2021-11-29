import os
import numpy as np
import cv2
from sklearn.model_selection import train_test_split
from collections import Counter
import random
from shutil import copy

save_dir = "./dataset/"
os.makedirs(save_dir, exist_ok=True)
image_dir = "lfwcrop_grey/faces"

celebrity_photos = os.listdir(image_dir)
celebrity_images = np.array([os.path.join(image_dir, photo) for photo in celebrity_photos])
celebrity_names = np.array([name[: name.find("0") - 1].replace("_", " ") for name in celebrity_photos])

min_freq = 70
allowed_index = []

for name, freq in Counter(celebrity_names).items():
    if freq >= min_freq:
        allowed_index.extend((random.sample(list(np.nonzero(celebrity_names == name)[0]), min_freq)))
allowed_index = np.array(allowed_index, dtype="int")
celebrity_images = celebrity_images[allowed_index]

for image in celebrity_images:
    _, file = os.path.split(image)
    copy(image, os.path.join(save_dir, file))
celebrity_names = celebrity_names[allowed_index]
print(np.unique(celebrity_names))

arrayimages = np.array([cv2.imread(image, 0).ravel() for image in celebrity_images], dtype=np.float64).T
X_train, X_test, y_train, y_test = train_test_split(range(arrayimages.shape[1]), celebrity_names, test_size=0.2)
X_train = arrayimages[:, X_train]

mean = np.mean(X_train, axis=1, keepdims=True)
X_train -= mean

cov = X_train.T @ X_train
cov = cov / (cov.shape[0] - 1)

eigval, eigvec = np.linalg.eig(cov)
order = eigval.argsort()[::-1]
eigval = eigval[order]
eigvec = eigvec[:, order]

np.save("X_train.npy", X_train)
np.save("mean.npy", mean)
np.save("eigvec.npy", eigvec)
np.save("eigval.npy", eigval / np.sum(eigval))
np.save("y_train.npy", y_train)
