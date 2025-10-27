import React, { useEffect } from "react";

export default function RobotIPDetection({ onDetect }: { onDetect: () => void }) {
    useEffect(() => {
        onDetect();
    }, [onDetect]);

    return (
        <div className="p-4">
            <span className="loading loading-bars loading-xl"></span>
            <div className="my-4"></div>
            <h2 className="text-lg font-semibold mb-2">Detecting Robot IP Address...</h2>
        </div>
    );
}