import React, { useState, useEffect } from "react";
import axios from "axios";

export function EigenFaces(K = 10) {
    const [table, setTable] = useState(null);
    async function get(K) {
        let { data } = await axios.post("eigFaces", { K: K });
        setTable(data.files);
    }
    console.log("EigenFaces");
    useEffect(() => {
        get(K);
    }, []);

    useEffect(() => {
        console.log("rerender");
    }, [table]);

    return (
        <div>
            {table === null ? (
                <span>Loading...</span>
            ) : (
                <>
                    <div className="text-center">Eigenfaces</div>
                    <div className="table">
                        {table.map((file, i) => {
                            return (
                                <div key={i}>
                                    <div>
                                        <img src={file} />
                                    </div>
                                    <div>{i}</div>
                                </div>
                            );
                        })}
                    </div>
                </>
            )}
        </div>
    );
}
