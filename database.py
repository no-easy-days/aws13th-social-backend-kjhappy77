#----- 데모용 DB, 리스트 형태로 우선 선언, 추후 실제 DB 연동 예정 ------------
demo_db = []

#----- DB에서 user_id를 활용하여 사용자 찾기(코드 리뷰 반영) ---------
def find_user_by_id(user_id: str) -> dict | None:
    for user in demo_db:
        if user["user_id"] == user_id:
            return user
    return None

#----- DB에서 email_address를 활용하여 사용자 찾기(코드 리뷰 반영) ---------
def find_user_by_email(email: str) -> dict | None:
    for user in demo_db:
        if user["email_address"] == email:
            return user
    return None

#----- user_id 부여 (추후 DB 확장성 고려, 함수 형태로 구현) --------------
user_counter = 0
def generate_user_id():
    global user_counter
    user_counter += 1
    return f"user_{user_counter}"