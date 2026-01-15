# 클라우드 커뮤니티 REST API Docs

<aside>
<img src="notion://custom_emoji/845a6cfa-ad4b-4505-8350-960c9f51a87a/168954da-c755-8023-8dcf-007afaa4b2e6" alt="notion://custom_emoji/845a6cfa-ad4b-4505-8350-960c9f51a87a/168954da-c755-8023-8dcf-007afaa4b2e6" width="40px" />

전체화면으로 해놓고 구현하시면 편합니다!
Cmd + T (Ctrl + T) 누르면 탭 추가가 가능합니다. 참고하세요!

창 추가하는건 Cmd + Shift + N (Ctrl + Shift + N) 입니다!.

</aside>

### { 내가 좋아요한 게시글 목록 }

**GET** `/users/me/likes` 

내가 좋아요한 게시글의 목록을 조회합니다. 로그인을 하고 진행합니다.

**Request Headers**

| 헤더 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| Authorization | String | O | 로그인 토큰으로 인증 |

**Query Parameters**

| 파라미터 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| page | integer | X | 페이지 번호(기본값 :  1) |
| limit | integer | X | 페이지 크기 |

**Response (200 OK)**

```json
{
  "status": "success",
  "data": [
    {
      "post_id": "1",
	     "title": "내가 좋아요를 누른 게시글 제목",
	     "author" : {
		     "author_id" : "admin",
		     "nickname" : "abc" 
		    },
		  "count_likes" : 12,
		  "count_comment" : 90,
      "created_at": "2026-01-04T12:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100
  }
}
```

**Response (401 UNAUTHORIZED)**

```json
{
  "status": "error",
  "error": {
    "code": "UNAUTHORIZED",
    "message": "로그인이 필요합니다."
  }
}
```

**Response (404 NOT_FOUND)**

```json
{
  "status": "error",
  "error": {
    "code": "NOT_FOUND",
    "message": "게시글을 찾을 수 없습니다"
  }
}
```

---

### { 좋아요 상태 확인 }

**GET** `/posts/{post_id}/likes` 

특정 게시글의 총 좋아요 수와 현재 로그인한 사용자의 좋아요 여부를 확인합니다.

**Request Headers**

| 헤더 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| Authorization | string | O  | 로그인 토큰으로 인증 |

**Path Parameters**

| 파라미터 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| post_id | String | O | 게시글 ID |

**Response (200 OK)**

```json
{
  "status": "success",
  "data":
    {
      "post_id" : "1",
      "count_likes" : 3,
      "liked" : true
    }
}
```

**Response (404 NOT_FOUND)**

```json
{
  "status": "error",
  "error": {
    "code": "NOT_FOUND",
    "message": "게시글을 찾을 수 없습니다"
  }
}
```

---

### 내가 작성한 댓글

**GET** `/users/me/comments`

내가 작성한 댓글 목록을 조회합니다. 로그인이 필요합니다.

**Request Headers**

| 헤더 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| Authorization | string | O | Bearer 토큰 |

**Query Parameters**

| 파라미터 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| page | integer | X | 페이지 번호 (기본값: 1) |
| limit | integer | X | 페이지당 댓글 수 (기본값: 20) |
| sort | string | X | 정렬 기준 (created_at, updated_at) |

**Response (200 OK)**

```json
{
  "status": "success",
  "data": [
    {
      "id": "comment_1",
      "post": {
        "id": "1",
        "title": "게시글 제목"
      },
      "content": "내가 작성한 댓글",
      "created_at": "2026-01-04T12:00:00Z",
      "updated_at": "2026-01-05T12:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100
  }
}
```

**Response (401 Unauthorized)**

```json
{
  "status": "error",
  "error": {
    "code": "UNAUTHORIZED",
    "message": "로그인이 필요합니다."
  }
}
```

---

### { 댓글 목록 조회 }

**GET** `/posts/{post_id}/comments`

특정 게시글의 댓글을 조회합니다. 대량의 데이터를 조회하기 위해 `page`와 `limit`으로 페이지를 나눴습니다.

**Path Parameters**

| 파라미터 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| post_id | String | O | 특정 게시글을 나타내는 유일한 식별자 입니다. |

**Query Parameters**

