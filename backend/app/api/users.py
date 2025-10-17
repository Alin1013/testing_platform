from fastapi import APIRouter, Depends, HTTPException, status, UploadFile, File
from sqlalchemy.orm import Session
from app.database import get_db
from app.models.user import UserInfo
from app.schemas import UserCreate, UserLogin, UserUpdate, UserResponse, Token
from app.auth import get_password_hash, verify_password, create_access_token, get_current_user
import os
import shutil

router = APIRouter()


@router.post("/register", response_model=UserResponse)
def register(user: UserCreate, db: Session = Depends(get_db)):
    # 检查用户名是否已存在
    db_user = db.query(UserInfo).filter(UserInfo.username == user.username).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")

    # 密码验证
    if len(user.password) < 8 or not any(c.isalpha() for c in user.password):
        raise HTTPException(
            status_code=400,
            detail="Password must be at least 8 characters long and contain letters"
        )

    # 创建用户
    hashed_password = get_password_hash(user.password)
    db_user = UserInfo(
        username=user.username,
        password_hash=hashed_password,
        avatar_path="default_avatar.png"
    )
    db.add(db_user)
    db.commit()
    db.refresh(db_user)
    return db_user


@router.post("/login", response_model=Token)
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(UserInfo).filter(UserInfo.username == user.username).first()
    if not db_user or not verify_password(user.password, db_user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
        )

    access_token = create_access_token(data={"sub": db_user.username})
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": UserResponse.from_orm(db_user)
    }


@router.get("/users/me", response_model=UserResponse)
def read_users_me(current_user: UserInfo = Depends(get_current_user)):
    return current_user


@router.put("/users/me", response_model=UserResponse)
def update_user(
        user_update: UserUpdate,
        current_user: UserInfo = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    if user_update.username:
        current_user.username = user_update.username

    if user_update.password:
        if len(user_update.password) < 8 or not any(c.isalpha() for c in user_update.password):
            raise HTTPException(
                status_code=400,
                detail="Password must be at least 8 characters long and contain letters"
            )
        current_user.password_hash = get_password_hash(user_update.password)

    db.commit()
    db.refresh(current_user)
    return current_user


@router.post("/users/me/avatar")
def upload_avatar(
        file: UploadFile = File(...),
        current_user: UserInfo = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    # 创建头像目录
    avatar_dir = "static/avatars"
    os.makedirs(avatar_dir, exist_ok=True)

    # 生成文件名
    file_extension = file.filename.split('.')[-1]
    filename = f"avatar_{current_user.id}.{file_extension}"
    file_path = os.path.join(avatar_dir, filename)

    # 保存文件
    with open(file_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    # 更新数据库
    current_user.avatar_path = filename
    db.commit()

    return {"filename": filename, "message": "Avatar uploaded successfully"}


@router.delete("/users/me")
def delete_user(
        current_user: UserInfo = Depends(get_current_user),
        db: Session = Depends(get_db)
):
    # 注销账号（软删除）
    current_user.is_active = False
    db.commit()
    return {"message": "User account deactivated successfully"}