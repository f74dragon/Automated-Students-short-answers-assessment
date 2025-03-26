import React, { useState } from 'react';
import '../styles/StudentForm.css';

const StudentForm = ({ 
  student = null, 
  onSubmit, 
  onCancel 
}) => {
  const [studentName, setStudentName] = useState(student ? student.student_name : '');
  const [schoolId, setSchoolId] = useState(student ? student.school_id : '');
  const [errors, setErrors] = useState({});

  const validate = () => {
    const newErrors = {};
    if (!studentName.trim()) newErrors.studentName = 'Student name is required';
    if (!schoolId || isNaN(schoolId)) newErrors.schoolId = 'Valid school ID is required';
    
    setErrors(newErrors);
    return Object.keys(newErrors).length === 0;
  };

  const handleSubmit = (e) => {
    e.preventDefault();
    
    if (!validate()) return;

    const studentData = {
      student_name: studentName,
      school_id: parseInt(schoolId, 10)
    };

    // If we're editing an existing student, add the ID
    if (student) {
      studentData.id = student.id;
    }

    onSubmit(studentData);
  };

  return (
    <form className="student-form" onSubmit={handleSubmit}>
      <h2>{student ? 'Edit Student' : 'Add New Student'}</h2>
      
      <div className="form-group">
        <label>Student Name</label>
        <input
          type="text"
          value={studentName}
          onChange={(e) => setStudentName(e.target.value)}
          placeholder="Enter student name"
          className={errors.studentName ? 'error' : ''}
        />
        {errors.studentName && <span className="error-text">{errors.studentName}</span>}
      </div>
      
      <div className="form-group">
        <label>School ID</label>
        <input
          type="number"
          value={schoolId}
          onChange={(e) => setSchoolId(e.target.value)}
          placeholder="Enter school ID"
          className={errors.schoolId ? 'error' : ''}
        />
        {errors.schoolId && <span className="error-text">{errors.schoolId}</span>}
      </div>
      
      <div className="form-actions">
        <button type="button" className="cancel-btn" onClick={onCancel}>
          Cancel
        </button>
        <button type="submit" className="submit-btn">
          {student ? 'Update Student' : 'Add Student'}
        </button>
      </div>
    </form>
  );
};

export default StudentForm;
