import { useState, useEffect } from "react";
import { useNavigate, Link } from "react-router-dom";
import api, { handleApiError } from "../utils/api";
import "../styles/Admin.css";

export default function Admin() {
  // State for prompts
  const [prompts, setPrompts] = useState([]);
  const [activePrompt, setActivePrompt] = useState(null);
  const [newPrompt, setNewPrompt] = useState({ name: "", description: "", template: "" });
  
  // State for models
  const [models, setModels] = useState([]);
  const [availableModels, setAvailableModels] = useState([]);
  const [activeModel, setActiveModel] = useState(null);
  const [modelParameters, setModelParameters] = useState({
    temperature: 0.7,
    top_p: 0.9,
    top_k: 40
  });
  
  // State for combinations
  const [combinations, setCombinations] = useState([]);
  const [activeCombination, setActiveCombination] = useState(null);
  
  // State for evaluation
  const [evaluationQuestions, setEvaluationQuestions] = useState([]);
  const [selectedQuestions, setSelectedQuestions] = useState([]);
  const [evaluationResults, setEvaluationResults] = useState(null);
  const [csvQuestions, setCsvQuestions] = useState([]);
  const [isUsingCsv, setIsUsingCsv] = useState(false);
  const [csvFile, setCsvFile] = useState(null);
  const [csvFileName, setCsvFileName] = useState("");
  const [isUploadingCsv, setIsUploadingCsv] = useState(false);
  
  // UI state
  const [activeTab, setActiveTab] = useState("prompt");
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState(null);
  const [successMessage, setSuccessMessage] = useState(null);
  
  const navigate = useNavigate();

  // Load data on component mount
  useEffect(() => {
    fetchPrompts();
    fetchModels();
    fetchCombinations();
    fetchQuestions();
  }, []);

  // Fetch functions
  const fetchPrompts = async () => {
    try {
      const response = await api.get('/prompts/');
      setPrompts(response.data);
      
      // Get active prompt
      try {
        const activePromptResponse = await api.get('/prompts/active');
        setActivePrompt(activePromptResponse.data);
      } catch (err) {
        // It's okay if no active prompt exists
        console.log("No active prompt found");
      }
    } catch (err) {
      console.error("Error fetching prompts:", err);
      setError(handleApiError(err));
    }
  };

  const fetchModels = async () => {
    try {
      // Get models from database
      const response = await api.get('/models/');
      setModels(response.data);
      
      // Get active model
      try {
        const activeModelResponse = await api.get('/models/active');
        setActiveModel(activeModelResponse.data);
      } catch (err) {
        // It's okay if no active model exists
        console.log("No active model found");
      }
      
      // Get available models from Ollama
      const availableResponse = await api.get('/models/available');
      setAvailableModels(availableResponse.data.models);
    } catch (err) {
      console.error("Error fetching models:", err);
      setError(handleApiError(err));
    }
  };

  const fetchCombinations = async () => {
    try {
      const response = await api.get('/evaluations/combinations');
      setCombinations(response.data);
      
      // Get active combination
      try {
        const activeCombResponse = await api.get('/evaluations/combinations/active');
        setActiveCombination(activeCombResponse.data);
      } catch (err) {
        // It's okay if no active combination exists
        console.log("No active combination found");
      }
    } catch (err) {
      console.error("Error fetching combinations:", err);
      setError(handleApiError(err));
    }
  };

  const fetchQuestions = async () => {
    try {
      // Get a sample of questions for evaluation
      // Using a different endpoint as the questions/ endpoint might not support GET
      const response = await api.get('/collections/1/questions'); // Assuming collection 1 exists
      setEvaluationQuestions(response.data.slice(0, 10)); // Limit to first 10 questions
    } catch (err) {
      console.error("Error fetching questions:", err);
      // Don't set error here as it's not critical
    }
  };
  
  // CSV handling functions
  const handleCsvFileChange = (event) => {
    const file = event.target.files[0];
    if (file) {
      setCsvFile(file);
      setCsvFileName(file.name);
    }
  };
  
  const handleCsvUpload = async () => {
    if (!csvFile) {
      setError("Please select a CSV file first");
      return;
    }
    
    setIsUploadingCsv(true);
    try {
      // Create a FormData object to send the file
      const formData = new FormData();
      formData.append("file", csvFile);
      
      // Make the API request
      const response = await api.post('/csv-evaluation/upload', formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });
      
      // Update state with the parsed questions
      setCsvQuestions(response.data.questions);
      setIsUsingCsv(true);
      
      // Clear selected questions when switching to CSV
      setSelectedQuestions([]);
      
      setSuccessMessage(`CSV file "${response.data.filename}" uploaded with ${response.data.count} questions`);
    } catch (err) {
      console.error("Error uploading CSV:", err);
      setError(handleApiError(err));
    } finally {
      setIsUploadingCsv(false);
    }
  };
  
  const handleBackToDbQuestions = () => {
    setIsUsingCsv(false);
    setSelectedQuestions([]);
    setCsvQuestions([]);
    setCsvFile(null);
    setCsvFileName("");
  };

  // Prompt management functions
  const handleCreatePrompt = async () => {
    try {
      setIsLoading(true);
      const response = await api.post('/prompts/', newPrompt);
      setPrompts([...prompts, response.data]);
      setNewPrompt({ name: "", description: "", template: "" });
      setSuccessMessage("Prompt created successfully!");
    } catch (err) {
      console.error("Error creating prompt:", err);
      setError(handleApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  const handleActivatePrompt = async (promptId) => {
    try {
      setIsLoading(true);
      const response = await api.put(`/prompts/${promptId}/activate`);
      setActivePrompt(response.data);
      
      // Update prompts list to reflect the change
      setPrompts(prompts.map(p => ({
        ...p,
        is_active: p.id === promptId
      })));
      
      setSuccessMessage("Prompt activated successfully!");
    } catch (err) {
      console.error("Error activating prompt:", err);
      setError(handleApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  // Model management functions
  const handlePullModel = async (modelName) => {
    try {
      setIsLoading(true);
      await api.post('/models/pull', { model_name: modelName });
      setSuccessMessage(`Model ${modelName} download started in the background.`);
      
      // Add a delay to make it more likely the model appears in the list
      setTimeout(() => {
        fetchModels();
      }, 5000);
    } catch (err) {
      console.error("Error pulling model:", err);
      setError(handleApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  const handleCreateModel = async (modelName) => {
    try {
      setIsLoading(true);
      const modelData = {
        name: modelName,
        description: `Model ${modelName}`,
        parameters: modelParameters
      };
      
      const response = await api.post('/models/', modelData);
      setModels([...models, response.data]);
      setSuccessMessage("Model added to database successfully!");
    } catch (err) {
      console.error("Error creating model:", err);
      setError(handleApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  const handleActivateModel = async (modelId) => {
    try {
      setIsLoading(true);
      const response = await api.put(`/models/${modelId}/activate`);
      setActiveModel(response.data);
      
      // Update models list to reflect the change
      setModels(models.map(m => ({
        ...m,
        is_active: m.id === modelId
      })));
      
      setSuccessMessage("Model activated successfully!");
    } catch (err) {
      console.error("Error activating model:", err);
      setError(handleApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  const handleUpdateModelParameters = async () => {
    if (!activeModel) {
      setError("No active model selected");
      return;
    }
    
    try {
      setIsLoading(true);
      await api.post(`/models/${activeModel.id}/update-parameters`, modelParameters);
      setSuccessMessage("Model parameters updated successfully!");
      fetchModels(); // Refresh model data
    } catch (err) {
      console.error("Error updating model parameters:", err);
      setError(handleApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  // Combination management functions
  const handleCreateCombination = async () => {
    if (!activePrompt || !activeModel) {
      setError("Both a prompt and a model must be selected");
      return;
    }
    
    try {
      setIsLoading(true);
      const combinationData = {
        prompt_id: activePrompt.id,
        model_id: activeModel.id,
        name: `${activeModel.name} with ${activePrompt.name}`,
        description: "Created from Admin panel",
        parameters: modelParameters
      };
      
      const response = await api.post('/evaluations/combinations', combinationData);
      setCombinations([...combinations, response.data]);
      setSuccessMessage("Combination created successfully!");
    } catch (err) {
      console.error("Error creating combination:", err);
      setError(handleApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  const handleActivateCombination = async (combinationId) => {
    try {
      setIsLoading(true);
      const response = await api.put(`/evaluations/combinations/${combinationId}/activate`);
      setActiveCombination(response.data);
      
      // Update combinations list to reflect the change
      setCombinations(combinations.map(c => ({
        ...c,
        is_active: c.id === combinationId
      })));
      
      // Also update the active model and prompt
      fetchModels();
      fetchPrompts();
      
      setSuccessMessage("Combination activated successfully!");
    } catch (err) {
      console.error("Error activating combination:", err);
      setError(handleApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  // Evaluation functions
  const handleToggleQuestionSelection = (questionId) => {
    if (selectedQuestions.includes(questionId)) {
      setSelectedQuestions(selectedQuestions.filter(id => id !== questionId));
    } else {
      setSelectedQuestions([...selectedQuestions, questionId]);
    }
  };

  const handleEvaluate = async () => {
    if (selectedQuestions.length === 0) {
      setError("Please select at least one question to evaluate");
      return;
    }
    
    if (!activePrompt && !activeModel && !activeCombination) {
      setError("Please select a prompt and model, or an active combination");
      return;
    }
    
    try {
      setIsLoading(true);
      
      let requestData;
      
      if (isUsingCsv) {
        // For CSV questions, we need to include the full question data
        const selectedCsvQuestions = csvQuestions.filter(q => selectedQuestions.includes(q.id));
        
        requestData = {
          csv_questions: selectedCsvQuestions,
          parameters: modelParameters,
          save_result: true,
          is_csv: true
        };
      } else {
        // For database questions, just include the IDs
        requestData = {
          question_ids: selectedQuestions,
          parameters: modelParameters,
          save_result: true
        };
      }
      
      if (activeCombination) {
        requestData.prompt_id = activeCombination.prompt_id;
        requestData.model_id = activeCombination.model_id;
        requestData.combination_name = `Evaluation of ${activeCombination.name}`;
      } else {
        requestData.prompt_id = activePrompt?.id;
        requestData.model_id = activeModel?.id;
        requestData.combination_name = activePrompt && activeModel ? 
          `${activeModel.name} with ${activePrompt.name}` : undefined;
      }
      
      const response = await api.post('/evaluations/evaluate', requestData);
      setEvaluationResults(response.data);
      fetchCombinations(); // Refresh combinations after evaluation
      
      setSuccessMessage("Evaluation completed successfully!");
    } catch (err) {
      console.error("Error during evaluation:", err);
      setError(handleApiError(err));
    } finally {
      setIsLoading(false);
    }
  };

  // Helper functions
  const clearMessages = () => {
    setError(null);
    setSuccessMessage(null);
  };

  // Render functions for each tab
  const renderPromptTab = () => (
    <div className="tab-content">
      <h3>Current Active Prompt</h3>
      {activePrompt ? (
        <div className="active-prompt">
          <h4>{activePrompt.name}</h4>
          <p>{activePrompt.description}</p>
          <div className="prompt-template">
            <h5>Template:</h5>
            <pre>{activePrompt.template}</pre>
          </div>
        </div>
      ) : (
        <p>No active prompt selected</p>
      )}

      <h3>Available Prompts</h3>
      <div className="prompts-list">
        {prompts.map(prompt => (
          <div key={prompt.id} className={`prompt-item ${prompt.is_active ? 'active' : ''}`}>
            <h4>{prompt.name}</h4>
            <p>{prompt.description}</p>
            <button 
              onClick={() => handleActivatePrompt(prompt.id)}
              disabled={prompt.is_active}
            >
              {prompt.is_active ? 'Active' : 'Activate'}
            </button>
          </div>
        ))}
      </div>

      <h3>Create New Prompt</h3>
      <div className="create-prompt">
        <input
          type="text"
          placeholder="Prompt Name"
          value={newPrompt.name}
          onChange={(e) => setNewPrompt({...newPrompt, name: e.target.value})}
        />
        <input
          type="text"
          placeholder="Description"
          value={newPrompt.description}
          onChange={(e) => setNewPrompt({...newPrompt, description: e.target.value})}
        />
        <textarea
          placeholder="Prompt Template"
          value={newPrompt.template}
          onChange={(e) => setNewPrompt({...newPrompt, template: e.target.value})}
          rows={10}
        />
        <button onClick={handleCreatePrompt} disabled={isLoading}>
          {isLoading ? 'Creating...' : 'Create Prompt'}
        </button>
      </div>
    </div>
  );

  const renderModelTab = () => (
    <div className="tab-content">
      <h3>Current Active Model</h3>
      {activeModel ? (
        <div className="active-model">
          <h4>{activeModel.name}</h4>
          <p>{activeModel.description}</p>
          <div className="model-parameters">
            <h5>Parameters:</h5>
            <pre>{JSON.stringify(activeModel.parameters, null, 2)}</pre>
          </div>
        </div>
      ) : (
        <p>No active model selected</p>
      )}

      <h3>Model Parameters</h3>
      <div className="model-parameters-editor">
        <div className="parameter">
          <label>Temperature:</label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={modelParameters.temperature}
            onChange={(e) => setModelParameters({...modelParameters, temperature: parseFloat(e.target.value)})}
          />
          <span>{modelParameters.temperature}</span>
        </div>
        <div className="parameter">
          <label>Top P:</label>
          <input
            type="range"
            min="0"
            max="1"
            step="0.1"
            value={modelParameters.top_p}
            onChange={(e) => setModelParameters({...modelParameters, top_p: parseFloat(e.target.value)})}
          />
          <span>{modelParameters.top_p}</span>
        </div>
        <div className="parameter">
          <label>Top K:</label>
          <input
            type="range"
            min="0"
            max="100"
            step="1"
            value={modelParameters.top_k}
            onChange={(e) => setModelParameters({...modelParameters, top_k: parseInt(e.target.value)})}
          />
          <span>{modelParameters.top_k}</span>
        </div>
        <button onClick={handleUpdateModelParameters} disabled={isLoading || !activeModel}>
          {isLoading ? 'Updating...' : 'Update Parameters'}
        </button>
      </div>

      <h3>Models in Database</h3>
      <div className="models-list">
        {models.map(model => (
          <div key={model.id} className={`model-item ${model.is_active ? 'active' : ''}`}>
            <h4>{model.name}</h4>
            <p>{model.description}</p>
            <button 
              onClick={() => handleActivateModel(model.id)}
              disabled={model.is_active}
            >
              {model.is_active ? 'Active' : 'Activate'}
            </button>
          </div>
        ))}
      </div>

      <h3>Available Models in Ollama</h3>
      <div className="available-models">
        {availableModels.map(model => (
          <div key={model.name} className="available-model-item">
            <h4>{model.name}</h4>
            <p>Size: {(model.size / (1024 * 1024 * 1024)).toFixed(2)} GB</p>
            <p>Modified: {new Date(model.modified_at).toLocaleDateString()}</p>
            <div className="action-buttons">
              <button onClick={() => handleCreateModel(model.name)}>
                Add to Database
              </button>
            </div>
          </div>
        ))}
      </div>

      <h3>Pull a New Model</h3>
      <div className="pull-model">
        <input
          type="text"
          placeholder="Model name (e.g., llama3:8b)"
          id="modelNameInput"
        />
        <button 
          onClick={() => {
            const modelName = document.getElementById('modelNameInput').value;
            if (modelName) handlePullModel(modelName);
          }} 
          disabled={isLoading}
        >
          {isLoading ? 'Pulling...' : 'Pull Model'}
        </button>
      </div>
    </div>
  );

  const renderCombinationTab = () => (
    <div className="tab-content">
      <h3>Current Active Combination</h3>
      {activeCombination ? (
        <div className="active-combination">
          <h4>{activeCombination.name}</h4>
          <p>Model: {activeCombination.model_name}</p>
          <p>Prompt: {activeCombination.prompt_template ? activeCombination.prompt_template.substring(0, 100) + "..." : "N/A"}</p>
          <div className="combination-metrics">
            <h5>Performance Metrics:</h5>
            <p>Average Accuracy: {activeCombination.average_accuracy?.toFixed(3) || "N/A"}</p>
            <p>Average Response Time: {activeCombination.average_response_time?.toFixed(2) || "N/A"}s</p>
            <p>Consistency Score: {activeCombination.consistency_score?.toFixed(3) || "N/A"}</p>
          </div>
        </div>
      ) : (
        <p>No active combination selected</p>
      )}

      <h3>Create New Combination</h3>
      <div className="create-combination">
        <p>Current Active Prompt: {activePrompt ? activePrompt.name : "None"}</p>
        <p>Current Active Model: {activeModel ? activeModel.name : "None"}</p>
        <button 
          onClick={handleCreateCombination} 
          disabled={isLoading || !activePrompt || !activeModel}
        >
          {isLoading ? 'Creating...' : 'Create Combination with Active Prompt and Model'}
        </button>
      </div>

      <h3>Saved Combinations</h3>
      <div className="combinations-list">
        {combinations.map(combination => (
          <div key={combination.id} className={`combination-item ${combination.is_active ? 'active' : ''}`}>
            <h4>{combination.name}</h4>
            <p>Model: {combination.model_name}</p>
            <div className="metrics">
              {combination.average_accuracy && (
                <p>Accuracy: {combination.average_accuracy.toFixed(3)}</p>
              )}
              {combination.average_response_time && (
                <p>Resp. Time: {combination.average_response_time.toFixed(2)}s</p>
              )}
            </div>
            <button 
              onClick={() => handleActivateCombination(combination.id)}
              disabled={combination.is_active}
            >
              {combination.is_active ? 'Active' : 'Activate'}
            </button>
          </div>
        ))}
      </div>
    </div>
  );

  const renderEvaluationTab = () => (
    <div className="tab-content">
      <h3>Evaluation</h3>
      <div className="evaluation-config">
        <p>Active Prompt: {activePrompt ? activePrompt.name : "None"}</p>
        <p>Active Model: {activeModel ? activeModel.name : "None"}</p>
        <p>Active Combination: {activeCombination ? activeCombination.name : "None"}</p>
        
        {/* CSV file upload section */}
        <div className="csv-upload-section">
          <h4>Upload Questions from CSV</h4>
          <p className="instruction">
            Upload a CSV file with columns for:
            <ul>
              <li>Question</li>
              <li>Model Answer (or ModelAnswer)</li>
              <li>Student Answer (or StudentAnswer)</li>
              <li>Model Grade (optional)</li>
            </ul>
          </p>
          
          <div className="file-input-container">
            <input 
              type="file" 
              id="csv-file-input" 
              accept=".csv" 
              onChange={handleCsvFileChange}
              className="file-input"
            />
            <label htmlFor="csv-file-input" className="file-input-label">
              {csvFileName || "Choose CSV File"}
            </label>
            <button 
              onClick={handleCsvUpload}
              disabled={isUploadingCsv || !csvFile}
              className="upload-button"
            >
              {isUploadingCsv ? 'Uploading...' : 'Upload'}
            </button>
          </div>
        </div>
        
        <h4>
          {isUsingCsv ? (
            <div className="questions-source-header">
              <span>Questions from CSV: {csvFileName}</span>
              <button 
                onClick={handleBackToDbQuestions}
                className="switch-source-button"
              >
                Switch to Database Questions
              </button>
            </div>
          ) : "Select Questions to Evaluate"}
        </h4>
        
        <div className="question-selector">
          {isUsingCsv ? (
            // Display CSV questions
            csvQuestions.map(question => (
              <div key={question.id} className="question-item">
                <input
                  type="checkbox"
                  id={`csv-question-${question.id}`}
                  checked={selectedQuestions.includes(question.id)}
                  onChange={() => handleToggleQuestionSelection(question.id)}
                />
                <label htmlFor={`csv-question-${question.id}`}>
                  <strong>Q:</strong> {question.text.substring(0, 80)}...
                  <div className="student-answer">
                    <strong>Student Answer:</strong> {question.student_answer.substring(0, 60)}...
                  </div>
                </label>
              </div>
            ))
          ) : (
            // Display database questions
            evaluationQuestions.map(question => (
              <div key={question.id} className="question-item">
                <input
                  type="checkbox"
                  id={`question-${question.id}`}
                  checked={selectedQuestions.includes(question.id)}
                  onChange={() => handleToggleQuestionSelection(question.id)}
                />
                <label htmlFor={`question-${question.id}`}>
                  {question.text.substring(0, 100)}...
                </label>
              </div>
            ))
          )}
        </div>
        
        <button 
          onClick={handleEvaluate} 
          disabled={isLoading || selectedQuestions.length === 0}
          className="evaluate-button"
        >
          {isLoading ? 'Evaluating...' : 'Run Evaluation'}
        </button>
      </div>

      {evaluationResults && (
        <div className="evaluation-results">
          <h3>Evaluation Results</h3>
          <div className="result-summary">
            <h4>Model: {evaluationResults.model_name}</h4>
            <div className="metrics">
              <p>Total Questions: {evaluationResults.metrics.total_questions}</p>
              <p>Successful Evaluations: {evaluationResults.metrics.successful_evaluations}</p>
              {evaluationResults.metrics.average_accuracy && (
                <p>Average Accuracy: {evaluationResults.metrics.average_accuracy.toFixed(3)}</p>
              )}
              <p>Average Response Time: {evaluationResults.metrics.average_response_time.toFixed(2)}s</p>
            </div>
          </div>
          
          <h4>Detailed Results</h4>
          <div className="results-list">
            {evaluationResults.evaluations.map((result, index) => (
              <div key={index} className="result-item">
                {result.error ? (
                  <div className="error-result">
                    <h5>Error on Question {result.question_id || index + 1}</h5>
                    <p>{result.error_message}</p>
                  </div>
                ) : (
                  <div className="success-result">
                    <h5>Question {result.question_id || index + 1}</h5>
                    <p>Extracted Grade: {result.extracted_grade?.toFixed(2) || "N/A"}</p>
                    <p>Confidence: {result.confidence || "N/A"}</p>
                    {result.accuracy !== undefined && (
                      <p>Accuracy: {result.accuracy.toFixed(3)}</p>
                    )}
                    <p>Response Time: {result.response_time?.toFixed(2) || "N/A"}s</p>
                    <div className="response-text">
                      <h6>Model Response:</h6>
                      <pre>{result.response}</pre>
                    </div>
                  </div>
                )}
              </div>
            ))}
          </div>
        </div>
      )}
    </div>
  );

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

      {(error || successMessage) && (
        <div className={`message-container ${error ? 'error' : 'success'}`}>
          <p>{error || successMessage}</p>
          <button onClick={clearMessages}>✕</button>
        </div>
      )}

      <div className="content-box">
        <h2>Admin Panel</h2>
        
        <div className="tabs">
          <button 
            className={activeTab === "prompt" ? "active" : ""} 
            onClick={() => setActiveTab("prompt")}
          >
            Prompts
          </button>
          <button 
            className={activeTab === "model" ? "active" : ""} 
            onClick={() => setActiveTab("model")}
          >
            Models
          </button>
          <button 
            className={activeTab === "combination" ? "active" : ""} 
            onClick={() => setActiveTab("combination")}
          >
            Combinations
          </button>
          <button 
            className={activeTab === "evaluation" ? "active" : ""} 
            onClick={() => setActiveTab("evaluation")}
          >
            Evaluation
          </button>
        </div>
        
        {activeTab === "prompt" && renderPromptTab()}
        {activeTab === "model" && renderModelTab()}
        {activeTab === "combination" && renderCombinationTab()}
        {activeTab === "evaluation" && renderEvaluationTab()}
      </div>
    </div>
  );
}
