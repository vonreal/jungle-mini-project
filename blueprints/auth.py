from flask import render_template, jsonify, request, Blueprint, make_response
from db import db
import hashlib
from datetime import datetime,timedelta
import re
import jwt
from utils import handle_time

bp = Blueprint('auth', __name__)

@bp.route('/register')
def show_register():
    return render_template('signup.html')


@bp.route('/register', methods=['post'])
def create_id():
    new_id_receive = request.form['username']
    new_password_receive =request.form['password']
    new_nickname_receive =request.form['nickname']

    # 아이디 정규식 확인 (5~20자, 영문 소문자/숫자/특수기호)
    id_regex = r'^[a-z0-9_-]{5,20}$'
    if not re.match(id_regex, new_id_receive):
        return jsonify({
            'result': 'fail',
            'fields': {'username': "아이디는 5~20자의 영문 소문자, 숫자, 특수기호(_),(-)만 사용 가능합니다."}
        })

    # 비밀번호 정규식 확인 (8~16자, 영문/숫자/특수문자 필수 조합)
    password_regex = r'^(?=.*[a-zA-Z])(?=.*\d)(?=.*[~!@#$%^&*()\-=_+])[A-Za-z\d~!@#$%^&*()\-=_+]{8,16}$'
    if not re.match(password_regex, new_password_receive):
        return jsonify({
            'result': 'fail',
            'fields': {'password': "비밀번호는 8~16자의 영문, 숫자, 특수문자를 각각 최소 하나씩 포함해야 합니다."}
        })

    # 닉네임 정규식 확인 (1~16자, 영문/한글)
    nickname_regex = r'^[a-zA-Z가-힣]{1,16}$'
    if not re.match(nickname_regex, new_nickname_receive):
        return jsonify({
            'result': 'fail',
            'fields': {'nickname': "닉네임은 한글 또는 영문 1~16자로 입력해주세요. (숫자/특수문자 불가)"}
        })

    # 중복 확인
    if db.user.find_one({'username': new_id_receive}):
        return jsonify({'result': 'fail', 'fields': {'username': "이미 사용 중인 아이디입니다."}})
    if db.user.find_one({'nickname': new_nickname_receive}):
        return jsonify({'result': 'fail', 'fields': {'nickname': "이미 사용 중인 닉네임입니다."}})
    

    new_hash_password = hashlib.sha256(new_password_receive.encode('utf-8')).hexdigest()

    doc = {
        'username': new_id_receive,
        'password': new_hash_password,
        'nickname': new_nickname_receive,
        'create_date': handle_time.get_now(),
        'profile_img_path': "/assets/img/avatar.jpg"
    }

    db.user.insert_one(doc)

    #6 완료 응답
    return jsonify({'result': 'success', 'msg': "회원가입 완료되었습니다!"})



@bp.route('/login')
def show_login():
    
    return render_template('login.html')

@bp.route('/login', methods=['post'])
def check_login():

    id_receive = request.form['username']
    password_receive =request.form['password']

    hash_password = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()

    results = db.user.find_one({'username':id_receive,'password':hash_password})


    SECRET_KEY = "sheep"
    
    if results is not None:

        user_uid = str(results['_id'])

        payload = {
            'uid' : user_uid,
            'exp': datetime.now() + timedelta(seconds=60 * 60)  # 1시간 유효
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        res = make_response(jsonify({'result': 'success', 'msg': '로그인 성공!'}))

        res.set_cookie('mytoken', token)

        return res
    
    else:
        return jsonify({'result': 'fail','msg': '로그인 실패!'})
