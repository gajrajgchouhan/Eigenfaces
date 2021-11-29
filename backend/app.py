import os
from flask import Flask, request
import cv2
import numpy as np
from base64 import b64encode, b64decode
import json
import sys


def base64toEncodedImg(b):
    return b64decode(b)


def imgToBase64(img):
    return b64encode(cv2.imencode(".jpg", img)[1]).decode()


def encodedImgToArray(buf):
    return cv2.imdecode(np.frombuffer(buf, dtype=np.uint8), 0)


def dataURIJPG(b):
    return "data:image/jpeg;base64," + b


def base64ToArray(e):
    e = base64toEncodedImg(e)
    img = encodedImgToArray(e)
    return img


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

    def eigenfaces(self, K=10):
        eigenfaces = self.X_train @ self.eigvec[..., :K]
        for i in range(K):
            img = eigenfaces[..., i].reshape((64, 64))
            img = 255 * (img - img.min()) / (img.max() - img.min())
            img = img.astype("uint8")
            yield imgToBase64(img)


os.environ["FLASK_ENV"] = "development"
app = Flask(__name__, template_folder=".")
app.secret_key = "super secret key"
model = Model()


@app.route("/readImage", methods=["POST"])
def read_image():
    code = 200
    req = request.get_json(force=True)
    print(req, file=sys.stderr)
    if "file" in req:
        _, encoded_img = req["file"].split(",", 1)
        img = base64ToArray(encoded_img)
        result = dataURIJPG(imgToBase64(img))
    else:
        result = "no file"
        code = 404
    return json.dumps({"result": result}), code


@app.route("/predict", methods=["POST"])
def predict():
    code = 200
    req = request.get_json(force=True)
    print(req, file=sys.stderr)
    if "file" in req:
        _, encoded_img = req["file"].split(",", 1)
        img = base64ToArray(encoded_img)
        result = model.predict(img, 150)
        result = result[0]
    else:
        result = "no file"
        code = 404
    return json.dumps({"result": result}), code


@app.route("/eigFaces", methods=["POST"])
def send_eigfaces():
    req = request.get_json(force=True)
    if "K" in req:
        K = req["K"]
    else:
        K = 10
    res = {"files": list(map(dataURIJPG, model.eigenfaces()))}
    return json.dumps(res)


if __name__ == "__main__":
    app.run(debug=True)
