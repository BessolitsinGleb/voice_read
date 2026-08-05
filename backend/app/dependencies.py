from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException
from .services.auth_service import AuthService
from .core import sequrity
from .database import get_db
from .repositories.user_repos import UserRepo
from fastapi.security import OAuth2PasswordBearer
from .core.config import Settings
from .models import Users
from jose import jwt 

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/reg/login")

async def get_current_user(token: str = Depends(oauth2_scheme), db: AsyncSession = Depends(get_db)):
    try:
        payload = jwt.decode(token, Settings.SECRET_KEY, algorithms=[Settings.JWT_ALGO])
        user_id: str = payload.get("sub")
        if user_id is None:
            raise HTTPException(status_code=401)
    except:
        raise HTTPException(status_code=401)

    user = await db.get(Users, int(user_id))
    return user

async def get_auth_service(db: AsyncSession = Depends(get_db)):
    repo = UserRepo(db)
    return AuthService(repo, security= sequrity)