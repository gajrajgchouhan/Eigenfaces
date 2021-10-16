import os
from flask import Flask, flash, request, redirect, render_template
import cv2
import numpy as np
from base64 import b64encode
import json
import plotly
import plotly.express as px


def imgToBase64(img):
    return b64encode(cv2.imencode(".jpg", img)[1]).decode()


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

    def eigenfaces(self, K):
        pass

    def plotEigvals(self):
        fig = px.line(np.cumsum(self.eigval), markers=True)
        graphJSON = json.dumps(fig, cls=plotly.utils.PlotlyJSONEncoder)
        return graphJSON


os.environ["FLASK_ENV"] = "development"
app = Flask(__name__, template_folder=".")
app.secret_key = "super secret key"
model = Model()
graphJSON = model.plotEigvals()
header = "Plot of cumulative sum of eigenvalues aka variances."


@app.route("/", methods=["GET", "POST"])
def upload_file():
    if request.method == "POST":
        if "file" not in request.files:
            flash("No file part")
            return redirect(request.url)
        file = request.files["file"]
        if file.filename == "":
            flash("No selected file")
            return redirect(request.url)
        if file:
            encoded_img = file.read()
            img = encodedImgToArray(encoded_img)
            b64_img = imgToBase64(img)
            result = model.predict(img, 150)
            return render_template("index.html", header=header, graphJSON=graphJSON, img_data=b64_img, result=result[0])
    return render_template("index.html", header=header, graphJSON=graphJSON)


if __name__ == "__main__":
    app.run(debug=True)
