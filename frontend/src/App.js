import { BrowserRouter as Router, Route, Routes } from "react-router-dom";
import axios from "axios";
import Login from "./pages/Login";
import Home from "./pages/Home";
import CollectionDetails from "./pages/CollectionDetails";
import Pairs from "./pages/Pairs";
import Admin from "./pages/Admin";
import TestingWizard from "./pages/TestingWizard";

// Global Axios Configuration
axios.defaults.baseURL = window.location.origin;
axios.defaults.withCredentials = true;

// Configure axios to include authentication token in all requests
axios.interceptors.request.use(
  (config) => {
    const token = localStorage.getItem("token");
    if (token) {
      config.headers.Authorization = `Bearer ${token}`;
    }
    return config;
  },
  (error) => Promise.reject(error)
);

function App() {
  return (
    <Router>
      <Routes>
        <Route path="/" element={<Login />} />
        <Route path="/home" element={<Home />} />
        <Route path="/collection/:id" element={<CollectionDetails />} />
        <Route path="/pairs" element={<Pairs />} />
        <Route path="/admin" element={<Admin />} />
        <Route path="/testing-wizard" element={<TestingWizard />} />
      </Routes>
    </Router>
  );
}

export default App;
