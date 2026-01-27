def generate_new_id(cursor, table_name: str, id_column: str, prefix: str) -> str:
    # 예: user_id에서 "_" 뒤의 숫자를 정수로 변환하여 최댓값 조회
    # SUBSTRING_INDEX(col, '_', -1) : user_123 -> 123 추출
    query = f"""
        SELECT MAX(CAST(SUBSTRING_INDEX({id_column}, '_', -1) AS UNSIGNED)) as max_id 
        FROM {table_name}
    """
    cursor.execute(query)
    result = cursor.fetchone()

    max_id = result['max_id'] if result['max_id'] is not None else 0
    return f"{prefix}_{max_id + 1}"