import React, { useState } from "react";

type RobotIPInputProps = {
  onConnect?: (ip: string) => void;
};

export default function RobotIPInput({ onConnect }: RobotIPInputProps) {
  const [ip, setIP] = useState("");
  const [isValid, setIsValid] = useState(true);
  const [isTouched, setIsTouched] = useState(false);

  function isValidIPAddress(ip: string): boolean {
    const ipRegex =
      /^(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)(\.(25[0-5]|2[0-4]\d|1\d{2}|[1-9]?\d)){3}$/;
    return ipRegex.test(ip);
  }

  const handleChange = (e: React.ChangeEvent<HTMLInputElement>) => {
    const value = e.target.value;
    setIP(value);
    setIsValid(isValidIPAddress(value) || value === "");
    setIsTouched(true);
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    setIsValid(isValidIPAddress(ip));
    setIsTouched(true);
    if (isValidIPAddress(ip)) {
      // Call parent callback
      if (onConnect) onConnect(ip);
      // Optionally keep the alert or remove it
      alert("Valid IP address submitted: " + ip);
    }
  };

  return (
    <form className="join flex flex-col items-start gap-2" onSubmit={handleSubmit}>
      <label className="text-sm font-semibold mb-1" htmlFor="robot-ip">
        Robot IP Address
      </label>
      <div className="flex items-center gap-2">
        <input
          id="robot-ip"
          type="text"
          className={`input input-bordered rounded-sm text-black ${!isValid && isTouched ? "input-error" : ""}`}
          placeholder="192.168.1.200"
          value={ip}
          onChange={handleChange}
          required
        />
        <button
          className="btn btn-primary rounded-sm"
          type="submit"
          disabled={!isValid || ip === ""}
        >
          Submit
        </button>
      </div>
      {!isValid && isTouched && (
        <span className="text-error text-xs mt-1">
          Please enter a valid IP address.
        </span>
      )}
    </form>
  );
}