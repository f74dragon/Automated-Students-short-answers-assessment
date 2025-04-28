# app/database/crud.py
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.collection import Collection
from app.models.student import Student
from app.models.question import Question
from app.models.student_answer import StudentAnswer
from app.models.llm_response import LLMResponse
from app.schemas.user_schema import UserCreate, UserResponse, UserListResponse, UserDeleteResponse
from app.schemas.collection_schema import CollectionCreate, CollectionResponse, CollectionListResponse, CollectionDeleteResponse
from app.schemas.student_schema import StudentCreate, StudentResponse, StudentListResponse, StudentDeleteResponse
from app.schemas.question_schema import QuestionCreate, QuestionResponse, QuestionListResponse, QuestionDeleteResponse
from app.schemas.student_answer_schema import StudentAnswerCreate, StudentAnswerResponse, StudentAnswerListResponse, StudentAnswerDeleteResponse
from app.schemas.llm_response_schema import LLMResponseCreate, LLMResponseResponse, LLMResponseListResponse
from app.auth.auth import get_password_hash 

"""
User Database Functions
"""
def create_user(db: Session, user: UserCreate) -> User:
    """Create a new user with a hashed password."""
    hashed_password = get_password_hash(user.password)  # Hash password before saving
    db_user = User(username=user.username, password=hashed_password)  # Store hashed password
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user

def get_users(db: Session) -> UserListResponse:
    users = db.query(User).all()
    return UserListResponse(users=[UserResponse(id=user.id, username=user.username, password=user.password) for user in users])

def get_user(db: Session, user_id: int) -> UserResponse:
    user = db.query(User).where(User.id == user_id).first()
    if not user:
        raise ValueError(f"User {user_id} not found") 
    return UserResponse(id=user.id, username=user.username, password=user.password)

def delete_user(db: Session, user_id: int) -> UserDeleteResponse:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError(f"User {user_id} not found") 
    db.delete(user)
    db.commit()
    return UserDeleteResponse(message="User {user_id} deleted successfully")

"""
Collection Database Functions
"""
def create_collection(db: Session, collection: CollectionCreate) -> CollectionResponse:
    user = db.query(User).filter(User.id == collection.user_id).first()
    if not user:
        raise ValueError(f"User {collection.user_id} not found") 
    
    # Check if combination_id is provided and exists
    if collection.combination_id is not None:
        from app.models.combination import Combination
        combination = db.query(Combination).filter(Combination.id == collection.combination_id).first()
        if not combination:
            raise ValueError(f"Combination {collection.combination_id} not found")
    
    db_collection = Collection(
        user_id=collection.user_id, 
        name=collection.name, 
        description=collection.description,
        combination_id=collection.combination_id
    )
    db.add(db_collection)
    db.commit()
    db.refresh(db_collection)
    return CollectionResponse.model_validate(db_collection)

def get_all_collections(db: Session) -> CollectionListResponse:
    collections = db.query(Collection).all()
    return CollectionListResponse(collections=[
        CollectionResponse(
            id=col.id, 
            name=col.name, 
            description=col.description, 
            user_id=col.user_id,
            combination_id=col.combination_id
        ) for col in collections
    ])

def get_collections(db: Session, user_id: int) -> CollectionListResponse:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError(f"User {user_id} not found") 
    collections = db.query(Collection).where(Collection.user_id == user_id).all()
    return CollectionListResponse(collections=[
        CollectionResponse(
            id=col.id, 
            name=col.name, 
            description=col.description, 
            user_id=col.user_id,
            combination_id=col.combination_id
        ) for col in collections
    ])

def get_collection(db: Session, user_id: int, collection_id: int) -> CollectionResponse:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError(f"User {user_id} not found") 
    collection = db.query(Collection).filter(Collection.user_id == user_id, Collection.id == collection_id).first()
    if not collection:
        raise ValueError(f"Collection {collection_id} for User {user_id} not found") 
    return CollectionResponse.model_validate(collection)


