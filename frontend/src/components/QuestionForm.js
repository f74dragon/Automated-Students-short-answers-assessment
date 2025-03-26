import React, { useState } from 'react';
import '../styles/QuestionForm.css';

const QuestionForm = ({ 
  collectionId, 
  question = null, 
  onSubmit, 
  onCancel 
}) => {
  const [questionText, setQuestionText] = useState(question ? question.question_text : '');
  const [exampleAnswer, setExampleAnswer] = useState(question ? question.example_answer : '');
  const [errors, setErrors] = useState({});

  const validate = () => {
    const newErrors = {};
    if (!questionText.trim()) newErrors.questionText = 'Question text is required';
    if (!exampleAnswer.trim()) newErrors.exampleAnswer = 'Example answer is required';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!validate()) return;

    const questionData = {
      collection_id: collectionId,
      question_text: questionText,
      example_answer: exampleAnswer
    };

    // If we're editing an existing question, add the ID
    if (question) {
      questionData.id = question.id;
    }

    onSubmit(questionData);
  };

  return (
    <form className="question-form" onSubmit={handleSubmit}>
      <h2>{question ? 'Edit Question' : 'Create New Question'}</h2>
      
      <div className="form-group">
        <label>Question Text</label>
        <textarea
          value={questionText}
          onChange={(e) => setQuestionText(e.target.value)}
          placeholder="Enter the question text"
          className={errors.questionText ? 'error' : ''}
        />
        {errors.questionText && <span className="error-text">{errors.questionText}</span>}
      </div>
      
      <div className="form-group">
        <label>Example Answer</label>
        <textarea
          value={exampleAnswer}
          onChange={(e) => setExampleAnswer(e.target.value)}
          placeholder="Enter an example/model answer"
          className={errors.exampleAnswer ? 'error' : ''}
          rows={5}
        />
        {errors.exampleAnswer && <span className="error-text">{errors.exampleAnswer}</span>}
      </div>
      
      <div className="form-actions">
        <button type="button" className="cancel-btn" onClick={onCancel}>
          Cancel
        </button>
        <button type="submit" className="submit-btn">
          {question ? 'Update Question' : 'Create Question'}
        </button>
      </div>
    </form>
  );
};

export default QuestionForm;
