import json
import os
from dotenv import load_dotenv

#---- .env 참조, json 파일 Path 지정
load_dotenv()
DATA_DIR = os.getenv("DATA_DIR", "data")
users_json = os.path.join(DATA_DIR, os.getenv("USERS_JSON", "users.json"))
posts_json = os.path.join(DATA_DIR, os.getenv("POSTS_JSON", "posts.json"))
comments_json = os.path.join(DATA_DIR, os.getenv("COMMENTS_JSON", "comments.json"))
likes_json = os.path.join(DATA_DIR, os.getenv("LIKES_JSON", "likes.json"))

#----- users.json 불러오기 -------------------------------------------
def load_users():
    # json 안에 아무 정보가 없는 경우 만들어주기
    if not os.path.exists(users_json):
        with open(users_json, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)
        return []
    with open(users_json, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                return []
        # 파일 불러 왔는데 뭔가 깨졌거나 이상한 경우 새로 만들어주기
        except json.JSONDecodeError:
            with open(users_json, "w", encoding="utf-8") as fw:
                json.dump([], fw, ensure_ascii=False, indent=4)
            return []
#----- users.json 저장하기 -------------------------------------------
def save_users(users: list):
    with open(users_json, "w", encoding="utf-8") as f:
        json.dump(users, f, ensure_ascii=False, indent=4)

#----- DB에서 user_id를 활용하여 사용자 찾기(코드 리뷰 반영) ---------
def find_user_by_id(user_id: str) -> dict | None:
    users_json = load_users()
    for user in users_json:
        if user["user_id"] == user_id:
            return user
    return None
#----- DB에서 email_address를 활용하여 사용자 찾기(코드 리뷰 반영) ---------
def find_user_by_email(email: str) -> dict | None:
    users_json = load_users()
    for user in users_json:
        if user["email_address"] == email:
            return user
    return None
#---- user id 카운터값 1씩 증가
def generate_user_id():
    users_json = load_users()
    if not users_json:
        return "user_1"
    user_id_counter = max(int(user["user_id"].split("_")[1]) for user in users_json)
    return f"user_{user_id_counter + 1}"

#----- posts.json 불러오기 -------------------------------------------
def load_posts():
    # json 안에 아무 정보가 없는 경우 만들어주기
    if not os.path.exists(posts_json):
        with open(posts_json, "w", encoding="utf-8") as f:
            json.dump([], f, ensure_ascii=False, indent=4)
        return []
    with open(posts_json, "r", encoding="utf-8") as f:
        try:
            data = json.load(f)
            if isinstance(data, list):
                return data
            else:
                return []
        # 파일 불러 왔는데 뭔가 깨졌거나 이상한 경우 새로 만들어주기
        except json.JSONDecodeError:
            with open(posts_json, "w", encoding="utf-8") as fw:
                json.dump([], fw, ensure_ascii=False, indent=4)
            return []
#----- posts.json 저장하기 -------------------------------------------
def save_posts(posts: list):
    with open(posts_json, "w", encoding="utf-8") as f:
        json.dump(posts, f, ensure_ascii=False, indent=4)
#---- post_id 카운터값 1씩 증가
def generate_post_id():
    posts_json = load_posts()
    if not posts_json:
        return "post_1"
    user_id_counter = max(int(post["post_id"].split("_")[1]) for post in posts_json)
    return f"post_{user_id_counter + 1}"
