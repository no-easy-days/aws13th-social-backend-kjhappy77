"""
ID 생성 유틸리티
- int 기반 auto-increment ID 생성
- filelock을 사용하여 Windows/Mac/Linux 모두 지원
"""
import json
import os
from typing import Literal
from filelock import FileLock, Timeout


EntityType = Literal["user", "post", "comment"]


class IDCounter:
    """
    ID 카운터 관리 클래스
    """
    
    def __init__(self, data_dir: str = "./data") -> None:
        """
        Args:
            data_dir: 데이터 디렉토리 경로
        """
        self.data_dir = data_dir
        self.counters_file = os.path.join(data_dir, "_counters.json")
        self.lock_file = os.path.join(data_dir, "_counters.json.lock")
        self._ensure_file_exists()
    
    def _ensure_file_exists(self) -> None:
        """프로그램 첫 실행 시 데이터 폴더와 초기 카운터 파일(0으로 설정된 상태)을 자동으로 만듦       
        """
        """
        접근제어 : 클래스 외부나 모듈 외부에서 해당 함수를 직접 호출하는 것을 권장하지 않음
        내부 초기화 로직을 숨김
        """
        os.makedirs(self.data_dir, exist_ok=True)
        lock = FileLock(self.lock_path, timeout=10)
        try:
            with lock:
                if not os.path.exists(self.counters_file):
                    initial_counters = {
                        "user_id": 0,
                        "post_id": 0,
                        "comment_id": 0
                    }
                    with open(self.counters_file, 'w', encoding='utf-8') as f:
                        json.dump(initial_counters, f, indent=2)
        except Timeout:
            raise TimeoutError("ID 카운터 파일 접근 권한을 얻지 못했습니다.")
    
    def get_next_id(self, entity_type: EntityType) -> int:
        """
        다음 ID 생성 (auto-increment)
        
        Args: ## 어떤 종류의 id를 생성할지 결정함
            entity_type: 엔티티 타입 ("user", "post", "comment")
        
        Returns: # 새로운 id를 반환함
            int: 다음 ID (1부터 시작)
        """
        counter_key = f"{entity_type}_id"
        
        # filelock을 사용한 파일 락
        lock = FileLock(self.lock_file, timeout=10)
        
        with lock:
            # 현재 카운터 읽기
            with open(self.counters_file, 'r', encoding='utf-8') as f:
                counters = json.load(f)
            
            # 카운터 증가
            counters[counter_key] += 1
            next_id = counters[counter_key]
            
            # 파일에 다시 쓰기
            with open(self.counters_file, 'w', encoding='utf-8') as f:
                json.dump(counters, f, indent=2)
            
            return next_id
    
    def reset_counter(self, entity_type: EntityType, value: int = 0) -> None:
        """
        카운터 리셋 (테스트용)
        
        Args:
            entity_type: 엔티티 타입
            value: 리셋할 값 (기본값: 0)
        """
        counter_key = f"{entity_type}_id"
        
        lock = FileLock(self.lock_file, timeout=10)
        
        with lock:
            with open(self.counters_file, 'r', encoding='utf-8') as f:
                counters = json.load(f)
            
            counters[counter_key] = value
            
            with open(self.counters_file, 'w', encoding='utf-8') as f:
                json.dump(counters, f, indent=2)


# 싱글톤 인스턴스
_id_counter: IDCounter | None = None


def get_id_counter(data_dir: str = "./data") -> IDCounter:
    """
    IDCounter 싱글톤 인스턴스 반환
    
    Args:
        data_dir: 데이터 디렉토리 경로
    
    Returns:
        IDCounter: ID 카운터 인스턴스
    """
    global _id_counter
    if _id_counter is None:
        _id_counter = IDCounter(data_dir)
    return _id_counter


def generate_user_id(data_dir: str = "./data") -> int:
    """
    User ID 생성
    
    Args:
        data_dir: 데이터 디렉토리 경로
    
    Returns:
        int: 생성된 user ID (1, 2, 3, ...)
    """
    counter = get_id_counter(data_dir)
    return counter.get_next_id("user")


def generate_post_id(data_dir: str = "./data") -> int:
    """
    Post ID 생성
    
    Args:
        data_dir: 데이터 디렉토리 경로
    
    Returns:
        int: 생성된 post ID (1, 2, 3, ...)
    """
    counter = get_id_counter(data_dir)
    return counter.get_next_id("post")


def generate_comment_id(data_dir: str = "./data") -> int:
    """
    Comment ID 생성
    
    Args:
        data_dir: 데이터 디렉토리 경로
    
    Returns:
        int: 생성된 comment ID (1, 2, 3, ...)
    """
    counter = get_id_counter(data_dir)
    return counter.get_next_id("comment")