import json
import os
import threading
from dotenv import load_dotenv

#----- 코드리뷰 반영, 안전한 파일 경로 생성 ----------------------------
def path_check(base_dir: str, filename: str) -> str:
    # 상위 경로 받아와서 파일 이름 붙여서 반환
    base_dir_real = os.path.realpath(base_dir)
    target_path = os.path.realpath(os.path.join(base_dir_real, filename))
    # base_dir 이 아니면 에러 반환
    if os.path.commonpath([base_dir_real, target_path]) != base_dir_real:
        raise ValueError(f"파일 경로가 이상합니다. : {filename}")
    return target_path

#---- .env 참조, json 파일 Path 지정
load_dotenv()
DATA_DIR = os.getenv("DATA_DIR", "data")
users_json_path = path_check(DATA_DIR, os.getenv("USERS_JSON", "users.json"))
posts_json_path = path_check(DATA_DIR, os.getenv("POSTS_JSON", "posts.json"))
comments_json_path = path_check(DATA_DIR, os.getenv("COMMENTS_JSON", "comments.json"))
likes_json_path = path_check(DATA_DIR, os.getenv("LIKES_JSON", "likes.json"))

#----- 코드리뷰 반영, threading.lock 활용---------------------------
users_file_lock = threading.Lock()
posts_file_lock = threading.Lock()
likes_file_lock = threading.Lock()
comments_file_lock = threading.Lock()

#----- users.json 불러오기 -------------------------------------------
def load_users():
    # 디렉토리 유무 확인 (없으면 mkdir)
    os.makedirs(DATA_DIR, exist_ok=True)
    temp_path = users_json_path + ".tmp"
    # 코드리뷰 반영
    with users_file_lock:
        try:
            with open(users_json_path, "r", encoding="utf-8") as f:
                #코드 리뷰 반영 -- Race Condition
                data = json.load(f, ensure_ascii=False, indent=4)
                f.flush()
                os.fsync(f.fileno())
                return data if isinstance(data, list) else []
        except FileNotFoundError:
            # 파일이 없으면 생성
            with open(users_json_path, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)
            return []
        except json.JSONDecodeError:
            # 파일이 깨졌으면 초기화
            with open(users_json_path, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)
            return []
#----- users.json 저장하기 -------------------------------------------
def save_users(users: list):
    # 디렉토리 유무 확인 (없으면 mkdir)
    os.makedirs(DATA_DIR, exist_ok=True)
    temp_path = users_json_path + ".tmp"
    # 코드리뷰 반영
    with users_file_lock:
        with open(users_json_path, "w", encoding="utf-8") as f:
            json.dump(users, f, ensure_ascii=False, indent=4)
            f.flush()
            os.fsync(f.fileno())  # 디스크에 강제 반영
        os.replace(temp_path, users_json_path)
        os.chmod(users_json_path, 0o600) # 코드리뷰 반영 -- 소유자만 읽기 쓰기 가능

#----- DB에서 user_id를 활용하여 사용자 찾기(코드 리뷰 반영) ---------
def find_user_by_id(user_id: str) -> dict | None:
    users_json_path = load_users()
    for user in users_json_path:
        if user["user_id"] == user_id:
            return user
    return None
#----- DB에서 email_address를 활용하여 사용자 찾기(코드 리뷰 반영) ---------
def find_user_by_email(email: str) -> dict | None:
    users_json_path = load_users()
    for user in users_json_path:
        if user["email_address"] == email:
            return user
    return None
#---- user id 카운터값 1씩 증가, 무결성 검증 try except 추가
def generate_user_id():
    users_json_path = load_users()
    max_id = 0
    for user in users_json_path:
        try:
            user_id = user["user_id"]
            number = int(user_id.split("_")[1])
            max_id = max(max_id, number)
        except (KeyError, IndexError, ValueError, TypeError):
            continue
    return f"user_{max_id + 1}"

