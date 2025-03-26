import React, { useEffect, useState } from 'react';
import { useNavigate, Link } from 'react-router-dom';
import {
  getStudents,
  createStudent,
  updateStudent,
  deleteStudent
} from '../services/api';
import StudentForm from '../components/StudentForm';
import StudentDetail from '../components/StudentDetail';
import '../styles/Students.css';

export default function Students() {
  const [students, setStudents] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [selectedStudent, setSelectedStudent] = useState(null);
  const [showStudentForm, setShowStudentForm] = useState(false);
  const [editingStudent, setEditingStudent] = useState(null);
  const [showDeleteConfirm, setShowDeleteConfirm] = useState(false);
  const [studentToDelete, setStudentToDelete] = useState(null);
  const [userId, setUserId] = useState(null);
  const navigate = useNavigate();

  useEffect(() => {
    const token = localStorage.getItem('token');
    if (!token) return navigate('/');

    const fetchUserAndStudents = async () => {
      try {
        // Get the user ID from the token
        const decodedToken = JSON.parse(atob(token.split('.')[1]));
        setUserId(decodedToken.sub);
        
        // Fetch students
        await fetchStudents();
      } catch (err) {
        setError('Failed to fetch data');
        console.error(err);
      } finally {
        setLoading(false);
      }
    };

    fetchUserAndStudents();
  }, [navigate]);

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

  const handleCreateStudent = async (studentData) => {
    setLoading(true);
    try {
      await createStudent(studentData);
      setShowStudentForm(false);
      fetchStudents();
    } catch (err) {
      setError('Failed to create student');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleEditStudent = (student) => {
    setEditingStudent(student);
    setSelectedStudent(null);
    setShowStudentForm(true);
  };

  const handleUpdateStudent = async (studentData) => {
    setLoading(true);
    try {
      await updateStudent(studentData.id, studentData);
      setShowStudentForm(false);
      setEditingStudent(null);
      fetchStudents();
    } catch (err) {
      setError('Failed to update student');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handleDeletePrompt = (student) => {
    setStudentToDelete(student);
    setSelectedStudent(null);
    setShowDeleteConfirm(true);
  };

  const handleDeleteConfirm = async () => {
    setLoading(true);
    try {
      await deleteStudent(studentToDelete.id);
      setShowDeleteConfirm(false);
      setStudentToDelete(null);
      fetchStudents();
    } catch (err) {
      setError('Failed to delete student');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="students-container">
      <div className="taskbar">
        <div className="taskbar-left">
          <Link to="/home">🏠 Home</Link>
          <Link to="/students" className="active">👨‍🎓 Students</Link>
        </div>
        <div className="taskbar-right">
          <button className="create-student-btn" onClick={() => setShowStudentForm(true)}>
            ➕ Add Student
          </button>
          <span className="user-icon">👤</span>
        </div>
      </div>

      <div className="content-box">
        <h1>Students</h1>
        
        {loading && <div className="loading">Loading students...</div>}
        
        {error && <div className="error-message">{error}</div>}
        
        {!loading && !error && students.length === 0 ? (
          <div className="no-students">
            <p>No students have been added yet.</p>
            <button 
              className="add-first-student-btn" 
              onClick={() => setShowStudentForm(true)}
            >
              Add Your First Student
            </button>
          </div>
        ) : (
          <div className="students-grid">
            {students.map((student) => (
              <div
                key={student.id}
                className="student-card"
                onClick={() => setSelectedStudent(student)}
              >
                <h3>{student.student_name}</h3>
                <p>School ID: {student.school_id}</p>
              </div>
            ))}
          </div>
        )}
      </div>

      {selectedStudent && (
        <div className="modal-overlay">
          <div className="modal-content">
            <StudentDetail 
              student={selectedStudent}
              onClose={() => setSelectedStudent(null)}
              onEdit={handleEditStudent}
              onDelete={handleDeletePrompt}
            />
          </div>
        </div>
      )}

      {showStudentForm && (
        <div className="modal-overlay">
          <div className="modal-content">
            <StudentForm
              student={editingStudent}
              onSubmit={editingStudent ? handleUpdateStudent : handleCreateStudent}
              onCancel={() => {
                setShowStudentForm(false);
                setEditingStudent(null);
              }}
            />
          </div>
        </div>
      )}

      {showDeleteConfirm && (
        <div className="modal-overlay">
          <div className="modal-content delete-confirm">
            <h3>Delete Student</h3>
            <p>Are you sure you want to delete {studentToDelete.student_name}? This action cannot be undone.</p>
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
}