| 파라미터 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| page | integer | X | 페이지 번호(기본값 : 1) |
| limit | intger | X | 페이지당 댓글 수  |

**Response (200 OK)**

```json
{
  "status": "success",
  "data": [
    {
	    "comment_id" : "1",
	    "content" : "댓글 내용입니다.",
	    "author" : {
	      "login_id" : "admin",
	      "nickname" : "abc"
    },
      "created_at" : "2026-01-07T08:30:00+09:00",
      "title" : "댓글을 작성한 게시글의 제목"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100
  }
}
```

---

### { 내가 쓴 게시글 목록  }

**GET** `/users/me/posts`

로그인한 사용자가 본인이 작성한 게시글 목록을 조회합니다.

**Request Headers**

| 헤더 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| Authorization | string | O | 로그인한 토큰으로 사용자를 인증한다 |

**Query Parameters**

| 파라미터 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| page | integer | X | 페이지 번호(페이지는 1번부터) |
| limit | integer | X | 한 페이지당 게시글 (기본값:20) |
| sort | String | X | 정렬한 기준을 정한다. |

**Response (200 OK)**

```json
{
  "status": "success",
  "data": [
    {
      "post_id": "1",
      "title": "내가 쓴 게시글 제목",
      "created_at": "2026-01-04T12:00:00Z"
    }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100
  }
}
```

**Response (403 FORBIDDEN)**

```json
{
  "status": "error",
  "error": {
    "code": "POST_GET_FORBIDDEN",
    "message": "본인이 작성한 게시글만 조회할 수 있습니다.",
  }
}
```

---

### { 게시글 상세 조회 }

**GET** `/posts/{post_id}` 

특정 게시글의 상세 정보를 조회 합니다. 해당 API 호출시 조회수가 1 증가합니다.

**Path Parameters**

| 파라미터 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| post_id | String | O | 조회할 게시글 ID |

**Response (200 OK)**

```json
{
  "status": "success",
  "data": 
    {
      "post_id": "1",
      "title" : "게시글의 제목 입니다.",
      "content" : "게시글 내용입니다.",
      "author" : {
	      "id" : "admin",
	      "nickname" : "abc"
    },
  "created_at": "2026-01-04T12:00:00Z"
  }
}
```

**Response (403 FORBIDDEN)**

```json
{
  "status": "error",
  "code": "POST_ACCESS_DENIED",
  "message": "비공개 게시글입니다."
}
```

**Response (404 NOT_FOUND)**

```json
{
  "status": "error",
  "code": "**NOT_FOUND**",
  "message": "게시글을 찾을 수 없습니다."
}
```

**Response (400 BAD__REQUEST)**

```json
{
  "status": "error",
  "code": "**BAD_REQUEST**",
  "message": "잘못된 게시글의 ID입니다."
}
```

---

### { 게시글 정렬 }

**GET** `/posts` 

게시글 목록을 조회 합니다. `sort`로 정렬 기준을 지정할 수 있습니다. 

**Query Parameters**

| 파라미터 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| page | integer | X | 페이지 번호 (기본값: 1) |
| limit | integer | X | 페이지당 게시글 개수 (기본값: 20) |
| sort | String | X | 정렬 기준 |

**Response (200 OK)**

```json
{
  "status": "success",
  "data": [
	    {
      "post_id" : "1",
      "title" : "게시글의 제목",

      "author" : {
	      "author_id" : "admin",
	      "nickname" : "abc"
    },
      "created_at" : "2026-01-07T08:30:00+09:00"
      }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100
  }
}
```

**Response (400 BAD__REQUEST)**

```json
{
  "status": "error",
  "error": {
    "code": "**BAD__REQUEST**",
    "message" : "정렬 기준을 지원하지 않습니다."	  
  }
}
```

---

### { 게시글 검색 }

**GET** `/posts` 

게시글은 제목/내용을 기준으로 검색하여 목록을 조회합니다.(로그인 없이 검색 가능)

**Query Parameters**

| 파라미터 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| keyword | String | O | 제목 또는 내용에 포함된 검색 키워드 |
| page | integer | X | 페이지 번호 (기본값: 1) |
| limit | integer | X | 페이지당 게시글 개수 (기본값: 20) |