#----- posts.json 불러오기 -------------------------------------------
def load_posts():
    # 디렉토리 유무 확인 (없으면 mkdir)
    os.makedirs(DATA_DIR, exist_ok=True)
    # 코드리뷰 반영
    with posts_file_lock:
        try:
            with open(posts_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except FileNotFoundError:
            # 파일이 없으면 생성
            with open(posts_json_path, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)
            return []
        except json.JSONDecodeError:
            # 파일이 깨졌으면 초기화
            with open(posts_json_path, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)
            return []
#----- posts.json 저장하기 -------------------------------------------
def save_posts(posts: list):
    # 디렉토리 유무 확인 (없으면 mkdir)
    os.makedirs(DATA_DIR, exist_ok=True)
    temp_path = posts_json_path + ".tmp"
    # 코드리뷰 반영
    with posts_file_lock:
        with open(posts_json_path, "w", encoding="utf-8") as f:
            json.dump(posts, f, ensure_ascii=False, indent=4)
            f.flush()
            os.fsync(f.fileno())  # 디스크에 강제 반영
        os.replace(temp_path, posts_json_path)

#---- post_id 카운터값 1씩 증가, try except 코드 리뷰 반영
def generate_post_id():
    posts_json_path = load_posts()
    max_id = 0
    for post in posts_json_path:
        try:
            post_id = post["post_id"]
            number = int(post_id.split("_")[1])
            max_id = max(max_id, number)
        except (KeyError, IndexError, ValueError, TypeError):
            continue
    return f"post_{max_id + 1}"

#----- comments.json 불러오기 -------------------------------------------
def load_comments():
    # 디렉토리 유무 확인 (없으면 mkdir)
    os.makedirs(DATA_DIR, exist_ok=True)
    with comments_file_lock:
        try:
            with open(comments_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except FileNotFoundError:
            # 파일이 없으면 생성
            with open(comments_json_path, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)
            return []
        except json.JSONDecodeError:
            # 파일이 깨졌으면 초기화
            with open(comments_json_path, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)
            return []
#----- comments.json 저장하기 -------------------------------------------
def save_comments(comments: list):
    # 디렉토리 유무 확인 (없으면 mkdir)
    os.makedirs(DATA_DIR, exist_ok=True)
    temp_path = comments_json_path + ".tmp"
    # 코드리뷰 반영
    with comments_file_lock:
        with open(comments_json_path, "w", encoding="utf-8") as f:
            json.dump(comments, f, ensure_ascii=False, indent=4)
            f.flush()
            os.fsync(f.fileno())  # 디스크에 강제 반영
        os.replace(temp_path, comments_json_path)

#----- likes.json 불러오기 -------------------------------------------
def load_likes():
    # 디렉토리 유무 확인 (없으면 mkdir)
    os.makedirs(DATA_DIR, exist_ok=True)
    with likes_file_lock:
        try:
            with open(likes_json_path, "r", encoding="utf-8") as f:
                data = json.load(f)
                return data if isinstance(data, list) else []
        except FileNotFoundError:
            # 파일이 없으면 생성
            with open(likes_json_path, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)
            return []
        except json.JSONDecodeError:
            # 파일이 깨졌으면 초기화
            with open(likes_json_path, "w", encoding="utf-8") as f:
                json.dump([], f, ensure_ascii=False, indent=4)
            return []
#----- posts.json 저장하기 -------------------------------------------
def save_likes(likes: list):
    # 디렉토리 유무 확인 (없으면 mkdir)
    os.makedirs(DATA_DIR, exist_ok=True)
    temp_path = likes_json_path + ".tmp"
    # 코드리뷰 반영
    with likes_file_lock:
        with open(likes_json_path, "w", encoding="utf-8") as f:
            json.dump(likes, f, ensure_ascii=False, indent=4)
            f.flush()
            os.fsync(f.fileno())  # 디스크에 강제 반영
        os.replace(temp_path, likes_json_path)

#---- comment_id 카운터값 증가 로직 (post_id 로직과 동일함)
def generate_comment_id():
    comments = load_comments()
    max_id = 0
    for comment in comments:
        try:
            c_id = comment["comment_id"]
            number = int(c_id.split("_")[1])
            max_id = max(max_id, number)
        except (KeyError, IndexError, ValueError, TypeError):
            continue
    return f"comment_{max_id + 1}"

#---- 좋아요, 댓글 카운트 수 확인
def get_counts(post_id: str):
    likes = load_likes()
    comments = load_comments()
    likes_count = len([l for l in likes if l["post_id"] == post_id])
    comments_count = len([c for c in comments if c["post_id"] == post_id])
    return likes_count, comments_count