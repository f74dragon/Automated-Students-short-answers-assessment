import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";
import "../styles/Admin.css";

export default function Admin() {
  const [loading, setLoading] = useState(true);
  const [activeView, setActiveView] = useState("models");
  const [availableModels, setAvailableModels] = useState([]);
  const [modelName, setModelName] = useState("");
  const [isDownloading, setIsDownloading] = useState(false);
  const [downloadStatus, setDownloadStatus] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem("token");
    if (!token) return navigate("/");
    
    // Decode the token to check if user is admin
    const checkAdminStatus = () => {
      try {
        const decodedToken = JSON.parse(atob(token.split(".")[1]));
        if (!decodedToken.is_admin) {
          // If not admin, redirect to home
          navigate("/home");
        }
        setLoading(false);
      } catch (err) {
        console.error("Failed to check admin status", err);
        navigate("/home");
      }
    };

    checkAdminStatus();
  }, [navigate]);

  useEffect(() => {
    if (activeView === "models" && !loading) {
      fetchModels();
    }
  }, [activeView, loading]);

  const fetchModels = async () => {
    try {
      const response = await axios.get("/api/combinations/models");
      if (response.data && response.data.models) {
        setAvailableModels(response.data.models);
      }
    } catch (err) {
      console.error("Failed to fetch models", err);
    }
  };

  const handleModelPull = async () => {
    if (!modelName.trim()) return;

    try {
      setIsDownloading(true);
      setDownloadStatus(null);
      
      const response = await axios.post("/api/combinations/pull", { 
        model_name: modelName 
      });
      
      setDownloadStatus({ 
        success: true, 
        message: `Successfully pulled model: ${modelName}` 
      });
      
      // Refresh the models list
      fetchModels();
      
      // Clear the input field
      setModelName("");
    } catch (error) {
      setDownloadStatus({ 
        success: false, 
        message: `Failed to pull model: ${error.response?.data?.detail || error.message}`
      });
    } finally {
      setIsDownloading(false);
    }
  };

  const renderSidebar = () => (
    <div className="admin-sidebar">
      <div className="sidebar-header">
        <h3>Admin Panel</h3>
      </div>
      <ul className="sidebar-menu">
        <li 
          className={activeView === "models" ? "active" : ""}
          onClick={() => setActiveView("models")}
        >
          Manage Models
        </li>
        {/* Additional admin options can be added here */}
      </ul>
    </div>
  );

  const renderModelsView = () => (
    <div className="admin-content">
      <h2>Manage Models</h2>
      
      {/* Model Download Form */}
      <div className="model-download-section">
        <h3>Download New Model</h3>
        <p>
          Enter the name of an Ollama model to download.
          <br />
          Available models can be found at <a href="https://ollama.com/library" target="_blank" rel="noopener noreferrer">https://ollama.com/library</a>
        </p>
        
        <div className="model-form">
          <input
            type="text"
            value={modelName}
            onChange={(e) => setModelName(e.target.value)}
            placeholder="Enter model name (e.g., llama3.2)"
            className="model-input"
          />
          <button 
            className="btn-primary"
            onClick={handleModelPull}
            disabled={isDownloading || !modelName}
          >
            {isDownloading ? "Pulling..." : "Pull Model"}
          </button>
        </div>
        
        {downloadStatus && (
          <div className={`download-status ${downloadStatus.success ? 'success' : 'error'}`}>
            {downloadStatus.message}
          </div>
        )}
      </div>
      
      {/* Model List */}
      <div className="model-list-section">
        <h3>Available Models</h3>
        
        <div className="model-cards">
          {availableModels.map((model) => (
            <div key={model.name} className="model-card">
              <div className="model-card-header">
                <h4>{model.name}</h4>
              </div>
              <div className="model-card-content">
                {model.details && (
                  <>
                    <p><strong>Size:</strong> {model.details.parameter_size || "Unknown"}</p>
                    <p><strong>Family:</strong> {model.details.family || "Unknown"}</p>
                    <p><strong>Format:</strong> {model.details.format || "Unknown"}</p>
                  </>
                )}
                <p><strong>Last Modified:</strong> {new Date(model.modified_at).toLocaleString() || "Unknown"}</p>
              </div>
            </div>
          ))}
        </div>
        
        {availableModels.length === 0 && (
          <p>No models found. Pull a model to get started.</p>
        )}
      </div>
    </div>
  );

  if (loading) {
    return <div className="admin-loading">Loading...</div>;
  }

  return (
    <div className="admin-container">
      <div className="taskbar">
        <div className="taskbar-left">
          <Link to="/home">🏠 Home</Link>
          <Link to="/collections">📚 Collections</Link>
          <Link to="/pairs">🔗 Pairs</Link>
          <Link to="/admin">👑 Admin</Link>
        </div>
        <div className="taskbar-right">
          <span className="user-icon">👤</span>
        </div>
      </div>

      <div className="admin-body">
        {renderSidebar()}
        
        <div className="main-content">
          {activeView === "models" && renderModelsView()}
        </div>
      </div>
    </div>
  );
}
