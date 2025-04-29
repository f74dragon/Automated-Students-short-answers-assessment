import { useEffect, useState, useRef } from "react";
import { useParams, useNavigate } from "react-router-dom";
import axios from "axios";
import "../styles/CollectionDetails.css";

export default function CollectionDetails() {
  const { id } = useParams();
  const navigate = useNavigate();
  const [collection, setCollection] = useState(null);
  const [combination, setCombination] = useState(null);  // For storing the collection's combination
  const [questions, setQuestions] = useState([]);
  const [students, setStudents] = useState([]);
  const [studentAnswers, setStudentAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [showAddQuestionModal, setShowAddQuestionModal] = useState(false);
  const [showAddStudentModal, setShowAddStudentModal] = useState(false);
  const [showAddAnswerModal, setShowAddAnswerModal] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [selectedQuestion, setSelectedQuestion] = useState(null);
  const [newQuestion, setNewQuestion] = useState({ text: "", model_answer: "" });
  const [newStudent, setNewStudent] = useState({ name: "", pid: "" });
  const [newAnswer, setNewAnswer] = useState({ answer: "" });
  const [answerError, setAnswerError] = useState("");
  const [grades, setGrades] = useState({});
  const [gradingInProgress, setGradingInProgress] = useState({});
  const [showUploadQuestionsModal, setShowUploadQuestionsModal] = useState(false);
  const [showUploadAnswersModal, setShowUploadAnswersModal] = useState(false);
  const [questionsFile, setQuestionsFile] = useState(null);
  const [answersFile, setAnswersFile] = useState(null);
  const [uploadStatus, setUploadStatus] = useState(null);
  const [openStudentId, setOpenStudentId] = useState(null); // State for student dropdown
  const [isGradingAll, setIsGradingAll] = useState(false); // State for Grade All button
  
  // Model download progress tracking
  const [isDownloadingModel, setIsDownloadingModel] = useState(false);
  const [downloadProgress, setDownloadProgress] = useState(null);
  const [downloadStatus, setDownloadStatus] = useState(null);
  const downloadAbortController = useRef(null);

  // Fetch collection details, questions, and students when component mounts
  useEffect(() => {
    const fetchData = async () => {
      try {
        const token = localStorage.getItem("token");
        if (!token) return navigate("/");

        // Get the user ID from the token
        const decodedToken = JSON.parse(atob(token.split(".")[1]));
        const username = decodedToken.sub;
        const userRes = await axios.get(`/api/users/`);
        const user = userRes.data.users.find(u => u.username === username);
        if (!user) throw new Error("User not found");

        // Get collection
        const collectionRes = await axios.get(`/api/collections/${user.id}/${id}`);
        setCollection(collectionRes.data);

        // If collection has a combination_id, fetch the combination details
        if (collectionRes.data.combination_id) {
          try {
            const combinationRes = await axios.get(`/api/combinations/${collectionRes.data.combination_id}`);
            setCombination(combinationRes.data);
          } catch (err) {
            console.error("Failed to fetch combination details", err);
          }
        }

        // Get questions for this collection
        const questionsRes = await axios.get(`/api/questions/collection/${id}`);
        setQuestions(questionsRes.data.questions);

        // Get students for this collection
        const studentsRes = await axios.get(`/api/students/collection/${id}`);
        const fetchedStudents = studentsRes.data.students;
        setStudents(fetchedStudents);

        // Fetch student answers and grades using the newly fetched students
        await fetchStudentAnswersAndGrades(fetchedStudents);

        setLoading(false);
      } catch (err) {
        console.error("Failed to fetch collection details", err);
        setError("Failed to load collection details");
        setLoading(false);
      }
    };

    fetchData();
  }, [id, navigate]); // Removed fetchStudentAnswersAndGrades from dependency array as it now takes args

  // Fetch student answers and grades for a given list of students
  const fetchStudentAnswersAndGrades = async (studentsList) => {
    if (!studentsList || studentsList.length === 0) {
      setStudentAnswers({}); // Clear answers if no students
      return;
    }
    try {
      const answers = {};
      const gradeData = {};

      // For each student and question, fetch answers
      for (const student of studentsList) {
        const studentAnswersRes = await axios.get(`/api/student-answers/student/${student.id}`);
        const studentAnswersList = studentAnswersRes.data.student_answers || [];

        // Group answers by question
        studentAnswersList.forEach(answer => {
          if (!answers[student.id]) {
            answers[student.id] = {};
          }
          answers[student.id][answer.question_id] = answer;

          // Try to fetch grade for this answer
          fetchGradeForAnswer(answer.id).then(grade => {
            if (grade) {
              setGrades(prev => ({
                ...prev,
                [answer.id]: grade
              }));
            }
          });
        });
      }

      setStudentAnswers(answers);
    } catch (err) {
      console.error("Failed to fetch student answers", err);
    }
  };

  // Fetch grade for a specific answer
  const fetchGradeForAnswer = async (answerID) => {
    try {
      const gradeRes = await axios.get(`/api/student-answers/${answerID}/grades`);
      return gradeRes.data;
    } catch (err) {
      // If no grade exists yet, that's okay - just return null
      return null;
    }
  };

  // Add a new question to the collection
  const handleAddQuestion = async () => {
    try {
      await axios.post("/api/questions/", {
        ...newQuestion,
        collection_id: parseInt(id)
      });
      
      // Refresh questions
      const questionsRes = await axios.get(`/api/questions/collection/${id}`);
      setQuestions(questionsRes.data.questions);
      
      // Reset form and close modal
      setNewQuestion({ text: "", model_answer: "" });
      setShowAddQuestionModal(false);
    } catch (err) {
      console.error("Failed to add question", err);
    }
  };

  // Add a new student to the collection
  const handleAddStudent = async () => {
    try {
      await axios.post("/api/students/", {
        ...newStudent,
        collection_id: parseInt(id)
      });
      
      // Refresh students
      const studentsRes = await axios.get(`/api/students/collection/${id}`);
      setStudents(studentsRes.data.students);
      
      // Reset form and close modal
      setNewStudent({ name: "", pid: "" });
      setShowAddStudentModal(false);
    } catch (err) {
      console.error("Failed to add student", err);
    }
  };
  
  // Upload questions CSV
  const handleUploadQuestions = async () => {
    try {
      if (!questionsFile) {
        return;
      }
      
      setUploadStatus({
        message: "Uploading questions...",
        error: false
      });
      
      const formData = new FormData();
      formData.append('file', questionsFile);
      
      const response = await axios.post(
        `/api/collections/${id}/upload-questions`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      
      // Refresh questions
      const questionsRes = await axios.get(`/api/questions/collection/${id}`);
      setQuestions(questionsRes.data.questions);
      
      setUploadStatus({
        message: "Questions uploaded successfully!",
        error: false,
        details: response.data
      });
      
      // Auto-close after 3 seconds on success
      setTimeout(() => {
        if (questionsFile) {  // Only close if we're still showing this modal
          setShowUploadQuestionsModal(false);
          setUploadStatus(null);
          setQuestionsFile(null);
        }
      }, 3000);
      
    } catch (err) {
      console.error("Failed to upload questions CSV", err);
      setUploadStatus({
        message: "Failed to upload questions: " + (err.response?.data?.detail || err.message),
        error: true,
        details: err.response?.data
      });
    }
  };
  
  // Upload answers CSV
  const handleUploadAnswers = async () => {
    try {
      if (!answersFile) {
        return;
      }
      
      setUploadStatus({
        message: "Uploading answers...",
        error: false
      });
      
      const formData = new FormData();
      formData.append('file', answersFile);
      
      const response = await axios.post(
        `/api/collections/${id}/upload-answers`,
        formData,
        {
          headers: {
            'Content-Type': 'multipart/form-data'
          }
        }
      );
      
      // Refresh students and answers
      const studentsRes = await axios.get(`/api/students/collection/${id}`);
      const updatedStudents = studentsRes.data.students;
      setStudents(updatedStudents);
      await fetchStudentAnswersAndGrades(updatedStudents); // Pass updated students list
      
      setUploadStatus({
        message: "Answers uploaded successfully!",
        error: false,
        details: response.data
      });
      
      // Auto-close after 3 seconds on success
      setTimeout(() => {
        if (answersFile) {  // Only close if we're still showing this modal
          setShowUploadAnswersModal(false);
          setUploadStatus(null);
          setAnswersFile(null);
        }
      }, 3000);
      
    } catch (err) {
      console.error("Failed to upload answers CSV", err);
      setUploadStatus({
        message: "Failed to upload answers: " + (err.response?.data?.detail || err.message),
        error: true,
        details: err.response?.data
      });
    }
  };

  // Add a new answer for a student
  const handleAddAnswer = async () => {
    // Validate that answer is not empty
    if (!newAnswer.answer.trim()) {
      setAnswerError("Answer cannot be empty");
      return;
    }
    
    try {
      await axios.post("/api/student-answers/", {
        answer: newAnswer.answer,
        student_id: selectedStudent.id,
        question_id: selectedQuestion.id
      });
      
      // Refresh answers using the current student state
      await fetchStudentAnswersAndGrades(students);
      
      // Reset form and close modal
      setNewAnswer({ answer: "" });
      setAnswerError("");
      setShowAddAnswerModal(false);
    } catch (err) {
      console.error("Failed to add answer", err);
    }
  };

  // Grade all ungraded answers sequentially
  const handleGradeAll = async () => {
    setIsGradingAll(true);
    console.log("Starting bulk grading...");

    for (const student of students) {
      for (const question of questions) {
        const answer = studentAnswers[student.id]?.[question.id];
        // Check if answer exists and is not already graded
        if (answer && !grades[answer.id]) {
          console.log(`Grading answer ${answer.id} for student ${student.name}, question ${question.id}`);
          try {
            // Await each grading call to process sequentially
            await handleGradeAnswer(answer.id); 
          } catch (err) {
            // Log error but continue with the next answer
            console.error(`Failed to grade answer ${answer.id}:`, err);
          }
        }
      }
    }

    console.log("Bulk grading finished.");
    setIsGradingAll(false);
  };

  // Toggle student dropdown visibility
  const toggleStudent = (studentId) => {
    setOpenStudentId(prevOpenId => (prevOpenId === studentId ? null : studentId));
  };

  // Stream download progress for a model
  const streamModelDownloadProgress = async (answerID) => {
    try {
      // Abort any existing stream
      if (downloadAbortController.current) {
        downloadAbortController.current.abort();
      }
      
      // Create new abort controller for this stream
      downloadAbortController.current = new AbortController();
      setIsDownloadingModel(false); // Initialize to false - only show popup when needed
      setDownloadProgress(null);
      setDownloadStatus(null);
      
      // Using fetch instead of axios for better streaming support
      const response = await fetch(`/api/student-answers/${answerID}/grade/stream`, {
        method: "POST",
        headers: {
          "Authorization": `Bearer ${localStorage.getItem("token")}`
        },
        signal: downloadAbortController.current.signal
      });

      if (!response.ok) {
        throw new Error(`HTTP error! status: ${response.status}`);
      }

      const reader = response.body.getReader();
      const decoder = new TextDecoder();
      let buffer = '';

      while (true) {
        const { done, value } = await reader.read();
        
        if (done) {
          console.log("Stream complete");
          break;
        }
        
        // Decode the chunk and add to buffer
        buffer += decoder.decode(value, { stream: true });
        
        // Process complete lines
        const lines = buffer.split('\n');
        buffer = lines.pop() || ''; // Keep the last incomplete line in buffer
        
        for (const line of lines) {
          if (!line.trim()) continue;
          
          try {
            const data = JSON.parse(line);
            
            // Enhanced debugging
            console.log("Raw streaming data:", data);
            
            // Handle different status messages
            if (data.status === "error") {
              setDownloadStatus({
                success: false,
                message: data.message || "An error occurred during download"
              });
              setIsDownloadingModel(false);
              return false;
            } else if (data.status === "success" || data.status === "model_ready") {
              setDownloadStatus({
                success: true,
                message: data.message || `Model ready for grading`
              });
              // Clear download progress when complete
              setIsDownloadingModel(false);
              setDownloadProgress(null);
              return true;
            } else if (data.status === "model_exists") {
              console.log(`Model ${data.model_name} already exists`);
              // Don't show the download popup for existing models
              setIsDownloadingModel(false);
              // Continue streaming to see if the model works
            } else if (data.status === "downloading" || data.total !== undefined) {
              // Calculate MB for display
              const completed = data.completed || 0;
              const total = data.total || 0;
              const completedMB = Math.round((completed / (1024 * 1024)) * 10) / 10;
              const totalMB = Math.round((total / (1024 * 1024)) * 10) / 10;
              
              console.log(`Progress: ${completedMB}MB / ${totalMB}MB`);
              
              // Show the popup when we're actually downloading
              setIsDownloadingModel(true);
              
              // Update progress
              setDownloadProgress({
                status: data.status || "downloading",
                digest: data.digest,
                total: total,
                completed: completed,
                message: `Downloading ${data.model_name || ""} ${data.digest || ""} - ${completedMB} MB / ${totalMB} MB`
              });
            } else if (data.status === "model_not_found" || data.status === "downloading_gemma") {
              // Show the popup when a download is needed
              setIsDownloadingModel(true);
              
              // For other status updates
              console.log("Status update:", data.status);
              setDownloadProgress({
                status: data.status || "processing",
                message: data.message || data.status
              });
            } else {
              // For other status updates
              console.log("Status update:", data.status);
              setDownloadProgress({
                status: data.status || "processing",
                message: data.message || data.status
              });
            }
          } catch (e) {
            console.error("Failed to parse JSON:", e, line);
          }
        }
      }
      
      // If we get here, the stream completed successfully
      setIsDownloadingModel(false);
      return true;
    } catch (error) {
      console.error("Stream failed:", error);
      setDownloadStatus({ 
        success: false, 
        message: `Failed to download model: ${error.message}`
      });
      setIsDownloadingModel(false);
      setDownloadProgress(null);
      return false;
    }
  };
  
  // Grade a student's answer
  const handleGradeAnswer = async (answerID) => {
    try {
      setGradingInProgress(prev => ({ ...prev, [answerID]: true }));
      
      // First stream the model check/download progress
      await streamModelDownloadProgress(answerID);
      
      // Then proceed with grading
      const gradeRes = await axios.post(`/api/student-answers/${answerID}/grade`);
      
      // Update grades
      setGrades(prev => ({
        ...prev,
        [answerID]: gradeRes.data
      }));
      
      setGradingInProgress(prev => ({ ...prev, [answerID]: false }));
    } catch (err) {
      console.error("Failed to grade answer", err);
      setGradingInProgress(prev => ({ ...prev, [answerID]: false }));
    }
  };

  if (loading) return <div className="loading">Loading...</div>;
  if (error) return <div className="error">{error}</div>;
  if (!collection) return <div className="not-found">Collection not found</div>;

  return (
    <div className="collection-details-container">
      {/* Model Download Progress Bar - Only shown when downloading */}
      {isDownloadingModel && (
        <div className="model-download-overlay">
          <div className="model-download-panel">
            <h3>Downloading Model</h3>
            
            <div className="download-progress">
              <div className="progress-status">
                <span className="status-label">Status:</span>
                <span className="status-value">
                  {downloadProgress?.message || "Initializing download..."}
                </span>
              </div>
              
              {/* Show progress bar if we have download data */}
              {downloadProgress?.total > 0 && (
                <>
                  <div className="progress-bar-container">
                    <div 
                      className="progress-bar" 
                      style={{ 
                        width: `${Math.min(100, (downloadProgress.completed / downloadProgress.total) * 100)}%` 
                      }}
                    ></div>
                  </div>
                  <div className="progress-details">
                    <span>
                      {Math.round((downloadProgress.completed / (1024 * 1024)) * 10) / 10} MB / 
                      {Math.round((downloadProgress.total / (1024 * 1024)) * 10) / 10} MB
                    </span>
                    <span>
                      {Math.round((downloadProgress.completed / downloadProgress.total) * 100)}%
                    </span>
                  </div>
                </>
              )}
            </div>
            
            {downloadStatus && (
              <div className={`download-status ${downloadStatus.success ? 'success' : 'error'}`}>
                {downloadStatus.message}
              </div>
            )}
            
            <p className="download-info">
              Please wait while the model is downloaded. This may take a few minutes.
              <br/>
              The model needs to be downloaded only once.
            </p>
          </div>
        </div>
      )}
      <div className="collection-header">
        <button onClick={() => navigate("/home")} className="back-button">
          ← Back
        </button>
        <h1>{collection.name}</h1>
        <p>{collection.description}</p>
        
        {/* Grading pair information */}
        {combination ? (
          <div className="grading-info">
            <h3>Grading Configuration</h3>
            <p>
              <strong>Prompt-Model Pair:</strong> {combination.name} ({combination.model_name})
              {combination.description && <span className="pair-description"> - {combination.description}</span>}
            </p>
          </div>
        ) : collection.combination_id ? (
          <div className="grading-info">
            <p>Loading grading configuration...</p>
          </div>
        ) : (
          <div className="grading-info grading-warning">
            <p>⚠️ No grading pair selected for this collection.</p>
          </div>
        )}
        
        <div className="collection-actions">
          <button onClick={() => setShowUploadQuestionsModal(true)} className="upload-button">
            Upload Questions CSV
          </button>
          <button 
            onClick={() => setShowUploadAnswersModal(true)} 
            className="upload-button"
            disabled={questions.length === 0}
          >
            Upload Student Answers CSV
          </button>
        </div>
      </div>

      <div className="collection-content">
        <div className="questions-section">
          <div className="section-header">
            <h2>Questions</h2>
            <button onClick={() => setShowAddQuestionModal(true)}>Add Question</button>
          </div>
          <div className="questions-list">
            {questions.length === 0 ? (
              <p>No questions added yet. Add a question to get started.</p>
            ) : (
              questions.map(question => (
                <div key={question.id} className="question-item">
                  <h3>Question: {question.text}</h3>
                  <p><strong>Model Answer:</strong> {question.model_answer}</p>
                </div>
              ))
            )}
          </div>
        </div>

        <div className="students-section">
          <div className="section-header">
            <h2>Students</h2>
            <div> {/* Container for buttons */}
              <button 
                onClick={handleGradeAll} 
                disabled={isGradingAll || students.length === 0 || questions.length === 0}
                className="grade-all-button"
                style={{ marginRight: '10px' }} // Add some spacing
              >
                {isGradingAll ? "Grading All..." : "Grade All"}
              </button>
              <button onClick={() => setShowAddStudentModal(true)}>Add Student</button>
            </div>
          </div>
          <div className="students-list">
            {students.length === 0 ? (
              <p>No students added yet. Add students to this collection.</p>
            ) : (
              students.map(student => (
                <div key={student.id} className="student-item">
                  <h3 onClick={() => toggleStudent(student.id)} style={{ cursor: 'pointer' }}>
                    {student.name} {openStudentId === student.id ? '▲' : '▼'}
                  </h3>
                  
                  {/* Display all questions and answers for this student - Conditionally Rendered */}
                  {openStudentId === student.id && (
                    <div className="student-answers">
                    {questions.map(question => {
                      const answer = studentAnswers[student.id]?.[question.id];
                      const grade = answer ? grades[answer.id] : null;
                      
                      return (
                        <div key={question.id} className="answer-item">
                          <p><strong>Question:</strong> {question.text}</p>
                          
                          {answer ? (
                            <>
                              <p><strong>Answer:</strong> {answer.answer}</p>
                              
                              {grade ? (
                                <div className="grade-display">
                                  <p><strong>Grade:</strong> {grade.grade.toFixed(2)}</p>
                                  <p><strong>Feedback:</strong> {grade.feedback}</p>
                                </div>
                              ) : (
                                <button 
                                  onClick={() => handleGradeAnswer(answer.id)}
                                  disabled={gradingInProgress[answer.id]}
                                  className="grade-button"
                                >
                                  {gradingInProgress[answer.id] ? "Grading..." : "Grade"}
                                </button>
                              )}
                            </>
                          ) : (
                            <div className="no-answer">
                              <p>No answer submitted</p>
                              <button 
                                onClick={() => {
                                  setSelectedStudent(student);
                                  setSelectedQuestion(question);
                                  setShowAddAnswerModal(true);
                                }}
                              >
                                Add Answer
                              </button>
                            </div>
                          )}
                        </div>
                      );
                    })}
                  </div>
                  )} {/* End conditional rendering */}
                </div>
              ))
            )}
          </div>
        </div>
      </div>

      {/* Add Question Modal */}
      {showAddQuestionModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h2>Add New Question</h2>
            <input
              type="text"
              placeholder="Question Text"
              value={newQuestion.text}
              onChange={(e) => setNewQuestion({ ...newQuestion, text: e.target.value })}
            />
            <textarea
              placeholder="Model Answer (correct answer)"
              value={newQuestion.model_answer}
              onChange={(e) => setNewQuestion({ ...newQuestion, model_answer: e.target.value })}
            />
            <div className="modal-buttons">
              <button onClick={() => setShowAddQuestionModal(false)}>Cancel</button>
              <button onClick={handleAddQuestion}>Add Question</button>
            </div>
          </div>
        </div>
      )}

      {/* Add Student Modal */}
      {showAddStudentModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h2>Add New Student</h2>
            <input
              type="text"
              placeholder="Student Name"
              value={newStudent.name}
              onChange={(e) => setNewStudent({ ...newStudent, name: e.target.value })}
            />
            <input
              type="text"
              placeholder="Student PID (e.g., email)"
              value={newStudent.pid}
              onChange={(e) => setNewStudent({ ...newStudent, pid: e.target.value })}
            />
            <div className="modal-buttons">
              <button onClick={() => setShowAddStudentModal(false)}>Cancel</button>
              <button onClick={handleAddStudent}>Add Student</button>
            </div>
          </div>
        </div>
      )}

      {/* Add Answer Modal */}
      {showAddAnswerModal && selectedStudent && selectedQuestion && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h2>Add Answer for {selectedStudent.name}</h2>
            <p><strong>Question:</strong> {selectedQuestion.text}</p>
            <textarea
              placeholder="Student's Answer"
              value={newAnswer.answer}
              onChange={(e) => setNewAnswer({ ...newAnswer, answer: e.target.value })}
            />
            <div className="modal-buttons">
              {answerError && <p className="answer-error">{answerError}</p>}
              <button onClick={() => {
                setShowAddAnswerModal(false);
                setAnswerError("");
              }}>Cancel</button>
              <button 
                onClick={handleAddAnswer}
                disabled={!newAnswer.answer.trim()}
              >Save Answer</button>
            </div>
          </div>
        </div>
      )}
      
      {/* Upload Questions CSV Modal */}
      {showUploadQuestionsModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h2>Upload Questions CSV</h2>
            <p>Upload a CSV file with questions and model answers.</p>
            <p className="csv-format">Expected format: <code>question,model_answer</code></p>
            <p className="csv-example">Example: <code>"What is X?","X is Y"</code></p>
            
            <div className="file-upload-container">
              <label className="file-upload-button" htmlFor="questions-csv-upload">
                Choose CSV File
              </label>
              <input
                id="questions-csv-upload"
                type="file"
                accept=".csv"
                onChange={(e) => {
                  const file = e.target.files[0];
                  setQuestionsFile(file);
                }}
              />
              <div className={`file-name-display ${questionsFile ? 'visible' : ''}`}>
                {questionsFile ? questionsFile.name : ''}
              </div>
            </div>
            
            {uploadStatus && (
              <div className={`upload-status ${uploadStatus.error ? 'error' : 'success'}`}>
                <p>{uploadStatus.message}</p>
                {uploadStatus.details && (
                  <pre>{JSON.stringify(uploadStatus.details, null, 2)}</pre>
                )}
              </div>
            )}
            
            <div className="modal-buttons">
              <button onClick={() => {
                setShowUploadQuestionsModal(false);
                setUploadStatus(null);
                setQuestionsFile(null);
              }}>Cancel</button>
              <button 
                onClick={handleUploadQuestions}
                disabled={!questionsFile}
                className={questionsFile ? 'upload-highlight' : ''}
              >
                Upload
              </button>
            </div>
          </div>
        </div>
      )}
      
      {/* Upload Answers CSV Modal */}
      {showUploadAnswersModal && (
        <div className="modal-overlay">
          <div className="modal-content">
            <h2>Upload Student Answers CSV</h2>
            <p>Upload a CSV file with student answers.</p>
            <p className="csv-format">Expected format: <code>student_name,student_pid,question,answer</code></p>
            <p className="csv-example">Example: <code>"John Doe","johndoe@vt.edu","What is X?","X is Z"</code></p>
            <p className="csv-note">Note: Questions must already exist in the collection.</p>
            
            <div className="file-upload-container">
              <label className="file-upload-button" htmlFor="answers-csv-upload">
                Choose CSV File
              </label>
              <input
                id="answers-csv-upload"
                type="file"
                accept=".csv"
                onChange={(e) => {
                  const file = e.target.files[0];
                  setAnswersFile(file);
                }}
              />
              <div className={`file-name-display ${answersFile ? 'visible' : ''}`}>
                {answersFile ? answersFile.name : ''}
              </div>
            </div>
            
            {uploadStatus && (
              <div className={`upload-status ${uploadStatus.error ? 'error' : 'success'}`}>
                <p>{uploadStatus.message}</p>
                {uploadStatus.details && (
                  <pre>{JSON.stringify(uploadStatus.details, null, 2)}</pre>
                )}
              </div>
            )}
            
            <div className="modal-buttons">
              <button onClick={() => {
                setShowUploadAnswersModal(false);
                setUploadStatus(null);
                setAnswersFile(null);
              }}>Cancel</button>
              <button 
                onClick={handleUploadAnswers}
                disabled={!answersFile}
                className={answersFile ? 'upload-highlight' : ''}
              >
                Upload
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}
