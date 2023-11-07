from fastapi import  HTTPException, Depends

from app.exceptions.exceptions import UserIntegrityException
from app.models import get_db
from sqlalchemy.orm import Session
from app.models.user import User
from app.schema.user import UserCreate, UserUpdate, UserResponse
from fastapi import APIRouter

router = APIRouter(prefix="/user")

@router.get("/")
def get_all_users(db: Session = Depends(get_db)):
    return db.query(User).all()


@router.get("/{user_id}")
def get_user_by_email(user_id: int, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == user_id).first()
    if user:
        return user
    raise HTTPException(status_code=404, detail="User not found")


@router.post("/", response_model=UserResponse)
def create_user(user: UserCreate, db: Session = Depends(get_db)):
    try:
        db_user = User(email=user.email, pwd=user.pwd, authorizations=user.authorizations)
        db.add(db_user)
        db.commit()
        db.refresh(db_user)
    except:
        raise(UserIntegrityException)
    return db_user


@router.patch("/{user_id}")
def update_user_by_email(user_id: int, user: UserUpdate, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db_user.name = user.name
    db_user.email = user.email
    db.commit()
    return {"message": "User updated successfully"}


@router.delete("/{user_id}")
def delete_user_by_email(user_id: int, db: Session = Depends(get_db)):
    db_user = db.query(User).filter(User.id == user_id).first()
    if not db_user:
        raise HTTPException(status_code=404, detail="User not found")
    db.delete(db_user)
    db.commit()
    return {"message": "User deleted successfully"}
