from sqlalchemy.orm import Session
from app.models.user import User
from app.models.collection import Collection
from app.schemas.user_schema import UserCreate, UserResponse, UserListResponse, UserDeleteResponse
from app.schemas.collection_schema import CollectionCreate, CollectionResponse, CollectionListResponse, CollectionDeleteResponse


"""
User Database Functions
"""
def create_user(db: Session, user: UserCreate) -> User:
    db_user = User(username=user.username, password=user.password)
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
        raise ValueError("User not found") 
    return UserResponse(id=user.id, username=user.username, password=user.password)

def delete_user(db: Session, user_id: int) -> UserDeleteResponse:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User not found") 
    db.delete(user)
    db.commit()
    return UserDeleteResponse(message="User deleted successfully")

"""
Collection Database Functions
"""
def create_collection(db: Session, collection: CollectionCreate) -> Collection:
    db_collection = Collection(user_id=collection.user_id, name=collection.name, description=collection.description)
    db.add(db_collection)
    db.commit()
    db.refresh(db_collection)
    return db_collection

def get_collections(db: Session, user_id: int) -> CollectionListResponse:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User not found") 
    collections = db.query(Collection).where(Collection.user_id == user_id).all()
    return CollectionListResponse(collections=[CollectionResponse(id=col.id, name=col.name, description=col.description, user_id=col.user_id) for col in collections])

def get_collection(db: Session, user_id: int, collection_id) -> CollectionResponse:
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise ValueError("User not found") 
    collection = db.query(Collection).filter(Collection.user_id == user_id, Collection.id == collection_id).first()
    if not collection:
        raise ValueError("Collection not found") 
    return CollectionResponse(id = collection.id, name = collection.name, description=collection.description, user_id = collection.user_id)