import csv
import io
from typing import Dict, List, Tuple, Optional
from sqlalchemy.orm import Session
from app.database import crud
from app.models.collection import Collection
from app.models.question import Question
from app.models.student import Student
from app.models.student_answer import StudentAnswer
from app.schemas.question_schema import QuestionCreate
from app.schemas.student_schema import StudentCreate
from app.schemas.student_answer_schema import StudentAnswerCreate

class CSVService:
    """Service for handling CSV file uploads and processing."""
    
    @staticmethod
    def process_questions_csv(db: Session, collection_id: int, csv_content: bytes) -> Dict:
        """
        Process a CSV file containing questions and model answers for a collection.
        
        Args:
            db: Database session
            collection_id: Collection ID to add questions to
            csv_content: CSV file content as bytes
            
        Returns:
            Dict with processing statistics
        """
        # Check if collection exists
        collection = db.query(Collection).filter(Collection.id == collection_id).first()
        if not collection:
            raise ValueError(f"Collection with ID {collection_id} does not exist")
        
        # Parse CSV
        csv_text = csv_content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_text))
        
        expected_headers = ['question', 'model_answer']
        actual_headers = csv_reader.fieldnames
        
        if not actual_headers or not all(header in actual_headers for header in expected_headers):
            raise ValueError(f"CSV must contain headers: {', '.join(expected_headers)}")
        
        # Process rows
        stats = {
            'total': 0,
            'created': 0,
            'updated': 0,
            'errors': 0,
            'error_details': []
        }
        
        for i, row in enumerate(csv_reader, start=1):
            stats['total'] += 1
            
            try:
                question_text = row['question'].strip()
                model_answer = row['model_answer'].strip()
                
                if not question_text or not model_answer:
                    raise ValueError("Question and model answer cannot be empty")
                
                # Check if question already exists in this collection
                existing_question = db.query(Question).filter(
                    Question.collection_id == collection_id,
                    Question.text == question_text
                ).first()
                
                if existing_question:
                    # Update the model answer
                    existing_question.model_answer = model_answer
                    db.commit()
                    stats['updated'] += 1
                else:
                    # Create new question
                    question_create = QuestionCreate(
                        text=question_text,
                        model_answer=model_answer,
                        collection_id=collection_id
                    )
                    crud.create_question(db, question_create)
                    stats['created'] += 1
                    
            except Exception as e:
                stats['errors'] += 1
                stats['error_details'].append({
                    'row': i,
                    'error': str(e)
                })
        
        return stats
    
    @staticmethod
    def process_answers_csv(db: Session, collection_id: int, csv_content: bytes) -> Dict:
        """
        Process a CSV file containing student answers for a collection.
        
        Args:
            db: Database session
            collection_id: Collection ID
            csv_content: CSV file content as bytes
            
        Returns:
            Dict with processing statistics
        """
        # Check if collection exists
        collection = db.query(Collection).filter(Collection.id == collection_id).first()
        if not collection:
            raise ValueError(f"Collection with ID {collection_id} does not exist")
        
        # Parse CSV
        csv_text = csv_content.decode('utf-8')
        csv_reader = csv.DictReader(io.StringIO(csv_text))
        
        expected_headers = ['student_name', 'student_pid', 'question', 'answer']
        actual_headers = csv_reader.fieldnames
        
        if not actual_headers or not all(header in actual_headers for header in expected_headers):
            raise ValueError(f"CSV must contain headers: {', '.join(expected_headers)}")
        
        # Load all questions for this collection for quick lookup
        questions = db.query(Question).filter(Question.collection_id == collection_id).all()
        question_map = {q.text.lower().strip(): q for q in questions}
        
        if not questions:
            raise ValueError(f"No questions found for collection {collection_id}. Please upload questions first.")
        
        # Process rows
        stats = {
            'total': 0,
            'students_created': 0,
            'students_updated': 0,
            'answers_created': 0,
            'answers_updated': 0,
            'errors': 0,
            'error_details': []
        }
        
        # Track processed students by PID to avoid duplicates
        processed_students = {}
        
        for i, row in enumerate(csv_reader, start=1):
            stats['total'] += 1
            
            try:
                student_name = row['student_name'].strip()
                student_pid = row['student_pid'].strip()
                question_text = row['question'].strip()
                answer_text = row['answer'].strip()
                
                if not student_name or not student_pid or not question_text or not answer_text:
                    raise ValueError("All fields (student_name, student_pid, question, answer) are required")
                
                # Find matching question
                question = question_map.get(question_text.lower().strip())
                if not question:
                    raise ValueError(f"Question not found in collection: '{question_text}'")
                
                # Get or create student
                student = None
                if student_pid in processed_students:
                    student = processed_students[student_pid]
                else:
                    # Check if student already exists in this collection
                    student = db.query(Student).filter(
                        Student.collection_id == collection_id,
                        Student.pid == student_pid
                    ).first()
                    
                    if student:
                        # Update student name if it has changed
                        if student.name != student_name:
                            student.name = student_name
                            db.commit()
                        stats['students_updated'] += 1
                    else:
                        # Create new student
                        student_create = StudentCreate(
                            name=student_name,
                            pid=student_pid,
                            collection_id=collection_id
                        )
                        student = crud.create_student(db, student_create)
                        stats['students_created'] += 1
                    
                    processed_students[student_pid] = student
                
                # Check if answer already exists
                existing_answer = db.query(StudentAnswer).filter(
                    StudentAnswer.student_id == student.id,
                    StudentAnswer.question_id == question.id
                ).first()
                
                if existing_answer:
                    # Update the answer
                    existing_answer.answer = answer_text
                    db.commit()
                    stats['answers_updated'] += 1
                else:
                    # Create new answer
                    answer_create = StudentAnswerCreate(
                        answer=answer_text,
                        student_id=student.id,
                        question_id=question.id
                    )
                    crud.create_student_answer(db, answer_create)
                    stats['answers_created'] += 1
                    
            except Exception as e:
                stats['errors'] += 1
                stats['error_details'].append({
                    'row': i,
                    'error': str(e)
                })
        
        return stats
