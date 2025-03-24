# app/database/crud.py
from sqlalchemy.orm import Session
from app.models.user import User
from app.models.collection import Collection
from app.models.student import Student  # Add this import
from app.schemas.user_schema import UserCreate, UserResponse, UserListResponse, UserDeleteResponse
from app.schemas.collection_schema import CollectionCreate, CollectionResponse, CollectionListResponse, CollectionDeleteResponse
from app.schemas.student_schema import StudentCreate, StudentResponse, StudentListResponse, StudentDeleteResponse  # Add this import
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
    db_collection = Collection(user_id=collection.user_id, name=collection.name, description=collection.description)
    db.add(db_collection)
    db.commit()
    db.refresh(db_collection)
    return CollectionResponse.model_validate(db_collection)

def get_all_collections(db: Session) -> CollectionListResponse:
    collections = db.query(Collection).all()
    return CollectionListResponse(collections=[CollectionResponse(id=col.id, name=col.name, description=col.description, user_id=col.user_id) for col in collections])

def get_collections(db: Session, user_id: int) -> CollectionListResponse:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError(f"User {user_id} not found") 
    collections = db.query(Collection).where(Collection.user_id == user_id).all()
    return CollectionListResponse(collections=[CollectionResponse(id=col.id, name=col.name, description=col.description, user_id=col.user_id) for col in collections])

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
        answer=student.answer,
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