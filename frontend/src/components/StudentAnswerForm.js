import React, { useState, useEffect } from 'react';
import { getQuestions, createStudentAnswer, createStudentAnswersBulk } from '../services/api';
import '../styles/StudentAnswerForm.css';

const StudentAnswerForm = ({ 
  student, 
  collectionId,
  onSubmit, 
  onCancel 
}) => {
  const [questions, setQuestions] = useState([]);
  const [answers, setAnswers] = useState({});
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [submitting, setSubmitting] = useState(false);

  useEffect(() => {
    fetchQuestions();
  }, [collectionId]);

  const fetchQuestions = async () => {
    if (!collectionId) return;
    
    setLoading(true);
    setError(null);
    
    try {
      const response = await getQuestions(collectionId);
      setQuestions(response.questions || []);
      
      // Initialize answers object
      const initialAnswers = {};
      response.questions.forEach(question => {
        initialAnswers[question.id] = '';
      });
      setAnswers(initialAnswers);
    } catch (err) {
      setError('Failed to load questions');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleAnswerChange = (questionId, value) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: value
    }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    
    if (!student || !collectionId) {
      setError('Missing student or collection information');
      return;
    }
    
    // Convert answers object to array format for bulk submission
    const answersArray = Object.entries(answers)
      .filter(([_, value]) => value.trim() !== '') // Only submit non-empty answers
      .map(([questionId, answer_text]) => ({
        question_id: parseInt(questionId, 10),
        answer_text
      }));
    
    if (answersArray.length === 0) {
      setError('Please provide at least one answer');
      return;
    }
    
    setSubmitting(true);
    setError(null);
    
    try {
      // Use bulk submission
      await createStudentAnswersBulk(student.id, answersArray);
      onSubmit();
    } catch (err) {
      setError('Failed to submit answers');
      console.error(err);
    } finally {
      setSubmitting(false);
    }
  };

  if (loading) {
    return <div className="loading">Loading questions...</div>;
  }

  if (error) {
    return <div className="error-message">{error}</div>;
  }

  return (
    <form className="student-answer-form" onSubmit={handleSubmit}>
      <h2>Submit Answers for {student.student_name}</h2>
      
      {questions.length === 0 ? (
        <div className="no-questions">
          <p>No questions available in this collection.</p>
        </div>
      ) : (
        <>
          <div className="questions-list">
            {questions.map(question => (
              <div key={question.id} className="question-item">
                <div className="question-text">
                  <strong>Question:</strong> {question.question_text}
                </div>
                <div className="answer-input">
                  <label htmlFor={`answer-${question.id}`}>Your Answer:</label>
                  <textarea
                    id={`answer-${question.id}`}
                    value={answers[question.id] || ''}
                    onChange={(e) => handleAnswerChange(question.id, e.target.value)}
                    placeholder="Enter your answer here"
                    rows={3}
                  />
                </div>
                <div className="example-answer">
                  <details>
                    <summary>View Example Answer</summary>
                    <div className="example-content">
                      {question.example_answer}
                    </div>
                  </details>
                </div>
              </div>
            ))}
          </div>
          
          <div className="form-actions">
            <button type="button" className="cancel-btn" onClick={onCancel}>
              Cancel
            </button>
            <button 
              type="submit" 
              className="submit-btn" 
              disabled={submitting}
            >
              {submitting ? 'Submitting...' : 'Submit Answers'}
            </button>
          </div>
        </>
      )}
    </form>
  );
};

export default StudentAnswerForm;
