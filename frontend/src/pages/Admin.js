import { useEffect, useState } from "react";
import { useNavigate, Link } from "react-router-dom";
import axios from "axios";
import "../styles/Admin.css";

// Default prompt template for new prompts
const DEFAULT_PROMPT = `Question: {{question}}

Correct Answer: {{model_answer}}

Student's Answer: {{student_answer}}

Grade the student's answer based on the correct answer from (0.0 - 1.0). 
Provide a brief explanation for your grade.`;

// Predefined academic categories
const ACADEMIC_CATEGORIES = [
  "General",
  "Computer Science",
  "Mathematics",
  "English",
  "Physics",
  "Chemistry",
  "Biology",
  "History",
  "Geography",
  "Economics",
  "Psychology"
];

export default function Admin() {
  const [loading, setLoading] = useState(true);
  const [activeView, setActiveView] = useState("models");
  const [availableModels, setAvailableModels] = useState([]);
  const [modelName, setModelName] = useState("");
  const [isDownloading, setIsDownloading] = useState(false);
  const [downloadStatus, setDownloadStatus] = useState(null);
  const [username, setUsername] = useState("");
  const navigate = useNavigate();
  
  // URL query parameters to handle views
  const searchParams = new URLSearchParams(window.location.search);
  const urlView = searchParams.get('view');
  const urlTestId = searchParams.get('id');
  
  // Tests state
  const [tests, setTests] = useState([]);
  const [selectedTest, setSelectedTest] = useState(null);
  const [testPrompts, setTestPrompts] = useState({});
  const [viewingPrompt, setViewingPrompt] = useState(null);
  
  // Prompts state
  const [prompts, setPrompts] = useState([]);
  const [isPromptModalOpen, setIsPromptModalOpen] = useState(false);
  const [promptName, setPromptName] = useState("");
  const [promptCategory, setPromptCategory] = useState("Computer Science");
  const [promptText, setPromptText] = useState(DEFAULT_PROMPT);
  const [categories, setCategories] = useState(ACADEMIC_CATEGORIES);
  const [selectedCategory, setSelectedCategory] = useState("All");
  const [isEditing, setIsEditing] = useState(false);
  const [currentPromptId, setCurrentPromptId] = useState(null);
  const [error, setError] = useState(null);

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
        setUsername(decodedToken.sub);
        setLoading(false);
      } catch (err) {
        console.error("Failed to check admin status", err);
        navigate("/home");
      }
    };

    checkAdminStatus();
  }, [navigate]);

  // Set initial view from URL if present
  useEffect(() => {
    if (urlView && !loading) {
      setActiveView(urlView);
      if (urlView === "tests" && urlTestId) {
        fetchTestDetails(urlTestId);
      }
    }
  }, [urlView, urlTestId, loading]);

  // Auto-refresh for running tests
  useEffect(() => {
    let intervalId;
    
    if (selectedTest && selectedTest.status === "running") {
      // Set up polling when a running test is being viewed
      intervalId = setInterval(() => {
        refreshTestDetails(selectedTest.id);
      }, 5000); // Poll every 5 seconds
    }
    
    // Clean up interval when component unmounts or dependencies change
    return () => {
      if (intervalId) {
        clearInterval(intervalId);
      }
    };
  }, [selectedTest]);

  useEffect(() => {
    if (!loading) {
      if (activeView === "models") {
        fetchModels();
      } else if (activeView === "prompts") {
        fetchPrompts();
        fetchCategories();
      } else if (activeView === "tests") {
        fetchTests();
      }
    }
  }, [activeView, loading, selectedCategory]);

  const fetchTests = async () => {
    try {
      const response = await axios.get("/api/tests/");
      setTests(response.data);
    } catch (err) {
      console.error("Failed to fetch tests", err);
      setError("Failed to fetch tests");
    }
  };
  
  // Fetch complete test details including prompts
  const fetchTestDetails = async (testId) => {
    try {
      const response = await axios.get(`/api/tests/${testId}`);
      setSelectedTest(response.data);
      
      // Fetch prompt details for this test
      if (response.data.prompt_ids && response.data.prompt_ids.length > 0) {
        const promptsData = {};
        
        for (const promptId of response.data.prompt_ids) {
          try {
            const promptResponse = await axios.get(`/api/prompts/${promptId}`);
            promptsData[promptId] = promptResponse.data;
          } catch (promptErr) {
            console.error(`Failed to fetch prompt details for ID ${promptId}`, promptErr);
          }
        }
        
        setTestPrompts(promptsData);
      }
    } catch (err) {
      console.error(`Failed to fetch test details for ID ${testId}`, err);
      setError(`Failed to fetch test details: ${err.response?.data?.detail || err.message}`);
    }
  };
  
  // Refresh just the test data (used for polling)
  const refreshTestDetails = async (testId) => {
    try {
      const response = await axios.get(`/api/tests/${testId}`);
      
      // Only update if status has changed or results have been added/modified
      const currentResults = selectedTest.results ? selectedTest.results.length : 0;
      const newResults = response.data.results ? response.data.results.length : 0;
      
      if (response.data.status !== selectedTest.status || newResults !== currentResults) {
        console.log(`Test ${testId} updated: status=${response.data.status}, results=${newResults}`);
        setSelectedTest(response.data);
        
        // If we have new prompt IDs that weren't previously loaded, fetch their details
        if (response.data.prompt_ids) {
          const newPromptIds = response.data.prompt_ids.filter(id => !testPrompts[id]);
          
          if (newPromptIds.length > 0) {
            const updatedPrompts = {...testPrompts};
            
            for (const promptId of newPromptIds) {
              try {
                const promptResponse = await axios.get(`/api/prompts/${promptId}`);
                updatedPrompts[promptId] = promptResponse.data;
              } catch (promptErr) {
                console.error(`Failed to fetch prompt details for ID ${promptId}`, promptErr);
              }
            }
            
            setTestPrompts(updatedPrompts);
          }
        }
      }
    } catch (err) {
      console.error(`Failed to refresh test details for ID ${testId}`, err);
      // Don't show error to user during auto-refresh to avoid error spam
    }
  };
  
  const handleShowPrompt = (promptId) => {
    setViewingPrompt(testPrompts[promptId]);
  };
  
  const handleClosePromptModal = () => {
    setViewingPrompt(null);
  };

  const handleDeleteTest = async (id) => {
    if (!window.confirm("Are you sure you want to delete this test?")) return;
    
    try {
      await axios.delete(`/api/tests/${id}`);
      // Refresh tests list
      fetchTests();
      // Clear selected test if it was deleted
      if (selectedTest && selectedTest.id === id) {
        setSelectedTest(null);
      }
    } catch (err) {
      console.error("Failed to delete test", err);
      setError(`Failed to delete test: ${err.response?.data?.detail || err.message}`);
    }
  };

  const fetchModels = async () => {
    try {
      const response = await axios.get("/api/combinations/models");
      if (response.data && response.data.models) {
        setAvailableModels(response.data.models);
      }
    } catch (err) {
      console.error("Failed to fetch models", err);
      setError("Failed to fetch models");
    }
  };
  
  const fetchPrompts = async () => {
    try {
      const category = selectedCategory !== "All" ? selectedCategory : undefined;
      const response = await axios.get("/api/prompts/", {
        params: { category }
      });
      setPrompts(response.data);
    } catch (err) {
      console.error("Failed to fetch prompts", err);
      setError("Failed to fetch prompts");
    }
  };
  
  const fetchCategories = async () => {
    try {
      const response = await axios.get("/api/prompts/categories/all");
      if (response.data && response.data.categories) {
        // Combine predefined categories with any additional ones from the database
        const uniqueCategories = [...new Set([...ACADEMIC_CATEGORIES, ...response.data.categories])];
        setCategories(uniqueCategories);
      }
    } catch (err) {
      console.error("Failed to fetch categories", err);
      // Fall back to predefined categories
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
  
  const handleCreatePrompt = () => {
    setIsEditing(false);
    setCurrentPromptId(null);
    setPromptName("");
    setPromptCategory("Computer Science");
    setPromptText(DEFAULT_PROMPT);
    setIsPromptModalOpen(true);
  };
  
  const handleEditPrompt = (prompt) => {
    setIsEditing(true);
    setCurrentPromptId(prompt.id);
    setPromptName(prompt.name);
    setPromptCategory(prompt.category);
    setPromptText(prompt.prompt);
    setIsPromptModalOpen(true);
  };
  
  const handleDeletePrompt = async (id) => {
    if (!window.confirm("Are you sure you want to delete this prompt?")) return;
    
    try {
      await axios.delete(`/api/prompts/${id}`);
      // Refresh prompts list
      fetchPrompts();
    } catch (err) {
      console.error("Failed to delete prompt", err);
      setError(`Failed to delete prompt: ${err.response?.data?.detail || err.message}`);
    }
  };
  
  const handleSavePrompt = async () => {
    if (!promptName.trim() || !promptCategory.trim() || !promptText.trim()) {
      setError("Please complete all required fields");
      return;
    }
    
    try {
      const promptData = {
        name: promptName,
        category: promptCategory,
        prompt: promptText
      };
      
      if (isEditing) {
        await axios.put(`/api/prompts/${currentPromptId}`, promptData);
      } else {
        await axios.post("/api/prompts/", promptData);
      }
      
      // Reset form and close modal
      setIsPromptModalOpen(false);
      setPromptName("");
      setPromptCategory("Computer Science");
      setPromptText(DEFAULT_PROMPT);
      setIsEditing(false);
      setCurrentPromptId(null);
      
      // Refresh prompts list
      fetchPrompts();
    } catch (err) {
      console.error("Failed to save prompt", err);
      setError(`Failed to save prompt: ${err.response?.data?.detail || err.message}`);
    }
  };
  
  const handleCategoryChange = (category) => {
    setSelectedCategory(category);
    // No longer calling fetchPrompts() here as it will be triggered by the useEffect
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
        <li 
          className={activeView === "prompts" ? "active" : ""}
          onClick={() => setActiveView("prompts")}
        >
          Manage Prompts
        </li>
        <li 
          className={activeView === "tests" ? "active" : ""}
          onClick={() => setActiveView("tests")}
        >
          Test Results
        </li>
        <li>
          <Link to="/testing-wizard">Testing Wizard</Link>
        </li>
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
  
  const renderTestsView = () => {
    // If a test is selected, show its details
    if (selectedTest) {
      // Add refresh message for running tests
      const isRunning = selectedTest.status === "running";
      return (
        <div className="admin-content">
          <div className="test-header">
            <h2>Test Details: {selectedTest.name}</h2>
            <div className="test-header-actions">
              {isRunning && (
                <div className="auto-refresh-indicator">
                  <span className="refresh-dot"></span> Auto-refreshing...
                </div>
              )}
              <button 
                className="btn-secondary"
                onClick={() => setSelectedTest(null)}
              >
                Back to Tests
              </button>
            </div>
          </div>
          
          {selectedTest.description && (
            <p className="test-description">{selectedTest.description}</p>
          )}
          
          <div className="test-info">
            <p><strong>Status:</strong> <span className={`status-badge ${selectedTest.status}`}>{selectedTest.status}</span></p>
            <p><strong>Created:</strong> {new Date(selectedTest.created_at).toLocaleString()}</p>
            
            <div className="test-models-info">
              <h3>Models Used</h3>
              <ul>
                {selectedTest.model_names.map((modelName) => (
                  <li key={modelName}>{modelName}</li>
                ))}
              </ul>
            </div>
            
            <div className="test-prompts-info">
              <h3>Prompts Used</h3>
              <ul>
                {selectedTest.prompt_ids.map((promptId) => (
                  <li key={promptId} onClick={() => handleShowPrompt(promptId)} className="clickable-prompt">
                    {testPrompts[promptId]?.name || `Prompt ID: ${promptId}`}
                  </li>
                ))}
              </ul>
            </div>
          </div>
          
          {selectedTest.summaries && selectedTest.summaries.length > 0 ? (
            <div className="test-results-section">
              <h3>Test Results</h3>
              <div className="test-summaries">
                {selectedTest.summaries.map((summary) => (
                  <div key={`${summary.model_name}-${summary.prompt_id}`} className="summary-card">
                    <h4>{summary.model_name}</h4>
                    <p><strong>Average Accuracy:</strong> {(summary.average_accuracy * 100).toFixed(2)}%</p>
                    <p><strong>Average Response Time:</strong> {summary.average_response_time.toFixed(2)}s</p>
                    <p><strong>Questions Evaluated:</strong> {summary.total_questions}</p>
                    <p>
                      <strong>Prompt:</strong>{" "}
                      <span 
                        className="clickable-prompt"
                        onClick={() => handleShowPrompt(summary.prompt_id)}
                      >
                        {testPrompts[summary.prompt_id]?.name || `Prompt ID: ${summary.prompt_id}`}
                      </span>
                    </p>
                  </div>
                ))}
              </div>
              
              <h3>Detailed Results</h3>
              <div className="test-details-table">
                <table>
                  <thead>
                    <tr>
                      <th>Model</th>
                      <th>Prompt</th>
                      <th>Question</th>
                      <th>Model Grade</th>
                      <th>Extracted Grade</th>
                      <th>Accuracy</th>
                      <th>Response Time</th>
                    </tr>
                  </thead>
                  <tbody>
                    {selectedTest.results.map((result) => (
                      <tr key={result.id}>
                        <td>{result.model_name}</td>
                        <td>
                          <span 
                            className="clickable-prompt"
                            onClick={() => handleShowPrompt(result.prompt_id)}
                          >
                            {testPrompts[result.prompt_id]?.name || `Prompt ID: ${result.prompt_id}`}
                          </span>
                        </td>
                        <td className="question-cell">{result.question}</td>
                        <td>{result.model_grade.toFixed(2)}</td>
                        <td>{result.extracted_grade.toFixed(2)}</td>
                        <td>{(result.accuracy * 100).toFixed(2)}%</td>
                        <td>{result.response_time.toFixed(2)}s</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            </div>
          ) : (
            <div className="no-results">
              {selectedTest.status === "pending" ? (
                <p>This test is pending. Upload test questions to start processing.</p>
              ) : selectedTest.status === "running" ? (
                <p>Test is currently running. Results will appear here when complete.</p>
              ) : (
                <p>No results available for this test.</p>
              )}
            </div>
          )}
        </div>
      );
    }
    
    // Otherwise, show the list of tests
    return (
      <div className="admin-content">
        <div className="tests-header">
          <h2>Test Results</h2>
          <Link to="/testing-wizard" className="btn-primary">
            Create New Test
          </Link>
        </div>
        
        {tests.length > 0 ? (
          <div className="tests-list">
            {tests.map((test) => (
              <div key={test.id} className="test-card">
                <div className="test-card-header">
                  <h4>{test.name}</h4>
                  <div className="test-card-actions">
                    <button 
                      className="btn-primary btn-sm"
                      onClick={() => fetchTestDetails(test.id)}
                    >
                      View
                    </button>
                    <button 
                      className="btn-danger btn-sm"
                      onClick={() => handleDeleteTest(test.id)}
                    >
                      Delete
                    </button>
                  </div>
                </div>
                <div className="test-card-content">
                  {test.description && (
                    <p>{test.description}</p>
                  )}
                  <p><strong>Status:</strong> <span className={`status-badge ${test.status}`}>{test.status}</span></p>
                  <p><strong>Models:</strong> {test.model_names.join(", ")}</p>
                  <p><strong>Created:</strong> {new Date(test.created_at).toLocaleString()}</p>
                </div>
              </div>
            ))}
          </div>
        ) : (
          <p className="no-tests">No tests found. Use the Testing Wizard to create a new test.</p>
        )}
      </div>
    );
  };

  const renderPromptsView = () => (
    <div className="admin-content">
      <h2>Manage Prompts</h2>
      
      <div className="prompts-actions">
        <button 
          className="btn-primary"
          onClick={handleCreatePrompt}
        >
          Create New Prompt
        </button>
        
        <div className="category-filter">
          <label htmlFor="category-filter">Filter by Category:</label>
          <select 
            id="category-filter"
            value={selectedCategory}
            onChange={(e) => handleCategoryChange(e.target.value)}
          >
            <option value="All">All Categories</option>
            {categories.map(category => (
              <option key={category} value={category}>{category}</option>
            ))}
          </select>
        </div>
      </div>
      
      <div className="prompt-list">
        {prompts.length > 0 ? (
          <div className="prompt-cards">
            {prompts.map((prompt) => (
              <div key={prompt.id} className="prompt-card">
                <div className="prompt-card-header">
                  <h4>{prompt.name}</h4>
                  <div className="prompt-card-actions">
                    <button 
                      className="btn-secondary btn-sm"
                      onClick={() => handleEditPrompt(prompt)}
                    >
                      Edit
                    </button>
                    <button 
                      className="btn-danger btn-sm"
                      onClick={() => handleDeletePrompt(prompt.id)}
                    >
                      Delete
                    </button>
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
        ) : (
          <p className="no-prompts">No prompts found. Create a new prompt to get started.</p>
        )}
      </div>
      
      {/* Prompt Modal */}
      {isPromptModalOpen && (
        <div className="modal">
          <div className="modal-content">
            <div className="modal-header">
              <h3>{isEditing ? "Edit Prompt" : "Create New Prompt"}</h3>
              <button className="close-button" onClick={() => setIsPromptModalOpen(false)}>×</button>
            </div>
            
            <div className="modal-body">
              <div className="form-group">
                <label htmlFor="prompt-name">Name *</label>
                <input 
                  type="text"
                  id="prompt-name"
                  value={promptName}
                  onChange={(e) => setPromptName(e.target.value)}
                  placeholder="Enter a name for this prompt"
                  className="form-control"
                  required
                />
              </div>
              
              <div className="form-group">
                <label htmlFor="prompt-category">Category *</label>
                <select
                  id="prompt-category"
                  value={promptCategory}
                  onChange={(e) => setPromptCategory(e.target.value)}
                  className="form-control"
                  required
                >
                  {categories.map(category => (
                    <option key={category} value={category}>{category}</option>
                  ))}
                </select>
              </div>
              
              <div className="form-group">
                <label htmlFor="prompt-text">Prompt *</label>
                <textarea
                  id="prompt-text"
                  value={promptText}
                  onChange={(e) => setPromptText(e.target.value)}
                  className="prompt-textarea"
                  placeholder="Enter the prompt text..."
                  required
                />
              </div>
            </div>
            
            <div className="modal-footer">
              <button 
                className="btn-secondary"
                onClick={() => setIsPromptModalOpen(false)}
              >
                Cancel
              </button>
              <button 
                className="btn-primary"
                onClick={handleSavePrompt}
              >
                Save
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );

  if (loading) {
    return <div className="admin-loading">Loading...</div>;
  }

  return (
    <div className="admin-container">
      {/* Prompt Viewing Modal - shown when clicking on a prompt name */}
      {viewingPrompt && (
        <div className="modal">
          <div className="modal-content">
            <div className="modal-header">
              <h3>Prompt: {viewingPrompt.name}</h3>
              <button className="close-button" onClick={handleClosePromptModal}>×</button>
            </div>
            <div className="modal-body">
              <div className="form-group">
                <label><strong>Category:</strong> {viewingPrompt.category}</label>
              </div>
              <div className="form-group">
                <label><strong>Prompt Text:</strong></label>
                <pre className="prompt-preview">{viewingPrompt.prompt}</pre>
              </div>
            </div>
          </div>
        </div>
      )}
      <div className="taskbar">
        <div className="taskbar-left">
          <Link to="/home">Home</Link>
          <Link to="/pairs">Pairs</Link>
          <Link to="/admin">Admin</Link>
        </div>
        <div className="taskbar-right">
          <div className="user-profile">
            <span className="user-icon"></span>
            <div className="username-tooltip">{username}</div>
          </div>
        </div>
      </div>

      <div className="admin-body">
        {renderSidebar()}
        
        <div className="main-content">
          {error && (
            <div className="error-message">
              {error}
              <button onClick={() => setError(null)}>✕</button>
            </div>
          )}
          
          {activeView === "models" && renderModelsView()}
          {activeView === "prompts" && renderPromptsView()}
          {activeView === "tests" && renderTestsView()}
        </div>
      </div>
    </div>
  );
}