def delete_collection(db: Session, user_id: int, collection_id: int) -> CollectionDeleteResponse:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError(f"User {user_id} not found") 
    collection = db.query(Collection).filter(Collection.user_id == user_id, Collection.id == collection_id).first()
    if not collection:
        raise ValueError(f"Collection {collection_id} not found") 
    db.delete(collection)
    db.commit()
    return UserDeleteResponse(message=f"Collection {collection_id} for User {user_id} deleted successfully")
    
def update_collection(db: Session, user_id: int, collection_id: int, new_collection: CollectionCreate) -> Collection:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError(f"User {user_id} not found") 
    collection = db.query(Collection).filter(Collection.user_id == user_id, Collection.id == collection_id).first()
    if not collection:
        raise ValueError(f"Collection {collection_id} not found") 
    for key, value in new_collection.model_dump(exclude_unset=True).items():
        setattr(collection, key, value)
    db.commit()
    db.refresh(collection)  # Refresh instance
    return CollectionResponse.model_validate(collection)

# Student CRUD operations
def create_student(db: Session, student: StudentCreate) -> StudentResponse:
    collection = db.query(Collection).filter(Collection.id == student.collection_id).first()
    if not collection:
        raise ValueError(f"Collection {student.collection_id} not found")
    
    db_student = Student(
        name=student.name,
        pid=student.pid,  # Add this line
        collection_id=student.collection_id
    )
    db.add(db_student)
    db.commit()
    db.refresh(db_student)
    return StudentResponse.model_validate(db_student)

def get_students_by_collection(db: Session, collection_id: int) -> StudentListResponse:
    students = db.query(Student).filter(Student.collection_id == collection_id).all()
    return StudentListResponse(students=[StudentResponse.model_validate(s) for s in students])

def get_student(db: Session, student_id: int) -> StudentResponse:
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise ValueError(f"Student {student_id} not found")
    return StudentResponse.model_validate(student)

def delete_student(db: Session, student_id: int) -> StudentDeleteResponse:
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise ValueError(f"Student {student_id} not found")
    db.delete(student)
    db.commit()
    return StudentDeleteResponse(message=f"Student {student_id} deleted successfully")

def update_student(db: Session, student_id: int, student_update: StudentCreate) -> StudentResponse:
    student = db.query(Student).filter(Student.id == student_id).first()
    if not student:
        raise ValueError(f"Student {student_id} not found")
    
    for key, value in student_update.model_dump(exclude_unset=True).items():
        setattr(student, key, value)
    
    db.commit()
    db.refresh(student)
    return StudentResponse.model_validate(student)

