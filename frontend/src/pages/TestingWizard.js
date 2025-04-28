import React, { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";
import "../styles/TestingWizard.css";

export default function TestingWizard() {
  const [currentStep, setCurrentStep] = useState(1); // steps 1, 2, 3
  const [availableModels, setAvailableModels] = useState([]);
  const [selectedModels, setSelectedModels] = useState([]);
  const [availablePrompts, setAvailablePrompts] = useState([]);
  const [selectedPrompts, setSelectedPrompts] = useState([]);
  const [categories, setCategories] = useState([]);
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [csvFile, setCsvFile] = useState(null);
  const [csvPreview, setCsvPreview] = useState(null);
  const [testName, setTestName] = useState("");
  const [testDescription, setTestDescription] = useState("");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [testId, setTestId] = useState(null);
  const navigate = useNavigate();

  // Fetch data based on current step
  useEffect(() => {
    if (currentStep === 1) {
      fetchModels();
    } else if (currentStep === 2) {
      fetchPrompts();
      fetchCategories();
    }
  }, [currentStep, selectedCategory]);

  const fetchModels = async () => {
    setIsLoading(true);
    try {
      const response = await axios.get("/api/combinations/models");
      if (response.data && response.data.models) {
        setAvailableModels(response.data.models);
      }
    } catch (err) {
      setError("Failed to fetch models");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchPrompts = async () => {
    setIsLoading(true);
    try {
      const category = selectedCategory !== "All" ? selectedCategory : undefined;
      const response = await axios.get("/api/prompts/", {
        params: { category }
      });
      setAvailablePrompts(response.data);
    } catch (err) {
      setError("Failed to fetch prompts");
      console.error(err);
    } finally {
      setIsLoading(false);
    }
  };

  const fetchCategories = async () => {
    try {
      const response = await axios.get("/api/prompts/categories/all");
      if (response.data && response.data.categories) {
        setCategories(["All", ...response.data.categories]);
      }
    } catch (err) {
      console.error("Failed to fetch categories", err);
    }
  };

  const handleModelSelect = (modelName) => {
    if (selectedModels.includes(modelName)) {
      setSelectedModels(selectedModels.filter(name => name !== modelName));
    } else {
      setSelectedModels([...selectedModels, modelName]);
    }
  };

  const handlePromptSelect = (promptId) => {
    if (selectedPrompts.includes(promptId)) {
      setSelectedPrompts(selectedPrompts.filter(id => id !== promptId));
    } else {
      setSelectedPrompts([...selectedPrompts, promptId]);
    }
  };

  const handleCategoryChange = (category) => {
    setSelectedCategory(category);
  };

  const handleFileChange = (e) => {
    const file = e.target.files[0];
    if (file) {
      setCsvFile(file);
      
      // Preview the CSV
      const reader = new FileReader();
      reader.onload = (event) => {
        const content = event.target.result;
        
        // Parse the first few lines for preview
        const lines = content.split('\n').slice(0, 6); // Header + 5 rows
        if (lines.length > 0) {
          setCsvPreview({
            header: lines[0],
            rows: lines.slice(1, 6)
          });
        }
      };
      reader.readAsText(file);
    }
  };

  const handleCreateTest = async () => {
    if (!testName || selectedModels.length === 0 || selectedPrompts.length === 0) {
      setError("Please provide a test name, select at least one model and prompt");
      return;
    }

    setIsLoading(true);
    try {
      // Create the test configuration
      const response = await axios.post("/api/tests/", {
        name: testName,
        description: testDescription,
        model_names: selectedModels,
        prompt_ids: selectedPrompts
      });

      setTestId(response.data.id);
      
      // Go to the next step if successful
      setCurrentStep(currentStep + 1);
    } catch (err) {
      setError(`Failed to create test: ${err.response?.data?.detail || err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleUploadCsv = async () => {
    if (!csvFile) {
      setError("Please select a CSV file to upload");
      return;
    }

    setIsLoading(true);
    try {
      const formData = new FormData();
      formData.append("file", csvFile);

      await axios.post(`/api/tests/${testId}/upload`, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      // Navigate to test results view or dashboard
      navigate(`/admin?view=tests&id=${testId}`);
    } catch (err) {
      setError(`Failed to upload CSV: ${err.response?.data?.detail || err.message}`);
    } finally {
      setIsLoading(false);
    }
  };

  const handleNext = () => {
    // Validation logic for each step
    if (currentStep === 1 && selectedModels.length === 0) {
      setError("Please select at least one model");
      return;
    } else if (currentStep === 2 && selectedPrompts.length === 0) {
      setError("Please select at least one prompt");
      return;
    }

    if (currentStep < 3) {
      setCurrentStep(currentStep + 1);
      setError(null);
    } else {
      // For the last step (3), we initiate the test creation
      handleCreateTest();
    }
  };

  const handlePrevious = () => {
    if (currentStep > 1) {
      setCurrentStep(currentStep - 1);
      setError(null);
    }
  };

  const handleFinish = () => {
    handleUploadCsv();
  };

  const renderStepIndicator = () => (
    <div className="steps-indicator">
      <div className={`step ${currentStep >= 1 ? "active" : ""}`}>
        <div className="step-number">1</div>
        <div className="step-text">Select Models</div>
      </div>
      <div className="step-connector"></div>
      <div className={`step ${currentStep >= 2 ? "active" : ""}`}>
        <div className="step-number">2</div>
        <div className="step-text">Select Prompts</div>
      </div>
      <div className="step-connector"></div>
      <div className={`step ${currentStep >= 3 ? "active" : ""}`}>
        <div className="step-number">3</div>
        <div className="step-text">Upload Test Questions</div>
      </div>
      <div className="step-connector"></div>
      <div className={`step ${currentStep >= 4 ? "active" : ""}`}>
        <div className="step-number">4</div>
        <div className="step-text">Run Test</div>
      </div>
    </div>
  );

  const renderModelSelectionStep = () => (
    <div className="step-content">
      <h3>Step 1: Select Models</h3>
      <p>Choose one or more models to test</p>
      
      {isLoading ? (
        <p>Loading models...</p>
      ) : (
        <div className="model-selection-grid">
          {availableModels.map((model) => (
            <div
              key={model.name}
              className={`model-card ${selectedModels.includes(model.name) ? "selected" : ""}`}
              onClick={() => handleModelSelect(model.name)}
            >
              <div className="model-card-header">
                <h4>{model.name}</h4>
                <div className="model-select-indicator">
                  {selectedModels.includes(model.name) && <span>✓</span>}
                </div>
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
      )}
      
      {availableModels.length === 0 && !isLoading && (
        <p>No models found. Please pull models in the Admin panel first.</p>
      )}
    </div>
  );

  const renderPromptSelectionStep = () => (
    <div className="step-content">
      <h3>Step 2: Select Prompts</h3>
      <p>Choose one or more prompts to test</p>
      
      <div className="category-filter">
        <label htmlFor="category-filter">Filter by Category:</label>
        <select
          id="category-filter"
          value={selectedCategory}
          onChange={(e) => handleCategoryChange(e.target.value)}
        >
          {categories.map(category => (
            <option key={category} value={category}>{category}</option>
          ))}
        </select>
      </div>
      
      {isLoading ? (
        <p>Loading prompts...</p>
      ) : (
        <div className="prompt-selection-grid">
          {availablePrompts.map((prompt) => (
            <div
              key={prompt.id}
              className={`prompt-card ${selectedPrompts.includes(prompt.id) ? "selected" : ""}`}
              onClick={() => handlePromptSelect(prompt.id)}
            >
              <div className="prompt-card-header">
                <h4>{prompt.name}</h4>
                <div className="prompt-select-indicator">
                  {selectedPrompts.includes(prompt.id) && <span>✓</span>}
                </div>
              </div>
              <div className="prompt-card-content">
                <div className="prompt-card-category">
                  <strong>Category:</strong> {prompt.category}
                </div>
                <div className="prompt-card-text">
                  <strong>Prompt:</strong>
                  <pre>{prompt.prompt}</pre>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
      
      {availablePrompts.length === 0 && !isLoading && (
        <p>No prompts found. Please create prompts in the Admin panel first.</p>
      )}
    </div>
  );

  const renderTestUploadStep = () => (
    <div className="step-content">
      <h3>Step 3: Upload Test Questions</h3>
      <p>Upload a CSV file containing test questions</p>
      
      <div className="form-group">
        <label htmlFor="test-name">Test Name *</label>
        <input
          type="text"
          id="test-name"
          value={testName}
          onChange={(e) => setTestName(e.target.value)}
          className="form-control"
          placeholder="Enter a name for this test"
          required
        />
      </div>
      
      <div className="form-group">
        <label htmlFor="test-description">Description (optional)</label>
        <input
          type="text"
          id="test-description"
          value={testDescription}
          onChange={(e) => setTestDescription(e.target.value)}
          className="form-control"
          placeholder="Add a short description of this test"
        />
      </div>
      
      <div className="csv-upload-section">
        <p>The CSV file must contain the following columns:</p>
        <ul>
          <li>Question</li>
          <li>Model Answer</li>
          <li>Student Answer</li>
          <li>Model Grade</li>
        </ul>
        
        <div className="file-input-container">
          <label htmlFor="csv-file" className="file-input-label">
            Choose CSV File
          </label>
          <input
            type="file"
            id="csv-file"
            accept=".csv"
            onChange={handleFileChange}
            className="file-input"
          />
          {csvFile && <p className="file-name">{csvFile.name}</p>}
        </div>
      </div>
      
      {csvPreview && (
        <div className="csv-preview">
          <h4>CSV Preview</h4>
          <div className="csv-preview-content">
            <div className="csv-preview-header">
              {csvPreview.header}
            </div>
            {csvPreview.rows.map((row, index) => (
              <div key={index} className="csv-preview-row">
                {row}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

  const renderTestRunStep = () => (
    <div className="step-content">
      <h3>Step 4: Run Test</h3>
      <p>Review test configuration and run the test</p>
      
      <div className="test-summary">
        <h4>Test Summary</h4>
        <p><strong>Name:</strong> {testName}</p>
        {testDescription && <p><strong>Description:</strong> {testDescription}</p>}
        
        <div className="test-models">
          <h5>Selected Models ({selectedModels.length})</h5>
          <ul>
            {selectedModels.map(model => (
              <li key={model}>{model}</li>
            ))}
          </ul>
        </div>
        
        <div className="test-prompts">
          <h5>Selected Prompts ({selectedPrompts.length})</h5>
          <ul>
            {availablePrompts
              .filter(prompt => selectedPrompts.includes(prompt.id))
              .map(prompt => (
                <li key={prompt.id}>{prompt.name} ({prompt.category})</li>
              ))}
          </ul>
        </div>
        
        {csvFile && (
          <div className="test-csv">
            <h5>Test Data</h5>
            <p>{csvFile.name} ({(csvFile.size / 1024).toFixed(2)} KB)</p>
          </div>
        )}
      </div>
      
      <p className="test-instruction">Click "Run Test" to upload the CSV file and start the test.</p>
    </div>
  );

  return (
    <div className="testing-wizard-container">
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

      <div className="testing-wizard-body">
        <div className="sidebar">
          <div className="sidebar-header">
            <h3>Testing Wizard</h3>
          </div>
          <ul className="sidebar-menu">
            <li className="active">Create Test</li>
            <li><Link to="/admin?view=tests">View Tests</Link></li>
          </ul>
        </div>
        
        <div className="main-content">
          {error && (
            <div className="error-message">
              {error}
              <button onClick={() => setError(null)}>✕</button>
            </div>
          )}
          
          {renderStepIndicator()}
          
          <div className="content-body">
            {currentStep === 1 && renderModelSelectionStep()}
            {currentStep === 2 && renderPromptSelectionStep()}
            {currentStep === 3 && renderTestUploadStep()}
            {currentStep === 4 && renderTestRunStep()}
          </div>

          <div className="step-actions">
            {currentStep > 1 && (
              <button onClick={handlePrevious} className="btn btn-secondary" disabled={isLoading}>
                Previous
              </button>
            )}
            
            {currentStep < 4 ? (
              <button 
                onClick={handleNext} 
                className="btn btn-primary"
                disabled={isLoading}
              >
                {isLoading ? "Loading..." : "Next"}
              </button>
            ) : (
              <button 
                onClick={handleFinish} 
                className="btn btn-primary"
                disabled={isLoading}
              >
                {isLoading ? "Running..." : "Run Test"}
              </button>
            )}
          </div>
        </div>
      </div>
    </div>
  );
}
