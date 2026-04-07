from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from ..logging_config import logger
from ..database import get_db
from .. import models, schemas
from ..auth_utils import generate_hash, check_hash, build_token

router = APIRouter(prefix="/auth", tags=["Authentication"])


#  REGISTER
@router.post("/register")
def register_user(data: schemas.UserRegister, db: Session = Depends(get_db)):
    try:
        existing_user = db.query(models.User).filter(
            models.User.username == data.username
        ).first()

        if existing_user:
            raise HTTPException(status_code=400, detail="Username already exists")

        new_user = models.User(
            username=data.username,
            password=generate_hash(data.password),
            role="user",
        )

        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        logger.info(f"User registered: id={new_user.id}, username={new_user.username}")
        return {"message": "User registered successfully"}



    except Exception as e:

        db.rollback()

        logger.exception("Registration failed")

        raise HTTPException(status_code=500, detail=str(e))


#  LOGIN
@router.post("/login")
def login_user(data: schemas.UserLogin, db: Session = Depends(get_db)):
    user = db.query(models.User).filter(
        models.User.username == data.username
    ).first()

    if not user or not check_hash(data.password, user.password):
        raise HTTPException(status_code=401, detail="Invalid credentials")

    token = build_token({
        "user_id": user.id,
        "role": user.role
    }
    )
    logger.info(f"User logged in: id={user.id}, username={user.username}")

    return {
        "access_token": token,
        "token_type": "bearer"
    }



# test
@router.get("/test")
def test_auth():
    return {"message": "Auth route working"}


