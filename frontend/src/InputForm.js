import React, { useState } from "react";
import axios from "axios";

export function InputForm() {
    const [selectedImage, setSelectedImage] = useState("");
    const [isFilePicked, setIsFilePicked] = useState(false);
    const [prediction, setPrediction] = useState(null);

    const readFile = (inputFile) => {
        return new Promise((resolve, reject) => {
            const temporaryFileReader = new FileReader();
            temporaryFileReader.onerror = () => {
                temporaryFileReader.abort();
                reject(new DOMException("Problem parsing input file."));
            };

            temporaryFileReader.onload = () => {
                resolve(temporaryFileReader.result);
            };
            temporaryFileReader.readAsDataURL(inputFile);
        });
    };

    const changeHandler = (event) => {
        setPrediction(null);
        const file = event.target.files[0];
        readFile(file).then((result) => {
            const finalFile = result;
            axios.post("/readImage", { file: finalFile }).then(({ data }) => {
                setSelectedImage(data.result);
                setIsFilePicked(true);
            });
        });
    };

    const handleSubmission = () => {
        axios.post("/predict", { file: selectedImage }).then(({ data }) => {
            const prediction = data.result;
            setPrediction(prediction);
        });
    };

    console.log("inputForm");
    return (
        <>
            <div className="form">
                <input
                    type="file"
                    id="form-input"
                    onChange={changeHandler}
                    hidden
                />
                <label className="input-label" htmlFor="form-input">
                    Upload a File
                </label>
                {isFilePicked ? (
                    <div className="file-picked">
                        <img
                            id="uploadedImage"
                            src={selectedImage}
                            alt="uploadedImage"
                        />
                    </div>
                ) : (
                    <p>Select a file to predict</p>
                )}
                <button className="form-btn" onClick={handleSubmission}>
                    Submit
                </button>
            </div>
            {prediction !== null ? <div>Predicted: {prediction}</div> : <></>}
        </>
    );
}
