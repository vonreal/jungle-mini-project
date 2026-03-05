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
    #1 아이디 비번 비번확인 닉네임 받아

    new_id_receive = request.form['username']
    new_password_receive =request.form['password']
    new_nickname_receive =request.form['nickname']

    #3 아이디,닉네임 중복과 정규형 맞췄늕 확인
    id_dup = db.user.find_one({'username':new_id_receive})
    nickname_dup = db.user.find_one({'nickname':new_nickname_receive})

    if  id_dup is not None:
        return jsonify({'result': 'fail', 'msg': "중복된 아이디 입니다"})
    if nickname_dup is not None:
        return jsonify({'result': 'fail', 'msg': "중복된 닉네임 입니다"})
    
    #아이디,비번,닉네임 정규식 확인
    id_regex = r'^[a-z0-9_-]{5,20}$'
    if not re.match(id_regex, new_id_receive):
        return jsonify({'result': 'fail', 'msg': "아이디 형식이 올바르지 않습니다."})

    password_regex = r'^(?=.*[a-zA-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,16}$'
    if not re.match(password_regex, new_password_receive):
        return jsonify({'result': 'fail', 'msg': "비밀번호 형식이 올바르지 않습니다."})
    
    nickname_regex = r'^[a-zA-Z가-힣]{1,16}$'
    if not re.match(nickname_regex, new_nickname_receive):
        return jsonify({'result': 'fail', 'msg': "닉네임 형식이 올바르지 않습니다."})
    

    #4 비밀번호를 해싱
    new_hash_password = hashlib.sha256(new_password_receive.encode('utf-8')).hexdigest()

    #5 디비에 유저객체를 만들어 저장해
    doc = {
        'username': new_id_receive,
        'password': new_hash_password,
        'nickname': new_nickname_receive,
        'create_date': handle_time.get_now(),
        'profile_img_path': "assets/img/avatar.jpg"
    }

    db.user.insert_one(doc)

    #6 완료 응답
    return jsonify({'result': 'success', 'msg': "회원가입 완료되었습니다!"})



@bp.route('/login')
def show_login():
    
    return render_template('login.html')

@bp.route('/login', methods=['post'])
def check_login():

    #1단 아이디랑 비번을 받아
    id_receive = request.form['username']
    password_receive =request.form['password']

    #2제 비번을 암호화해
    hash_password = hashlib.sha256(password_receive.encode('utf-8')).hexdigest()

    #3. 아이디랑 비번을 디비랑 조회를 해
    results = db.user.find_one({'username':id_receive,'password':hash_password})

    #4.확인을 하고 토큰을 주거나 알림을 줘

    SECRET_KEY = "sheep"
    
    if results is not None:

        user_uid = str(results['_id'])

        payload = {
            'uid' : user_uid,
            'exp': datetime.now() + timedelta(seconds=60 * 60)  # 1시간 유효
        }
        token = jwt.encode(payload, SECRET_KEY, algorithm='HS256')

        res = make_response(jsonify({'result': 'success', 'msg': '로그인 성공!'}))

        # 클라이언트 컴퓨터 쿠기에 토큰을 저장해
        res.set_cookie('mytoken', token)

        return res
    
    else:
        return jsonify({'result': 'fail','msg': '로그인 실패!'})
