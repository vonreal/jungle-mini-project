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


    new_nickname = request.form.get('nickname_give')
    saved_file_path = handle_image.save_image(request.files, type="profile")
    # file = request.files.get('file_give')
    # if not file:
    #     return jsonify({'result': 'fail', 'msg': '사진 파일이 없습니다.'})
    
    # extension = file.filename.split('.')[-1]
    # now_time = datetime.now().strftime('%Y%m%d%H%M%S')
    # file_name = f"{user_id}_{now_time}.{extension}"

    # save_path = os.path.join('static/image', file_name)
    # file.save(save_path)

    

    db.user.update_one(
        {'username': user_id},
        {'$set': {
            'nickname': new_nickname,
            'profile_img': saved_file_path
        }}
    )

    return jsonify({'result': 'success', 'msg': '프로필 수정 완료!'})

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

        #여기에 좋아요를 가져 올 수 있을꺼 같은데
        

        feeds_list.append({
            'feed_id': str(f['_id']),
            'feed_img': f.get('image_path', '')
        })


    
    # 리스폰스 조
    return jsonify({
        'profile_img': user.get('profile_img_path', 'default_profile.png'),
        'nickname': user.get('nickname'),
        'likes': total_likes,
        'feed_total': len(feeds_list), 
        'feeds': feeds_list
    })