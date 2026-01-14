"""
보안 관련 유틸리티
- JWT 토큰 생성/검증 (PyJWT 사용)
- 비밀번호 해싱/검증
"""
from datetime import datetime, timedelta, timezone
from typing import Any

import jwt
from jwt.exceptions import InvalidTokenError, ExpiredSignatureError, DecodeError
from passlib.context import CryptContext

from app.core.config import get_settings

settings = get_settings()
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    비밀번호 평문과 해시된 비밀번호 비교
    
    Args:
        plain_password: 평문 비밀번호
        hashed_password: 해시된 비밀번호
        
    Returns:
        bool: 비밀번호 일치 여부
    """
    return pwd_context.verify(plain_password, hashed_password)


def get_password_hash(password: str) -> str:
    """
    비밀번호 해싱
    
    Args:
        password: 평문 비밀번호
        
    Returns:
        str: 해시된 비밀번호
    """
    return pwd_context.hash(password)


def create_access_token(data: dict[str, Any], expires_delta: timedelta | None = None) -> str:
    """
    JWT 액세스 토큰 생성 (PyJWT 사용)
    
    Args:
        data: 토큰에 포함할 데이터 (payload)
        expires_delta: 토큰 만료 시간 (지정하지 않으면 설정값 사용)
        
    Returns:
        str: 생성된 JWT 토큰
        
    Example:
        >>> token = create_access_token({"sub": "user@example.com", "user_id": 123})
        >>> token = create_access_token({"sub": "user@example.com"}, expires_delta=timedelta(hours=1))
    """
    to_encode = data.copy()
    
    # 만료 시간 설정
    if expires_delta:
        expire = datetime.now(timezone.utc) + expires_delta
    else:
        expire = datetime.now(timezone.utc) + timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    
    # JWT 표준 클레임 추가
    to_encode.update({
        "exp": expire,  # expiration time
        "iat": datetime.now(timezone.utc)  # issued at
    })
    
    # PyJWT를 사용한 토큰 인코딩
    encoded_jwt = jwt.encode(
        to_encode, 
        settings.SECRET_KEY, 
        algorithm=settings.ALGORITHM
    )
    
    return encoded_jwt


def decode_access_token(token: str) -> dict[str, Any] | None:
    """
    JWT 액세스 토큰 디코딩 및 검증 (PyJWT 사용)
    
    Args:
        token: 검증할 JWT 토큰
        
    Returns:
        dict[str, Any] | None: 디코딩된 payload 또는 None (검증 실패 시)
        
    Example:
        >>> payload = decode_access_token(token)
        >>> if payload:
        >>>     user_id = payload.get("user_id")
        >>>     email = payload.get("sub")
    """
    try:
        # PyJWT를 사용한 토큰 디코딩 및 검증
        payload = jwt.decode(
            token, 
            settings.SECRET_KEY, 
            algorithms=[settings.ALGORITHM]
        )
        return payload
    except ExpiredSignatureError:
        # 토큰 만료
        return None
    except DecodeError:
        # 토큰 디코딩 실패 (잘못된 형식)
        return None
    except InvalidTokenError:
        # 기타 토큰 검증 실패
        return None