"""
Question Database Functions
"""
def create_question(db: Session, question: QuestionCreate) -> QuestionResponse:
    collection = db.query(Collection).filter(Collection.id == question.collection_id).first()
    if not collection:
        raise ValueError(f"Collection {question.collection_id} not found")
    
    db_question = Question(
        text=question.text,
        model_answer=question.model_answer,
        collection_id=question.collection_id
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return QuestionResponse.model_validate(db_question)

def get_questions_by_collection(db: Session, collection_id: int) -> QuestionListResponse:
    questions = db.query(Question).filter(Question.collection_id == collection_id).all()
    return QuestionListResponse(questions=[QuestionResponse.model_validate(q) for q in questions])

def get_question(db: Session, question_id: int) -> QuestionResponse:
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise ValueError(f"Question {question_id} not found")
    return QuestionResponse.model_validate(question)

def delete_question(db: Session, question_id: int) -> QuestionDeleteResponse:
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise ValueError(f"Question {question_id} not found")
    db.delete(question)
    db.commit()
    return QuestionDeleteResponse(message=f"Question {question_id} deleted successfully")

def update_question(db: Session, question_id: int, question_update: QuestionCreate) -> QuestionResponse:
    question = db.query(Question).filter(Question.id == question_id).first()
    if not question:
        raise ValueError(f"Question {question_id} not found")
    
    for key, value in question_update.model_dump(exclude_unset=True).items():
        setattr(question, key, value)
    
    db.commit()
    db.refresh(question)
    return QuestionResponse.model_validate(question)

"""
Student Answer Database Functions
"""
def create_student_answer(db: Session, student_answer: StudentAnswerCreate) -> StudentAnswerResponse:
    student = db.query(Student).filter(Student.id == student_answer.student_id).first()
    if not student:
        raise ValueError(f"Student {student_answer.student_id} not found")
    
    question = db.query(Question).filter(Question.id == student_answer.question_id).first()
    if not question:
        raise ValueError(f"Question {student_answer.question_id} not found")
    
    db_student_answer = StudentAnswer(
        answer=student_answer.answer,
        student_id=student_answer.student_id,
        question_id=student_answer.question_id
    )
    db.add(db_student_answer)
    db.commit()
    db.refresh(db_student_answer)
    return StudentAnswerResponse.model_validate(db_student_answer)

def get_student_answers_by_student(db: Session, student_id: int) -> StudentAnswerListResponse:
    student_answers = db.query(StudentAnswer).filter(StudentAnswer.student_id == student_id).all()
    return StudentAnswerListResponse(student_answers=[StudentAnswerResponse.model_validate(sa) for sa in student_answers])

def get_student_answers_by_question(db: Session, question_id: int) -> StudentAnswerListResponse:
    student_answers = db.query(StudentAnswer).filter(StudentAnswer.question_id == question_id).all()
    return StudentAnswerListResponse(student_answers=[StudentAnswerResponse.model_validate(sa) for sa in student_answers])

def get_student_answer(db: Session, student_answer_id: int) -> StudentAnswerResponse:
    student_answer = db.query(StudentAnswer).filter(StudentAnswer.id == student_answer_id).first()
    if not student_answer:
        raise ValueError(f"Student answer {student_answer_id} not found")
    return StudentAnswerResponse.model_validate(student_answer)

def delete_student_answer(db: Session, student_answer_id: int) -> StudentAnswerDeleteResponse:
    student_answer = db.query(StudentAnswer).filter(StudentAnswer.id == student_answer_id).first()
    if not student_answer:
        raise ValueError(f"Student answer {student_answer_id} not found")
    db.delete(student_answer)
    db.commit()
    return StudentAnswerDeleteResponse(message=f"Student answer {student_answer_id} deleted successfully")

def update_student_answer(db: Session, student_answer_id: int, student_answer_update: StudentAnswerCreate) -> StudentAnswerResponse:
    student_answer = db.query(StudentAnswer).filter(StudentAnswer.id == student_answer_id).first()
    if not student_answer:
        raise ValueError(f"Student answer {student_answer_id} not found")
    
    for key, value in student_answer_update.model_dump(exclude_unset=True).items():
        setattr(student_answer, key, value)
    
    db.commit()
    db.refresh(student_answer)
    return StudentAnswerResponse.model_validate(student_answer)

"""
LLM Response Database Functions
"""
def create_llm_response(db: Session, llm_response: LLMResponseCreate) -> LLMResponseResponse:
    student_answer = db.query(StudentAnswer).filter(StudentAnswer.id == llm_response.student_answer_id).first()
    if not student_answer:
        raise ValueError(f"Student answer {llm_response.student_answer_id} not found")
    
    db_llm_response = LLMResponse(
        raw_response=llm_response.raw_response,
        grade=llm_response.grade,
        feedback=llm_response.feedback,
        student_answer_id=llm_response.student_answer_id
    )
    db.add(db_llm_response)
    db.commit()
    db.refresh(db_llm_response)
    return LLMResponseResponse.model_validate(db_llm_response)

def get_llm_responses_by_student_answer(db: Session, student_answer_id: int) -> LLMResponseListResponse:
    llm_responses = db.query(LLMResponse).filter(LLMResponse.student_answer_id == student_answer_id).all()
    return LLMResponseListResponse(llm_responses=[LLMResponseResponse.model_validate(lr) for lr in llm_responses])

def get_latest_llm_response_by_student_answer(db: Session, student_answer_id: int) -> LLMResponseResponse:
    llm_response = db.query(LLMResponse).filter(
        LLMResponse.student_answer_id == student_answer_id
    ).order_by(LLMResponse.timestamp.desc()).first()
    
    if not llm_response:
        raise ValueError(f"No LLM response found for student answer {student_answer_id}")
    
    return LLMResponseResponse.model_validate(llm_response)
