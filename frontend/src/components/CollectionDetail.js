import React, { useState, useEffect } from 'react';
import { getQuestions, deleteQuestion, getStudents } from '../services/api';
import QuestionForm from './QuestionForm';
import StudentAnswerForm from './StudentAnswerForm';
import '../styles/CollectionDetail.css';

const CollectionDetail = ({ collection, onClose, onRefresh }) => {
  const [activeTab, setActiveTab] = useState('details');
  const [questions, setQuestions] = useState([]);
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [showQuestionForm, setShowQuestionForm] = useState(false);
  const [editingQuestion, setEditingQuestion] = useState(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [questionToDelete, setQuestionToDelete] = useState(null);
  const [showAnswerForm, setShowAnswerForm] = useState(false);
  const [selectedStudent, setSelectedStudent] = useState(null);

  useEffect(() => {
    if (activeTab === 'questions' && collection) {
      fetchQuestions();
    }
    
    if (activeTab === 'answers' && collection) {
      fetchStudents();
      fetchQuestions();
    }
  }, [activeTab, collection]);

  const fetchQuestions = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getQuestions(collection.id);
      setQuestions(data.questions || []);
    } catch (err) {
      setError('Failed to load questions');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const fetchStudents = async () => {
    setLoading(true);
    setError(null);
    try {
      const data = await getStudents();
      setStudents(data.students || []);
    } catch (err) {
      setError('Failed to load students');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleCreateQuestion = () => {
    setEditingQuestion(null);
    setShowQuestionForm(true);
  };

  const handleEditQuestion = (question) => {
    setEditingQuestion(question);
    setShowQuestionForm(true);
  };

  const handleDeletePrompt = (question) => {
    setQuestionToDelete(question);
    setShowDeleteConfirm(true);
  };

  const handleDeleteConfirm = async () => {
    try {
      await deleteQuestion(collection.id, questionToDelete.id);
      setShowDeleteConfirm(false);
      setQuestionToDelete(null);
      fetchQuestions();
    } catch (err) {
      setError('Failed to delete question');
      console.error(err);
    }
  };

  const handleQuestionFormSubmit = async (questionData) => {
    setLoading(true);
    try {
      if (editingQuestion) {
        await updateQuestion(collection.id, editingQuestion.id, questionData);
      } else {
        await createQuestion(collection.id, questionData);
      }
      setShowQuestionForm(false);
      fetchQuestions();
    } catch (err) {
      setError(editingQuestion ? 'Failed to update question' : 'Failed to create question');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const handleStudentSelect = (student) => {
    setSelectedStudent(student);
    setShowAnswerForm(true);
  };

  const handleAnswerFormSubmit = async () => {
    setShowAnswerForm(false);
    setSelectedStudent(null);
    // After answers are submitted, we don't need to refresh any data
    // as we're not displaying answers in this component
  };

  const truncateText = (text, maxLength = 100) => {
    if (!text) return '';
    return text.length > maxLength ? `${text.substring(0, maxLength)}...` : text;
  };

  return (
    <div className="collection-detail">
      <button className="close-btn" onClick={onClose}>✖</button>
      
      <div className="collection-tabs">
        <button 
          className={activeTab === 'details' ? 'active' : ''} 
          onClick={() => setActiveTab('details')}
        >
          Details
        </button>
        <button 
          className={activeTab === 'questions' ? 'active' : ''} 
          onClick={() => setActiveTab('questions')}
        >
          Questions
        </button>
        <button 
          className={activeTab === 'answers' ? 'active' : ''} 
          onClick={() => setActiveTab('answers')}
        >
          Submit Answers
        </button>
      </div>
      
      {activeTab === 'details' && (
        <div className="details-tab">
          <h1>{collection.name}</h1>
          <p className="collection-description">{collection.description}</p>
          <p className="collection-meta">Created: {new Date(collection.created_at).toLocaleDateString()}</p>
        </div>
      )}
      
      {activeTab === 'questions' && (
        <div className="questions-tab">
          <div className="questions-header">
            <h2>Questions</h2>
            <button 
              className="add-question-btn" 
              onClick={handleCreateQuestion}
            >
              Add Question
            </button>
          </div>
          
          {loading && <div className="loading">Loading questions...</div>}
          
          {error && <div className="error-message">{error}</div>}
          
          {!loading && !error && questions.length === 0 ? (
            <div className="no-questions">
              <p>No questions have been added to this collection yet.</p>
              <button 
                className="add-first-question-btn" 
                onClick={handleCreateQuestion}
              >
                Add Your First Question
              </button>
            </div>
          ) : (
            <div className="questions-list">
              {questions.map(question => (
                <div key={question.id} className="question-item">
                  <div className="question-content">
                    <h3>{truncateText(question.question_text, 150)}</h3>
                    <p>Example Answer: {truncateText(question.example_answer, 200)}</p>
                  </div>
                  <div className="question-actions">
                    <button 
                      className="edit-btn" 
                      onClick={() => handleEditQuestion(question)}
                    >
                      Edit
                    </button>
                    <button 
                      className="delete-btn" 
                      onClick={() => handleDeletePrompt(question)}
                    >
                      Delete
                    </button>
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
      
      {activeTab === 'answers' && (
        <div className="answers-tab">
          <div className="answers-header">
            <h2>Submit Student Answers</h2>
          </div>
          
          {loading && <div className="loading">Loading data...</div>}
          
          {error && <div className="error-message">{error}</div>}
          
          {!loading && !error && (
            <>
              {questions.length === 0 ? (
                <div className="no-questions">
                  <p>No questions have been added to this collection yet.</p>
                  <button 
                    className="add-first-question-btn" 
                    onClick={() => setActiveTab('questions')}
                  >
                    Go to Questions Tab
                  </button>
                </div>
              ) : students.length === 0 ? (
                <div className="no-students">
                  <p>No students have been added yet.</p>
                  <button 
                    className="add-student-btn" 
                    onClick={() => window.location.href = '/students'}
                  >
                    Go to Students Page
                  </button>
                </div>
              ) : (
                <div className="student-selection">
                  <h3>Select a student to submit answers for:</h3>
                  <div className="students-list">
                    {students.map(student => (
                      <div 
                        key={student.id} 
                        className="student-select-item"
                        onClick={() => handleStudentSelect(student)}
                      >
                        <h4>{student.student_name}</h4>
                        <p>School ID: {student.school_id}</p>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </>
          )}
        </div>
      )}
      
      {showQuestionForm && (
        <div className="modal-overlay">
          <div className="modal-content">
            <QuestionForm 
              collectionId={collection.id}
              question={editingQuestion}
              onSubmit={handleQuestionFormSubmit}
              onCancel={() => setShowQuestionForm(false)}
            />
          </div>
        </div>
      )}
      
      {showAnswerForm && selectedStudent && (
        <div className="modal-overlay">
          <div className="modal-content">
            <StudentAnswerForm
              student={selectedStudent}
              collectionId={collection.id}
              onSubmit={handleAnswerFormSubmit}
              onCancel={() => {
                setShowAnswerForm(false);
                setSelectedStudent(null);
              }}
            />
          </div>
        </div>
      )}
      
      {showDeleteConfirm && (
        <div className="modal-overlay">
          <div className="modal-content delete-confirm">
            <h3>Delete Question</h3>
            <p>Are you sure you want to delete this question? This action cannot be undone.</p>
            <div className="delete-actions">
              <button 
                className="cancel-btn" 
                onClick={() => setShowDeleteConfirm(false)}
              >
                Cancel
              </button>
              <button 
                className="delete-confirm-btn" 
                onClick={handleDeleteConfirm}
              >
                Delete
              </button>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default CollectionDetail;

// Import these at the top but forgot to add them
function createQuestion(collectionId, questionData) {
  return import('../services/api.js').then(module => {
    return module.createQuestion(collectionId, questionData);
  });
}

function updateQuestion(collectionId, questionId, questionData) {
  return import('../services/api.js').then(module => {
    return module.updateQuestion(collectionId, questionId, questionData);
  });
}
