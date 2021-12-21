import React, { useState, useEffect } from "react";
import axios from "axios";

export function EigenFaces(K = 10) {
    const [table, setTable] = useState(null);

    async function get(K) {
        let { data } = await axios.post("eigFaces", { K: K });
        setTable(data.files);
    }

    useEffect(() => {
        get(K);
    }, []);

    return (
        <div className="table-wrap">
            {table === null ? (
                <span>Loading...</span>
            ) : (
                <>
                    <div className="text-center">Eigenfaces</div>
                    <div className="table">
                        {table.map((file, i) => {
                            const alt = `eigen face : ${i}`;
                            return (
                                <div key={i}>
                                    <div>
                                        <img src={file} alt={alt} />
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
