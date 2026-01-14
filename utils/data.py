import json
from typing import Any, Optional
from pathlib import Path

# 프로젝트 루트 디렉토리 경로
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"


def ensure_data_dir():
    """data 디렉토리가 없으면 생성"""
    if not DATA_DIR.exists():
        DATA_DIR.mkdir(exist_ok=True)


def load_data(filename: str) -> list[Any]:
    """JSON 파일에서 데이터 로드"""
    ensure_data_dir()
    filepath = DATA_DIR / filename

    # 파일이 없으면 빈 리스트 반환
    if not filepath.exists():
        return []

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            return json.load(f)
    except json.JSONDecodeError:
        # JSON 파싱 에러 시 빈 리스트 반환
        return []
    except Exception as e:
        print(f"Error loading {filename}: {e}")
        return []


def save_data(data: list[Any], filename: str) -> bool:
    """JSON 파일에 데이터 저장"""
    ensure_data_dir()
    filepath = DATA_DIR / filename

    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, ensure_ascii=False, indent=2)
        return True
    except Exception as e:
        print(f"Error saving {filename}: {e}")
        return False


def get_next_id(filename: str) -> int:
    """다음 ID 값 생성"""
    data = load_data(filename)
    if not data:
        return 1

    # 가장 큰 ID 값 + 1 반환
    max_id = max(item.get("id", 0) for item in data)
    return max_id + 1


def find_by_id(filename: str, item_id: int) -> Optional[dict]:
    """ID로 아이템 찾기"""
    data = load_data(filename)
    for item in data:
        if item.get("id") == item_id:
            return item
    return None


def find_by_field(filename: str, field: str, value: Any) -> Optional[dict]:
    """특정 필드 값으로 아이템 찾기"""
    data = load_data(filename)
    for item in data:
        if item.get(field) == value:
            return item
    return None


def update_by_id(filename: str, item_id: int, updates: dict) -> bool:
    """ID로 아이템 업데이트"""
    data = load_data(filename)
    for i, item in enumerate(data):
        if item.get("id") == item_id:
            data[i].update(updates)
            return save_data(data, filename)
    return False


def delete_by_id(filename: str, item_id: int) -> bool:
    """ID로 아이템 삭제"""
    data = load_data(filename)
    original_length = len(data)
    data = [item for item in data if item.get("id") != item_id]

    if len(data) < original_length:
        return save_data(data, filename)
    return False