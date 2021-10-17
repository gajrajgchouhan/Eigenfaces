import cv2
import numpy as np
import streamlit as st
from time import time
import plotly.express as px


def encodedImgToArray(buf):
    return cv2.imdecode(np.frombuffer(buf, dtype=np.uint8), 0)


class Model:
    def __init__(self) -> None:
        self.mean = np.load("mean.npy")  # 4096x1
        self.X_train = np.load("X_train.npy")  # 4096xtrain
        self.eigvec = np.load("eigvec.npy")  # trainxtrain
        self.eigval = np.load("eigval.npy")  # train
        self.y_train = np.load("y_train.npy")  # train
        self.no_of_train = self.X_train.shape[1]  # int

    def predict(self, img, K):
        img = cv2.resize(img, (64, 64)).reshape(-1, 1).astype("float")
        img -= self.mean
        u = self.X_train @ self.eigvec[:, :K]
        u = u / np.linalg.norm(u, axis=0)
        reconstructed = self.X_train.T @ u
        test_constructed = img.T @ u
        er = np.zeros((self.no_of_train, 1), dtype="float")
        for i in range(self.no_of_train):
            er[i, 0] = np.linalg.norm(reconstructed[i, :] - test_constructed[0, :])
        pred = self.y_train[np.argmin(er, axis=0)]
        return pred

    def eigenfaces(self):
        faces = self.X_train @ self.eigvec[:, :10]
        for i in range(10):
            yield faces[:, i].reshape(64, 64)


def heading(txt, level=5):
    return "#" * level + " " + txt


model = Model()

"""
# Eigenfaces for face recognition

### Upload a file to test this out!

#### Image is resized to 64x64
#### Dataset (each person appears 70 times in dataset)

- Ariel Sharon
- Colin Powell
- Donald Rumsfeld
- George W Bush
- Gerhard Schroeder
- Hugo Chavez
- Tony Blair

"""

K = st.slider(("How many top eigenvectors to consider?"), 1, model.no_of_train, 150)
uploaded_file = st.file_uploader("Choose a file")
if uploaded_file is not None:
    bytes_data = uploaded_file.getvalue()
    img = encodedImgToArray(bytes_data)
    st.write(heading("Uploaded pic:"))
    st.image(img, width=256)
    with st.spinner("Predicting.....:)"):
        s = time()
        result = model.predict(img, K)
        e = time()
    st.write(heading(f"Execution time: {e-s:.4f} (seconds)"))
    st.write(heading(f"Result: {result[0]}"))

st.write(heading("Plot of cumulative sum of eigenvalues aka variances."))
fig = px.line(np.cumsum(model.eigval), markers=True)
st.plotly_chart(fig)
