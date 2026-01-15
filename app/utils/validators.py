"""
입력 검증 유틸리티
"""
import re
from typing import Optional


def validate_password(password: str) -> tuple[bool, Optional[str]]:
    """
    비밀번호 검증
    - 최소 8자 이상
    - 영문과 숫자 조합
    
    Args:
        password: 검증할 비밀번호
    
    Returns:
        tuple[bool, Optional[str]]: (유효성, 에러 메시지)
    """
    if len(password) < 8:
        return False, "Password must be at least 8 characters long"
    
    # 영문과 숫자 포함 확인
    has_letter = bool(re.search(r'[a-zA-Z]', password))
    has_digit = bool(re.search(r'\d', password))
    
    if not (has_letter and has_digit):
        return False, "Password must contain both letters and numbers"
    
    return True, None


def validate_nickname(nickname: str) -> tuple[bool, Optional[str]]:
    """
    닉네임 검증
    - 2자 이상 20자 이하
    
    Args:
        nickname: 검증할 닉네임
    
    Returns:
        tuple[bool, Optional[str]]: (유효성, 에러 메시지)
    """
    if len(nickname) < 2:
        return False, "Nickname must be at least 2 characters long"
    
    if len(nickname) > 20:
        return False, "Nickname must be at most 20 characters long"
    
    return True, None


def validate_post_title(title: str) -> tuple[bool, Optional[str]]:
    """
    게시글 제목 검증
    - 1자 이상 200자 이하
    
    Args:
        title: 검증할 제목
    
    Returns:
        tuple[bool, Optional[str]]: (유효성, 에러 메시지)
    """
    if len(title) < 1:
        return False, "Title cannot be empty"
    
    if len(title) > 200:
        return False, "Title must be at most 200 characters long"
    
    return True, None


def validate_post_content(content: str) -> tuple[bool, Optional[str]]:
    """
    게시글 내용 검증
    - 1자 이상 10000자 이하
    
    Args:
        content: 검증할 내용
    
    Returns:
        tuple[bool, Optional[str]]: (유효성, 에러 메시지)
    """
    if len(content) < 1:
        return False, "Content cannot be empty"
    
    if len(content) > 10000:
        return False, "Content must be at most 10000 characters long"
    
    return True, None


def validate_comment_content(content: str) -> tuple[bool, Optional[str]]:
    """
    댓글 내용 검증
    - 1자 이상 500자 이하
    
    Args:
        content: 검증할 내용
    
    Returns:
        tuple[bool, Optional[str]]: (유효성, 에러 메시지)
    """
    if len(content) < 1:
        return False, "Comment cannot be empty"
    
    if len(content) > 500:
        return False, "Comment must be at most 500 characters long"
    
    return True, None