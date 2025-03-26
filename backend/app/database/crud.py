from sqlalchemy.orm import Session
from app.models.user import User
from app.models.collection import Collection
from app.models.question import Question
from app.schemas.user_schema import UserCreate, UserResponse, UserListResponse, UserDeleteResponse
from app.schemas.collection_schema import CollectionCreate, CollectionResponse, CollectionListResponse, CollectionDeleteResponse
from app.schemas.question_schema import QuestionCreate, QuestionResponse, QuestionListResponse, QuestionDeleteResponse
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
    return CollectionListResponse(collections=[
        CollectionResponse(
            id=col.id, 
            name=col.name, 
            description=col.description, 
            user_id=col.user_id,
            created_at=col.created_at
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
            created_at=col.created_at
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
    return CollectionDeleteResponse(message=f"Collection {collection_id} for User {user_id} deleted successfully")
    
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

"""
Question Database Functions
"""
def create_question(db: Session, question: QuestionCreate) -> QuestionResponse:
    # Verify collection exists
    collection = db.query(Collection).filter(Collection.id == question.collection_id).first()
    if not collection:
        raise ValueError(f"Collection {question.collection_id} not found")
    
    db_question = Question(
        collection_id=question.collection_id,
        question_text=question.question_text,
        example_answer=question.example_answer
    )
    db.add(db_question)
    db.commit()
    db.refresh(db_question)
    return QuestionResponse.model_validate(db_question)

def get_questions(db: Session, collection_id: int) -> QuestionListResponse:
    # Verify collection exists
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if not collection:
        raise ValueError(f"Collection {collection_id} not found")
    
    questions = db.query(Question).filter(Question.collection_id == collection_id).all()
    return QuestionListResponse(questions=[
        QuestionResponse(
            id=q.id,
            collection_id=q.collection_id,
            question_text=q.question_text,
            example_answer=q.example_answer
        ) for q in questions
    ])

def get_question(db: Session, collection_id: int, question_id: int) -> QuestionResponse:
    # Verify collection exists
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if not collection:
        raise ValueError(f"Collection {collection_id} not found")
    
    question = db.query(Question).filter(
        Question.collection_id == collection_id,
        Question.id == question_id
    ).first()
    
    if not question:
        raise ValueError(f"Question {question_id} not found in Collection {collection_id}")
    
    return QuestionResponse.model_validate(question)

def update_question(db: Session, collection_id: int, question_id: int, new_question: QuestionCreate) -> QuestionResponse:
    # Verify collection exists
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if not collection:
        raise ValueError(f"Collection {collection_id} not found")
    
    question = db.query(Question).filter(
        Question.collection_id == collection_id,
        Question.id == question_id
    ).first()
    
    if not question:
        raise ValueError(f"Question {question_id} not found in Collection {collection_id}")
    
    for key, value in new_question.model_dump(exclude_unset=True).items():
        setattr(question, key, value)
    
    db.commit()
    db.refresh(question)
    return QuestionResponse.model_validate(question)

def delete_question(db: Session, collection_id: int, question_id: int) -> QuestionDeleteResponse:
    # Verify collection exists
    collection = db.query(Collection).filter(Collection.id == collection_id).first()
    if not collection:
        raise ValueError(f"Collection {collection_id} not found")
    
    question = db.query(Question).filter(
        Question.collection_id == collection_id,
        Question.id == question_id
    ).first()
    
    if not question:
        raise ValueError(f"Question {question_id} not found in Collection {collection_id}")
    
    db.delete(question)
    db.commit()
    return QuestionDeleteResponse(message=f"Question {question_id} deleted successfully from Collection {collection_id}")