**Response (200 OK)**

```json
{
  "status": "success",
  "data": [
	    {
      "post_id" : "1",
      "title" : "게시글 제목",
      "author" : {
	      "id" : "admin",
	      "nickname" : "abc"
    },
    "created_at": "2026-01-04T12:00:00Z"
      }
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100
  }
}
```

**Response (400 BAD__REQUEST)**

```json
{
  "status": "error",
  "error": {
    "code": "**BAD__REQUEST**",
    "message" : "검색어(keyword)가 없습니다."	  
  }
}
```

---

### { 게시글 목록 조회 }

**GET** `/posts` 

게시글 목록을 페이지네이션 하여 조회합니다.

**Query Parameters**

| 파라미터 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| page | integer | X | 페이지 번호(1페이지 부터 시작) |
| limit | integer | X | 페이지당 게시글 개수 |

**Response (200 OK)**

```json
{
  "status": "success",
  "data": [
	    {
      "post_id" : "1",
      "title" : "postname",
      "author" : {
	      "authorid" : "admin",
	      "nickname" : "abc"
    }
      "created_at" : "2026-01-07T08:30:00+09:00",
  ],
  "pagination": {
    "page": 1,
    "limit": 20,
    "total": 100
  }
}
```

---

### { 특정 회원 조회 }

**GET** `/users/{user_id}` 

입력한 id에 맞는 회원을 조회합니다. 

**Path Parameters**

| 파라미터 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| user_id | String  | O  | 조회할 ID입니다. |

**Response (200 OK)**

```json
{
  "status": "success",
  "data": 
    {
	    "id" : "admin",
      "nickname": "abc",
		  "profile_image": "image.123",
		  "created_at": "2026-01-04T12:00:00Z"		  
    }
}
```

**Response (404 NOT_FOUND)**

```json
{
  "status": "error",
  "error": 
    {
	    "code" : "NOT_FOUND"
	    "message" : "사용자를 찾을 수 없습니다."		  
    }
}
```

---

### { 내 프로필 조회 }

**GET** `/users/me` 

로그인한 사용자 정보 조회

**Request Headers**

| 헤더 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| Authorization | string | O  | 토큰 형식의 인증 정보, 로그인 시 발급받은 토큰을 전달 |

**Response (200 OK)**

```json
{
  "status": "success",
  "data": 
    {
      "email": "example@naver.com",
	    "nickname" : "abc",
	    "profile_image" : "image.123",
	    "created_at": "2026-01-04T12:00:00Z",
	    "id" : "admin"
    }
}
```

**Response (401 UNAUTHORIZED)**

```json
{
  "status": "error",
  "error": {
    "code": "UNAUTHORIZED",
    "message": "로그인이 필요합니다."
  }
}
```

---

### { 좋아요 취소 }

**DELETE**`/posts/{post_id}/likes`

등록한 좋아요를 취소합니다. 

**Request Headers**

| 헤더 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| Authorization | String | O | 로그인 토큰으로 인증 |

**Response (204 No Content)**

```json
(응답 본문 없음)
```

**Response (401 UNAUTHORIZED)**

```json
{
  "status": "error",
  "error": {
    "code": "UNAUTHORIZED",
    "message": "로그인이 필요합니다."
  }
}
```

**Response (404 NOT_FOUND)**

```json
{
  "status": "error",
  "error": {
    "code": "NOT_FOUND",
    "message": "게시글을 찾을 수 없습니다"
  }
}
```

---

### 좋아요 등록

**POST** `/posts/{post_id}/likes`

게시글에 좋아요를 등록합니다. 로그인이 필요합니다.

**Request Headers**

| 헤더 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| Authorization | string | O | Bearer 토큰 |

**Path Parameters**

| 파라미터 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| post_id | string | O | 좋아요를 등록할 게시글 ID |

**Response (201 Created)**

```json
{
  "status": "success",
  "data": {
    "post_id": "1",
    "user_id": "admin",
    "created_at": "2026-01-04T12:00:00Z"
  }
}
```

**Response (401 UNAUTHORIZED)**

```json
{
  "status": "error",
  "error": {
    "code": "UNAUTHORIZED",
    "message": "로그인이 필요합니다."
  }
}
```

