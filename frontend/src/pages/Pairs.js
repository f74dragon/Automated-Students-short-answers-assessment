import React, { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";
import "../styles/Pairs.css";

// Default prompt template for new combinations
const DEFAULT_PROMPT = `Question: {{question}}

Correct Answer: {{model_answer}}

Student's Answer: {{student_answer}}

Grade the student's answer based on the correct answer from (0.0 - 1.0). 
Provide a brief explanation for your grade.`;

export default function Pairs() {
  const [activeView, setActiveView] = useState("create"); // 'create' or 'list'
  const [currentStep, setCurrentStep] = useState(1); // steps 1, 2, 3
  const [name, setName] = useState("");
  const [description, setDescription] = useState("");
  const [prompt, setPrompt] = useState(DEFAULT_PROMPT);
  const [availableModels, setAvailableModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState("");
  const [combinations, setCombinations] = useState([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const navigate = useNavigate();

  // Fetch combinations and models on component mount
  useEffect(() => {
    if (activeView === "list") {
      fetchCombinations();
    }
    if (activeView === "create" && currentStep === 2) {
      fetchModels();
    }
  }, [activeView, currentStep]);

  const fetchCombinations = async () => {
    setIsLoading(true);
    try {
      const response = await axios.get("/api/combinations/");
      setCombinations(response.data);
    } catch (err) {
      setError("Failed to fetch combinations");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchModels = async () => {
    setIsLoading(true);
    try {
      const response = await axios.get("/api/combinations/models");
      setAvailableModels(response.data.models || []);
      if (response.data.models && response.data.models.length > 0) {
        setSelectedModel(response.data.models[0].name);
      }
    } catch (err) {
      setError("Failed to fetch models from Ollama");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateCombination = async () => {
    if (!name || !prompt || !selectedModel) {
      setError("Please provide a name, prompt, and select a model");
      return;
    }

    setIsLoading(true);
    try {
      await axios.post("/api/combinations/", {
        name,
        description,
        prompt,
        model_name: selectedModel
      });
      setActiveView("list");
      fetchCombinations();
    } catch (err) {
      setError("Failed to create combination");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleDeleteCombination = async (id) => {
    if (!window.confirm("Are you sure you want to delete this combination?")) {
      return;
    }
    
    setIsLoading(true);
    try {
      await axios.delete(`/api/combinations/${id}`);
      fetchCombinations();
    } catch (err) {
      setError("Failed to delete combination. It may be in use by collections.");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNext = () => {
    if (currentStep < 3) {
      setCurrentStep(currentStep + 1);
    } else {
      // Submit on the last step
      handleCreateCombination();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
    }
  };

  const renderSidebar = () => (
    <div className="pairs-sidebar">
      <div className="sidebar-header">
        <h3>Prompt-Model Pairs</h3>
      </div>
      <ul className="sidebar-menu">
        <li 
          className={activeView === "create" ? "active" : ""}
          onClick={() => {
            setActiveView("create");
            setCurrentStep(1);
            setName("");
            setDescription("");
            setPrompt(DEFAULT_PROMPT);
          }}
        >
          Create New Pair
        </li>
        <li 
          className={activeView === "list" ? "active" : ""}
          onClick={() => setActiveView("list")}
        >
          View Pairs
        </li>
      </ul>
    </div>
  );

  const renderStepIndicator = () => (
    <div className="steps-indicator">
      <div className={`step ${currentStep >= 1 ? "active" : ""}`}>
        <div className="step-number">1</div>
        <div className="step-text">Create Prompt</div>
      </div>
      <div className="step-connector"></div>
      <div className={`step ${currentStep >= 2 ? "active" : ""}`}>
        <div className="step-number">2</div>
        <div className="step-text">Select Model</div>
      </div>
      <div className="step-connector"></div>
      <div className={`step ${currentStep >= 3 ? "active" : ""}`}>
        <div className="step-number">3</div>
        <div className="step-text">Save</div>
      </div>
    </div>
  );

  const renderCreateView = () => (
    <div className="pairs-content">
      {renderStepIndicator()}
      
      <div className="content-body">
        {currentStep === 1 && (
          <div className="step-content">
            <h3>Step 1: Create Prompt</h3>
            
            <div className="form-group">
              <label htmlFor="combination-name">Name *</label>
              <input 
                type="text"
                id="combination-name"
                value={name}
                onChange={(e) => setName(e.target.value)}
                className="form-control"
                placeholder="Enter a name for this prompt-model pair"
                required
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="combination-description">Description (optional)</label>
              <input 
                type="text"
                id="combination-description"
                value={description}
                onChange={(e) => setDescription(e.target.value)}
                className="form-control"
                placeholder="Add a short description of this combination"
              />
            </div>
            
            <div className="form-group">
              <label htmlFor="prompt-template">Prompt Template *</label>
              <textarea
                id="prompt-template"
                value={prompt}
                onChange={(e) => setPrompt(e.target.value)}
                className="prompt-textarea"
                placeholder="Enter your prompt template..."
                required
              />
            </div>
            
            <div className="prompt-help">
              <h4>Available Variables:</h4>
              <ul>
                <li><code>{'{{question}}'}</code> - The question being asked</li>
                <li><code>{'{{model_answer}}'}</code> - The model/correct answer</li>
                <li><code>{'{{student_answer}}'}</code> - The student's answer to grade</li>
              </ul>
            </div>
          </div>
        )}

        {currentStep === 2 && (
          <div className="step-content">
            <h3>Step 2: Select Model</h3>
            <p>Choose the LLM model to use with this prompt.</p>
            
            {isLoading ? (
              <p>Loading models...</p>
            ) : (
              <div className="model-selector">
                <select 
                  value={selectedModel} 
                  onChange={(e) => setSelectedModel(e.target.value)}
                >
                  {availableModels.map((model) => (
                    <option key={model.name} value={model.name}>
                      {model.name} ({model.details?.parameter_size || "Unknown size"})
                    </option>
                  ))}
                </select>
                
                {selectedModel && (
                  <div className="model-details">
                    <h4>Selected Model: {selectedModel}</h4>
                    {availableModels.find(m => m.name === selectedModel)?.details && (
                      <div>
                        <p>Size: {availableModels.find(m => m.name === selectedModel)?.details?.parameter_size || "Unknown"}</p>
                        <p>Family: {availableModels.find(m => m.name === selectedModel)?.details?.family || "Unknown"}</p>
                        <p>Format: {availableModels.find(m => m.name === selectedModel)?.details?.format || "Unknown"}</p>
                      </div>
                    )}
                  </div>
                )}
              </div>
            )}
          </div>
        )}

        {currentStep === 3 && (
          <div className="step-content">
            <h3>Step 3: Review and Save</h3>
            <div className="review-summary">
              <h4>Name:</h4>
              <p>{name}</p>
              
              {description && (
                <>
                  <h4>Description:</h4>
                  <p>{description}</p>
                </>
              )}
              
              <h4>Prompt Template:</h4>
              <pre>{prompt}</pre>
              
              <h4>Selected Model:</h4>
              <p>{selectedModel}</p>
              
              <p>Click "Save" to create this prompt-model pair.</p>
            </div>
          </div>
        )}
      </div>

      <div className="step-actions">
        {currentStep > 1 && (
          <button onClick={handlePrevious} className="btn btn-secondary">
            Previous
          </button>
        )}
        <button 
          onClick={handleNext} 
          className="btn btn-primary"
          disabled={isLoading}
        >
          {currentStep < 3 ? "Next" : "Save"}
        </button>
      </div>
    </div>
  );

  const renderListView = () => (
    <div className="pairs-content">
      <h2>Prompt-Model Pairs</h2>
      
      {isLoading ? (
        <p>Loading combinations...</p>
      ) : combinations.length === 0 ? (
        <p>No combinations found. Create a new one to get started.</p>
      ) : (
        <div className="combinations-list">
          {combinations.map((combination) => (
            <div key={combination.id} className="combination-card">
              <div className="combination-header">
                <h3>{combination.name}</h3>
                <div className="combination-actions">
                  <button 
                    onClick={() => handleDeleteCombination(combination.id)}
                    className="btn btn-danger btn-sm"
                  >
                    Delete
                  </button>
                </div>
              </div>
              <div className="combination-body">
                {combination.description && (
                  <div className="description">
                    <p>{combination.description}</p>
                  </div>
                )}
                
                <h4>Model:</h4>
                <p>{combination.model_name}</p>
                
                <h4>Prompt Template:</h4>
                <pre className="prompt-preview">{combination.prompt}</pre>
              </div>
              {combination.collections && combination.collections.length > 0 && (
                <div className="combination-footer">
                  <h4>Used by Collections:</h4>
                  <ul>
                    {combination.collections.map((collection) => (
                      <li key={collection.id}>{collection.name}</li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>
      )}
    </div>
  );

  return (
    <div className="pairs-container">
      <div className="taskbar">
        <div className="taskbar-left">
          <Link to="/home">🏠 Home</Link>
          <Link to="/collections">📚 Collections</Link>
          <Link to="/pairs">🔗 Pairs</Link>
        </div>
        <div className="taskbar-right">
          <span className="user-icon">👤 User</span>
        </div>
      </div>

      <div className="pairs-body">
        {renderSidebar()}
        
        <div className="main-content">
          {error && (
            <div className="error-message">
              {error}
              <button onClick={() => setError(null)}>✕</button>
            </div>
          )}
          
          {activeView === "create" ? renderCreateView() : renderListView()}
        </div>
      </div>
    </div>
  );
}
