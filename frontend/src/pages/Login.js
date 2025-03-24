import { useState } from "react";
import { useNavigate } from "react-router-dom";
import axios from "axios";
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
        // Signup request
        await axios.post("http://localhost:8001/api/users/", {
          username,
          password,
        });
        setMessage("Signup successful! Please log in.");
        setIsSignup(false);
        setUsername("");
        setPassword("");
      } else {
        // Login request
        const response = await axios.post("http://localhost:8001/api/login", {
          username,
          password,
        });
        localStorage.setItem("token", response.data.access_token);
        setMessage("Login successful!");
        navigate("/home");
      }
    } catch (error) {
      setMessage(
        isSignup
          ? "Signup failed. Username may be taken."
          : "Login failed. Please try again."
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
