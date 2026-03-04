from flask import Flask, render_template, jsonify, request,Blueprint
from db import db
from datetime import datetime
import re
import jwt
import os
from utils import handle_image

bp = Blueprint('mypage', __name__)
SECRET_KEY = "sheep"

@bp.route('/mypage/update_mypage', methods=['post'])
def change_pofile_img_path():

    # 1. 클라이언트 쿠키를 꺼내
    token_receive = request.cookies.get('mytoken')

    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        # 토큰에 적힌 id 가져오기
        user_id = payload['id']
    except jwt.ExpiredSignatureError:
        # 토큰의 유효기간이 끝난 경우
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        # 토큰이 뭔가 잘못됨
        return jsonify({'result': 'fail', 'msg': '로그인이 필요합니다.'})

    current_user = db.user.find_one({'username': user_id})
    new_nickname = request.form.get('nickname')
    saved_file_path = handle_image.save_image(request.files, type="profile")
    # file = request.files.get('file')
    # if not file:
    #     return jsonify({'result': 'fail', 'msg': '사진 파일이 없습니다.'})
    
    # extension = file.filename.split('.')[-1]
    # now_time = datetime.now().strftime('%Y%m%d%H%M%S')
    # file_name = f"{user_id}_{now_time}.{extension}"

    # save_path = os.path.join('static/image', file_name)
    # file.save(save_path)

    nickname_regex = r'^[a-zA-Z가-힣]{1,16}$'
    if not re.match(nickname_regex, new_nickname):
        return jsonify({'result': 'fail', 'msg': "닉네임 형식이 올바르지 않습니다. (한글/영문 1~16자)"})
    
    if new_nickname == current_user.get('nickname') and saved_file_path == current_user.get('profile_img_path'):
        return jsonify({'result': 'fail', 'msg': '변경사항이 없습니다.'})

    
    db.user.update_one(
        {'username': user_id},
        {'$set': {
            'nickname': new_nickname,
            'profile_img_path': saved_file_path
        }}
    )

    return jsonify({'result': 'success', 'msg': '프로필 수정 완료!'})

def delete_user():
    
    return jsonify({'result': 'success', 'msg': '아이디 삭제 완료!'})

@bp.route('/mypage', methods=['GET'])
def get_mypage():
    token_receive = request.cookies.get('mytoken')
    try:
        payload = jwt.decode(token_receive, SECRET_KEY, algorithms=['HS256'])
        user_id = payload['id']
    except jwt.ExpiredSignatureError:
        return jsonify({'result': 'fail', 'msg': '로그인 시간이 만료되었습니다.'})
    except jwt.exceptions.DecodeError:
        return jsonify({'result': 'fail', 'msg': '로그인이 필요합니다.'})


    user = db.user.find_one({'username': user_id}, {'_id': False, 'password': False})
    if not user:
        return jsonify({'result': 'fail', 'msg': '사용자를 찾을 수 없습니다.'})
    
    user_feeds = list(db.feeds.find({'username': user_id}).sort('create_date', -1))

    feeds_list = []
    total_likes = 0


    for f in user_feeds:

        total_likes += len(f.get('likes', []))

        feeds_list.append({
            'feed_id': str(f['_id']),
            'feed_img': f.get('image_path', '')
        })


    
    # 리스폰스 조
    return jsonify({
        'profile_img': user.get('profile_img_path', '/static/image/default.png'),
        'nickname': user.get('nickname'),
        'likes': total_likes,
        'feed_total': len(feeds_list), 
        'feeds': feeds_list
    })