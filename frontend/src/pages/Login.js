import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
import api, { handleApiError } from "../utils/api";
import "../styles/Login.css";

export default function Login() {
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [message, setMessage] = useState("");
  const [isSignup, setIsSignup] = useState(false);
  const navigate = useNavigate();

  const handleSubmit = async (e) => {
    e.preventDefault();
    try {
      if (isSignup) {
        // Signup request - use direct axios for this since we don't need auth
        await axios.post("http://localhost:8001/api/users/", {
          username,
          password,
        });
        setMessage("Signup successful! Please log in.");
        setIsSignup(false);
        setUsername("");
        setPassword("");
      } else {
        // Login request - use direct axios since we're getting the token
        const response = await axios.post("http://localhost:8001/api/login", {
          username,
          password,
        });
        // Store the token in localStorage
        localStorage.setItem("token", response.data.access_token);
        setMessage("Login successful!");
        navigate("/home");
      }
    } catch (error) {
      const errorMsg = handleApiError(error);
      setMessage(
        isSignup
          ? `Signup failed: ${errorMsg}`
          : `Login failed: ${errorMsg}`
      );
    }
  };

  return (
    <div className="login-container">
      <div className="login-box">
        <h2 className="login-title">{isSignup ? "Sign Up" : "Login"}</h2>
        <form onSubmit={handleSubmit}>
          <input
            type="text"
            placeholder="Username"
            value={username}
            onChange={(e) => setUsername(e.target.value)}
            required
          />
          <input
            type="password"
            placeholder="Password"
            value={password}
            onChange={(e) => setPassword(e.target.value)}
            required
          />
          <button className="login-button" type="submit">
            {isSignup ? "Sign Up" : "Login"}
          </button>
        </form>
        <button
          className="login-button"
          onClick={() => {
            setIsSignup((prev) => !prev);
            setMessage("");
          }}
        >
          {isSignup ? "Already have an account? Login" : "New user? Sign up"}
        </button>
        {message && <p className="login-message">{message}</p>}
      </div>
    </div>
  );
}