**Response (404 Not Found)**

```json
{
  "status": "error",
  "error": {
    "code": "POST_NOT_FOUND",
    "message": "게시글을 찾을 수 없습니다."
  }
}
```

**Response (409 Conflict)**

```json
{
  "status": "error",
  "error": {
    "code": "ALREADY_LIKED",
    "message": "이미 좋아요를 누른 게시글입니다."
  }
}
```

---

### {댓글 삭제}

**DELETE** `/comments/{comment_id}`

본인이 작성한 댓글을 삭제합니다.

**Request Headers**

| 헤더 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| Authorization | String | O | 로그인 토큰으로 인증 |

**Response (204 No Content)**

```json
(응답 본문 없음)
```

**Response (401 UNAUTHORIZED)**

```json
{
  "status": "error",
  "error": {
    "code": "UNAUTHORIZED",
    "message": "로그인이 필요합니다."
  }
}
```

**Response (403 FORBIDDEN)**

```json
{
  "status": "error",
  "error": {
    "code": "POST_DELETE_FORBIDDEN",
    "message": "본인이 작성한 댓글만 삭제할 수 있습니다.",
  }
}
```

**Response (404 NOT_FOUND)**

```json
{
  "status": "error",
  "error": {
    "code": "NOT_FOUND",
    "message": "댓글을 찾을 수 없습니다."
  }
}

```

---

### { 댓글 수정 }

**PUT** `/posts/{post_id}/comments/{comment_id}` 

본인이 작성한 댓글을 수정합니다.

**Request Headers**

| 헤더 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| Authorization | String | O | 로그인하고 생성된 토큰으로 식별 |
| Content-type  | String | O | application/json |

**Request Body**

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| content | String | O | 수정된 댓글 내용  |

**Request Example → Reqeust Body 가 있는 경우 작성 필**

```json
{
  "content": "수정된 댓글 내용"
}
```

**Response (200 OK) → 상황에 맞게 바꿔서 쓰세요.**

```json
{
  "status": "success",
  "data": {
    "post_id": "1",
    "id": "comment_1",
    "author" : {
	    "login_id" : "admin",
	    "nickname" : "abc"
	   },
	   "content" : "수정된 댓글의 내용",
	   "created_at": "2026-01-04T12:00:00Z",
	   "updated_at" : "2026-01-05T12:00:00Z"
  }
}
```

**Response (401 UNAUTHORIZED)** 

```json
{
  "status": "error",
  "error": {
    "code": "UNAUTHORIZED",
    "message": "로그인이 필요합니다."
  }
}
```

**Response (403 FORBIDDEN)** 

```json
{
  "status": "error",
  "error": {
    "code": "FORBIDDEN",
    "message": "본인이 작성한 댓글만 수정할 수 있습니다."
  }
}
```

---

### { 댓글 작성 }

**POST** `/posts/{post_id}/comments`

특정 게시글에 댓글을 작성합니다. 댓글은 로그인을 하고 작성할 수 있습니다.

**Request Headers**

| 헤더 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| Authorization | String | O | 로그인하고 받은 토큰으로 인 |
| Content-type  | String | O | application/json |

**Request Body**

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| content | String | O | 댓글의 내용 |

**Request Example → Reqeust Body 가 있는 경우 작성 필**

```json
{
  "content": "댓글의 내용"
}
```

**Response (201 Created) → 상황에 맞게 바꿔서 쓰세요.**

```json
{
  "status": "success",
  "data": {
    "post_id": "1",
    "id": "comment_1",
    "author" : {
	    "login_id" : "admin"
	    "nickname" : "abc"
	   },
	   "content" : "댓글의 내용"
	   "created_at": "2026-01-04T12:00:00Z"
  }
}
```

---

### { 게시글 삭제 }

**DELETE** `/posts/{post_id}`

로그인한 사용자가 작성한 게시글을 삭제합니다.

**Path Parameters**

| 파라미터 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| post_id | String | O | 조회할 게시글 ID |

**Request Headers**

| 헤더 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| Authorization | String | O | 로그인한 사용자 인증을 위한 헤더이다. |

**Response (204 No Content)**

```json
(응답 본문 없음)
```

**Response (403 FORBIDDEN)**

