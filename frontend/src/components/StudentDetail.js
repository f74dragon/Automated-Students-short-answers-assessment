import React, { useState, useEffect } from 'react';
import { getStudentAnswers } from '../services/api';
import '../styles/StudentDetail.css';

const StudentDetail = ({ student, onClose, onEdit, onDelete, questions = [] }) => {
  const [answers, setAnswers] = useState([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);
  const [activeTab, setActiveTab] = useState('details');
  
  useEffect(() => {
    if (student && activeTab === 'answers') {
      fetchStudentAnswers();
    }
  }, [student, activeTab]);
  
  const fetchStudentAnswers = async () => {
    if (!student) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await getStudentAnswers(student.id);
      setAnswers(response.answers || []);
    } catch (err) {
      setError('Failed to load student answers');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };
  
  const findQuestionText = (questionId) => {
    const question = questions.find(q => q.id === questionId);
    return question ? question.question_text : 'Question not found';
  };
  
  return (
    <div className="student-detail">
      
      
      <div className="student-tabs">
        <button 
          className={activeTab === 'details' ? 'active' : ''} 
          onClick={() => setActiveTab('details')}
        >
          Details
        </button>
        <button 
          className={activeTab === 'answers' ? 'active' : ''} 
          onClick={() => setActiveTab('answers')}
        >
          Answers
        </button>
      </div>
      
      {activeTab === 'details' && (
        <div className="details-tab">
          <h1>{student.student_name}</h1>
          <p className="student-meta">School ID: {student.school_id}</p>
          
          <div className="student-actions">
            <button className="edit-btn" onClick={() => onEdit(student)}>
              Edit Student
            </button>
            <button className="delete-btn" onClick={() => onDelete(student)}>
              Delete Student
            </button>
          </div>
        </div>
      )}
      
      {activeTab === 'answers' && (
        <div className="answers-tab">
          <h2>Student Answers</h2>
          
          {loading && <div className="loading">Loading answers...</div>}
          
          {error && <div className="error-message">{error}</div>}
          
          {!loading && !error && answers.length === 0 ? (
            <div className="no-answers">
              <p>This student hasn't submitted any answers yet.</p>
            </div>
          ) : (
            <div className="answers-list">
              {answers.map(answer => (
                <div key={answer.id} className="answer-item">
                  <div className="question-text">
                    <strong>Question:</strong> {findQuestionText(answer.question_id)}
                  </div>
                  <div className="answer-text">
                    <strong>Answer:</strong> {answer.answer_text}
                  </div>
                </div>
              ))}
            </div>
          )}
        </div>
      )}
      <button className="close-btn" onClick={onClose}>Close</button>
    </div>
  );
};

export default StudentDetail;
