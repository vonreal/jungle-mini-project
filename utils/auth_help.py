import jwt
from flask import request
from bson import ObjectId
from db import db

SECRET_KEY = "sheep" #

def get_user_from_token():
    # 1. 쿠키에서 토큰 꺼내기
    token_receive = request.cookies.get('mytoken')
    if not token_receive:
        return None, "로그인이 필요합니다."

    try:
        # 2. 토큰 복호화
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_uid = payload.get('uid') #
        
        # 3. DB에서 유저 찾기
        user = db.user.find_one({'_id': ObjectId(user_uid)}, {'password': False})
        if not user:
            return None, "사용자를 찾을 수 없습니다."
            
        return user, None # 유저 객체와 에러 없음(None) 반환

    except jwt.ExpiredSignatureError:
        return None, "로그인 시간이 만료되었습니다." #
    except jwt.exceptions.DecodeError:
        return None, "로그인이 필요합니다." #
    except Exception as e:
        return None, str(e)