```json
{
  "status": "error",
  "error": {
    "code": "POST_DELETE_FORBIDDEN",
    "message": "본인이 작성한 게시글만 삭제할 수 있습니다.",
  }
}
```

**Response (401 UNAUTHORIZED)**

```json
{
  "status": "error",
  "error": {
    "code": "**UNAUTHORIZED**",
    "message": "본인이 작성한 게시글만 삭제할 수 있습니다.",
  }
}
```

---

### { 게시글 수정 }

**PUT** `/posts/{post_id}` 

자신이 작성한 게시글을 수정합니다.

**Path Parameters**

| 파라미터 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| post_id | String | O | 조회할 게시글 ID |

**Request Headers**

| 헤더 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| Authorization | String | O | 로그인할 때 생성된 로그인으로 본인의 게시글을 판단 |
| Content-type  | String | O | application/json |

**Request Body**

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| title | String | X | 수정할 게시글의 제목 |
| content | String | X | 수정할 게시글의 내용 |

**Request Example → Reqeust Body 가 있는 경우 작성 필**

```json
{
  "title": "게시글의 제목",
  "content": "게시글의 내용"
}
```

**Response (200 OK) → 상황에 맞게 바꿔서 쓰세요.**

```json
{
  "status": "success",
  "data": {
	  "post_id" : "1"
    "title": "수정된 게시글의 제목",
    "content": "수정된 게시글의 내용",
    "author" : {
	    "id" : "admin",
	    "nickname" : "abc"
	    },
    "updated_at": "2026-01-04T12:00:00Z"
  }
}
```

**Response (403 FORBIDDEN)** 

```json
{
  "status": "error",
  "error": {
    "code": "POST_UPDATE_FORBIDDEN",
    "message": "본인이 작성한 게시글만 수정할 수 있습니다.",
  }
}
```

**Response (401 UNAUTHORIZED)** 

```json
{
  "status": "error",
  "error": {
    "code": "**UNAUTHORIZED**",
    "message": "로그인 후 게시글 수정이 가능합니다.",
  }
}
```

**Response (404 NOT FOUND)** 

```json
{
  "status": "error",
  "error": {
    "code": "**NOT FOUND**",
    "message": "게시글을 찾을 수 없습니다.",
  }
}
```

---

### { 게시글 작성 }

**POST** `/posts`

로그인한 사용자가 제목과 내용을 작성하여 게시글을 등록합니다.

**Request Headers**

| 헤더 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| Authorization | String  | O | 로그인 한 토큰으로 사용자를 인증한다. |
| Content-type | String  | O  | application/json |

**Request Body**

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| title | String | O | 게시글의 제목 |
| content | String | O | 게시글의 내용  |

**Request Example → Reqeust Body 가 있는 경우 작성 필**

```json
{
  "title": "게시글 제목",
  "content": "게시글 내용"
}
```

**Response (201 Created) → 상황에 맞게 바꿔서 쓰세요.**

```json
{
  "status": "success",
  "data": {
	  "post_id" : "1",
    "title": "게시글 제목",
    "content": "게시글 내용",
    "created_at" : "2026-01-07T08:30:00+09:00",
    "author" : {
	    "id" : "admin",
	    "nickname" : "abc" 
  }
  }
}
```

**Response (401 UNAUTHORIZED)**

```json
{
  "status": "error",
  "error": {
    "code": "**UNAUTHORIZED**",
    "message" : "로그인을 하지 않았습니다."	  
  }
}
```

**Response (400 BAD__REQUEST)**

```json
{
  "status": "error",
  "error": {
    "code": "**BAD__REQUEST**",
    "message" : "게시글의 제목 및 내용을 작성하지 않았습니다."	  
  }
}
```

---

### { 회원 탈퇴 }

**DELETE** `/users/me`

회원을 삭제합니다. 삭제된 회원은 복구할 수  없으므로 주의가 필요합니다. 

**Request Headers**

| 헤더 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| Authorization | String | O | 로그인 시 발급되 토큰 |

**Response (204 NoContent) → 상황에 맞게 바꿔서 쓰세요.**

```json
(응답 본문 없음)
```

**Response (401 UNAUTHORIZED)** 

