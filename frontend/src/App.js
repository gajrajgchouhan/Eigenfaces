import React, { useRef } from "react";
import { EigenFaces } from "./EigenFaces";
import { InputForm } from "./InputForm";

function App() {
    const K = useRef(10);
    return (
        <>
            <InputForm />
            <EigenFaces K={K} />
        </>
    );
}

export default App;
