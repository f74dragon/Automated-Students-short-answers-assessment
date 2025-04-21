import { useState, useEffect } from "react";
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
  const [promptTemplate, setPromptTemplate] = useState("");
  const [isDefaultPrompt, setIsDefaultPrompt] = useState(true);
  const [loading, setLoading] = useState(false);
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

  // Fetch current prompt template on component mount
  useEffect(() => {
    const fetchPromptTemplate = async () => {
      try {
        setLoading(true);
        const token = localStorage.getItem("token");
        if (!token) {
          console.warn("No authentication token found");
          return;
        }
        
        const response = await axios.get("http://localhost:8001/api/prompt", {
          headers: { Authorization: `Bearer ${token}` }
        });
        setPromptTemplate(response.data.template);
        setIsDefaultPrompt(response.data.is_default);
      } catch (error) {
        console.error("Failed to fetch prompt template:", error);
        if (error.response && error.response.status === 401) {
          alert("Authentication failed. Please log in again.");
          // Optionally redirect to login page
          // navigate("/login");
        } else {
          alert("Failed to load prompt template");
        }
      } finally {
        setLoading(false);
      }
    };

    fetchPromptTemplate();
  }, []);

  // Handle updating the prompt template
  const handleUpdatePrompt = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("token");
      if (!token) {
        alert("Authentication required. Please log in.");
        return;
      }
      
      const response = await axios.post("http://localhost:8001/api/prompt/update", 
        { template: promptTemplate },
        { headers: { Authorization: `Bearer ${token}` }}
      );
      
      setPromptTemplate(response.data.template);
      setIsDefaultPrompt(response.data.is_default);
      alert("Prompt template updated successfully!");
    } catch (error) {
      console.error("Failed to update prompt template:", error);
      if (error.response && error.response.status === 401) {
        alert("Authentication failed. Please log in again.");
        // Optionally redirect to login page
        // navigate("/login");
      } else {
        alert("Failed to update prompt template. Make sure all required placeholders are included.");
      }
    } finally {
      setLoading(false);
    }
  };

  // Handle resetting the prompt template to default
  const handleResetPrompt = async () => {
    try {
      setLoading(true);
      const token = localStorage.getItem("token");
      if (!token) {
        alert("Authentication required. Please log in.");
        return;
      }
      
      const response = await axios.post("http://localhost:8001/api/prompt/reset", 
        {},
        { headers: { Authorization: `Bearer ${token}` }}
      );
      
      setPromptTemplate(response.data.template);
      setIsDefaultPrompt(response.data.is_default);
      alert("Prompt template reset to default!");
    } catch (error) {
      console.error("Failed to reset prompt template:", error);
      if (error.response && error.response.status === 401) {
        alert("Authentication failed. Please log in again.");
        // Optionally redirect to login page
        // navigate("/login");
      } else {
        alert("Failed to reset prompt template");
      }
    } finally {
      setLoading(false);
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

        <div className="admin-section">
          <h3>Customize Grading Prompt</h3>
          <div className="prompt-info">
            <p>
              Customize the prompt template used by the LLM to grade student answers.
              Make sure to include the required placeholders:
            </p>
            <ul>
              <li><code>{"{question}"}</code> - The question being asked</li>
              <li><code>{"{model_answer}"}</code> - The correct answer</li>
              <li><code>{"{student_answer}"}</code> - The student's answer being graded</li>
            </ul>
          </div>
          
          <div className="prompt-editor">
            <textarea
              rows="10"
              value={promptTemplate}
              onChange={(e) => setPromptTemplate(e.target.value)}
              disabled={loading}
              placeholder="Loading prompt template..."
              className="prompt-textarea"
            />
            
            <div className="prompt-actions">
              <button 
                onClick={handleUpdatePrompt}
                disabled={loading}
                className="update-prompt-btn"
              >
                {loading ? "Saving..." : "Save Changes"}
              </button>
              
              <button 
                onClick={handleResetPrompt}
                disabled={loading || isDefaultPrompt}
                className="reset-prompt-btn"
              >
                Reset to Default
              </button>
            </div>
            
            {isDefaultPrompt && (
              <div className="default-prompt-indicator">
                <small>Using default prompt template</small>
              </div>
            )}
          </div>
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