```json
{
  "status": "error",
  "error": {
    "code": "**UNAUTHORIZED**",
    "message" : "로그인이 필요합니다."	  
  }
}
```

---

### { 프로필 수정 }

**PUT**`/users/me`

닉네임, 프로필 이미지, 비밀번호 변경

**Request Headers**

| 헤더 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| Authorization | String  | O | 로그인한 토큰을 전달 |
| Content-type | String  | O | application/json |

**Request Body**

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| current_password | String | O  | 변경전 비밀번호 입니다. |
| nickname | String | O | 변경할 닉네임입니다. |
| profile_image | String | X | 변경할 프로필이미지 입니다. |
| new_password | String | X | 변경 후 비밀번호입니다. |

**Request Example → Reqeust Body 가 있는 경우 작성 필**

```json
{
  "current_password": "admin123@",
  "nickname": "abc",
  "profile_image": "image.123"
}
```

**Response (200 OK) → 상황에 맞게 바꿔서 쓰세요.**

```json
{
  "status": "success",
  "data": {
	  "id" : "admin",
    "nickname": "abc",
		"email" : "example@naver.com",
	  "profile_image": "image.123",
    "updatedAt": "2026-01-07T08:30:00+09:00"
  }
}
```

**Response (400 BAD_REQUEST)** 

```json
{
  "status": "error",
  "error": {
    "code": "**BAD_REQUEST**",
    "message" : "필수 항목이 누락되었습니다."	  
  }
}
```

**Response (401 UNAUTHORIZED)** 

```json
{
  "status": "error",
  "error": {
    "code": "UNAUTHORIZED",
    "message" : "로그인이 필요합니다."	  
  }
}
```

---

### { 회원 로그인 }

**POST** `/auth/tokens`

이메일과 비밀번호로 사용자 인증을 수행하고 토큰을 발급한다. 

**Request Headers**

| 헤더 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| Content-type | String  | O | 요청 본문 형식(application/json) |

**Request Body**

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| email | String | O | 가입한 이메일 |
| password | String | O | 비밀번호(8자 이상, 영문/숫자/특수문자 포함) |

**Request Example → Reqeust Body 가 있는 경우 작성 필**

```json
{
  "id": "admin",
  "password": "admin123@"
}
```

**Response (201 Created) → 상황에 맞게 바꿔서 쓰세요.**

```json
{
  "status": "success",
  "data": {
	  "token_type": "Bearer",
	  "access_token" : "...",  // 실제 API 요청에 사용되는 토큰
    "expires_in": 3600
  }
}
```

**Response (401 UNAUTHORIZED) → 상황에 맞게 바꿔서 쓰세요.**

```json
{
  "status": "error",
  "error": {
    "code": "UNAUTHORIZED",
    "message": "이메일 또는 비밀번호가 올바르지 않습니다."
  }
}

```

---

### { 회원가입 }

**POST** `/users`

회원가입을 통해 회원 정보를 추가 합니다. 이메일, 비밀번호, 닉네임, 프로필 이미지(선택) 입니다.

**Request Headers**

| 헤더 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| Content-type | String | O | 요청 본문 형식(application/json) |

**Request Body**

| 필드 | 타입 | 필수 | 설명 |
| --- | --- | --- | --- |
| email | String  | O | 이메일형식으로 작성해주세요 |
| password | String | O  | 비밀번호(8자 이상, 영문/숫자/특수문자 포함) |
| nickname | String | O | 사용자 닉네임 |
| profile_image | String | X | 프로필 이미지 URL(선택) |

**Request Example → Reqeust Body 가 있는 경우 작성 필**

```json
{
  "email": "example@naver.com",
  "password": "admin123@",
  "nickname": "abc",
  "profile_image": "image.123"
}
```

**Response (201 Created)** 

```json
{
  "status": "success",
  "data": {
    "email": "example@naver.com",
    "nickname" : "abc",
    "profile_image" : "image.123",
    "created_at": "2026-01-04T12:00:00Z",
    "id" : "admin"
  }
}
```

**Response (400 BAD_REQUEST)** 

```json
{
  "status": "error",
  "error": {
    "code": "BAD_REQUEST",
    "message": "요청 형식이 올바르지 않습니다."
  }
}
```

---