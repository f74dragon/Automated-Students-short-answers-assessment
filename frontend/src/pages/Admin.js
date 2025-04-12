import { useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";
import "../styles/Admin.css";

export default function Admin() {
  const [dataset, setDataset] = useState(null);
  const [modelScore, setModelScore] = useState(null);
  const [manualScore, setManualScore] = useState(null);
  const [comparisonResult, setComparisonResult] = useState(null);
  const [meanAbsoluteError, setMeanAbsoluteError] = useState(null);
  const [selectedModel, setSelectedModel] = useState("default-model");
  const [showModal, setShowModal] = useState(false);
  const navigate = useNavigate();

  const handleDatasetUpload = async (e) => {
    const file = e.target.files[0];
    const formData = new FormData();
    formData.append("dataset", file);

    try {
      const res = await axios.post("http://localhost:8001/api/admin/upload-dataset", formData);
      setDataset(res.data.dataset);
      alert("Dataset uploaded successfully!");
    } catch (err) {
      console.error("Failed to upload dataset", err);
    }
  };

  const handleGetModelScore = async () => {
    try {
      const res = await axios.get("http://localhost:8001/api/admin/model-score");
      setModelScore(res.data.score);
    } catch (err) {
      console.error("Failed to fetch model score", err);
    }
  };

  const handleManualScore = (score) => {
    setManualScore(score);
  };

  const handleCompareScores = () => {
    if (modelScore !== null && manualScore !== null) {
      const error = Math.abs(modelScore - manualScore);
      setMeanAbsoluteError(error);
      setComparisonResult(`Model Score: ${modelScore}, Manual Score: ${manualScore}, Error: ${error}`);
    } else {
      alert("Please ensure both scores are available for comparison.");
    }
  };

  const handleChangeModel = async (model) => {
    try {
      await axios.post("http://localhost:8001/api/admin/change-model", { model });
      setSelectedModel(model);
      alert(`Model changed to ${model}`);
    } catch (err) {
      console.error("Failed to change model", err);
    }
  };

  return (
    <div className="admin-container">
      <div className="taskbar">
        <div className="taskbar-left">
          <Link to="/home">🏠 Home</Link>
          <Link to="/admin">🛠 Admin</Link>
        </div>
        <div className="taskbar-right">
          <span className="user-icon">👤 Admin</span>
        </div>
      </div>

      <div className="content-box">
        <h2>Admin Panel</h2>

        <div className="admin-section">
          <h3>Upload Dataset</h3>
          <input type="file" onChange={handleDatasetUpload} />
        </div>

        <div className="admin-section">
          <h3>Get Model Score</h3>
          <button onClick={handleGetModelScore}>Fetch Model Score</button>
          {modelScore !== null && <p>Model Score: {modelScore}</p>}
        </div>

        <div className="admin-section">
          <h3>Manual Scoring</h3>
          <input
            type="number"
            placeholder="Enter manual score"
            onChange={(e) => handleManualScore(Number(e.target.value))}
          />
          {manualScore !== null && <p>Manual Score: {manualScore}</p>}
        </div>

        <div className="admin-section">
          <h3>Compare Scores</h3>
          <button onClick={handleCompareScores}>Compare</button>
          {comparisonResult && <p>{comparisonResult}</p>}
          {meanAbsoluteError !== null && <p>Mean Absolute Error: {meanAbsoluteError}</p>}
        </div>

        <div className="admin-section">
          <h3>Change Model</h3>
          <select onChange={(e) => handleChangeModel(e.target.value)} value={selectedModel}>
            <option value="default-model">Default Model</option>
            <option value="model-1">Model 1</option>
            <option value="model-2">Model 2</option>
          </select>
        </div>
      </div>

      {showModal && (
        <div className="fullscreen-modal">
          <button className="close-btn" onClick={() => setShowModal(false)}>✖</button>
          <h2>Admin Modal</h2>
          {/* Add modal content here */}
        </div>
      )}
    </div>
  );
}