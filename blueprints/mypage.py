from flask import render_template, jsonify, request,Blueprint, redirect
from db import db
from datetime import datetime
import re
from bson import ObjectId
from utils import handle_image, auth_help

bp = Blueprint('mypage', __name__)

@bp.route('/mypage')
def show_register():

    user, _ = auth_help.get_user_from_token()

    if user is None:
        return redirect('/login')

    user_feeds = list(db.feeds.find({'user_id': user["_id"]}).sort('create_date', -1))

    feeds_list = []
    total_likes = 0

    for f in user_feeds:
        total_likes += len(f.get('likes', []))
        feeds_list.append({
            'feed_id': str(f['_id']),
            'feed_img': f.get('image_path', '')
        })

    feed_total = len(feeds_list)

    is_login = False
    if user != None:
        is_login = True

    return render_template('mypage.html', isLogin=is_login, user=user, totalLikes = total_likes,feedTotal = feed_total)

@bp.route('/mypage/update_mypage', methods=['post'])
def change_pofile_img_path():

    user, error_msg = auth_help.get_user_from_token()
    if error_msg:
        return jsonify({'result': 'fail', 'msg': error_msg})

    new_nickname = request.form.get('nickname', '').strip()

    image_file = request.files.get('image')
    
    if image_file and image_file.filename != '':
        saved_file_path = handle_image.save_image(request.files, type="profile")
    else:
        saved_file_path = user.get('profile_img_path') 

    nickname_regex = r'^[a-zA-Z가-힣]{1,16}$'
    if not re.match(nickname_regex, new_nickname):
        return jsonify({'result': 'fail', 'msg': "닉네임 형식이 올바르지 않습니다. (한글/영문 1~16자)"})
    
    
    if new_nickname == user['nickname'] and saved_file_path == user['profile_img_path']:
        return jsonify({'result': 'fail', 'msg': '변경사항이 없습니다.'})
    
    
    db.user.update_one(
        {'_id': user['_id']},
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
    user, error_msg = auth_help.get_user_from_token()
    if error_msg:
        return jsonify({'result': 'fail', 'msg': error_msg})
    
    user_feeds = list(db.feeds.find({'user_id': user["_id"]}).sort('create_date', -1))

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
        'profile_img': user['profile_img_path'],
        'nickname': user['nickname'],
        'likes': total_likes,
        'feed_total': len(feeds_list), 
        'feeds': feeds_list
    })
