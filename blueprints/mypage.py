from flask import render_template, jsonify, request,Blueprint, redirect, make_response
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
    
    is_login = False
    if user != None:
        is_login = True

    username = user["username"]
    
    
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

    profile_img = user.get('profile_img_path')


    return render_template('mypage.html',
                            isLogin=is_login,
                            username=username,
                            feedTotal= feed_total,
                            totalLikes = total_likes,
                            profileImg=profile_img,
                            feeds=feeds_list)

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



@bp.route('/mypage/update_mypage')
def show_update_mypage():
    user, _ = auth_help.get_user_from_token()

    if user is None:
        return redirect('/login')
    is_login = False
    if user != None:
        is_login = True

    profile_img = user.get('profile_img_path', '/assets/img/avatar.jpg')
    nickname = user.get('nickname', '')

    return render_template('profile_edit.html',
                           isLogin=is_login,
                           profileImg=profile_img,
                           nickname=nickname)

@bp.route('/mypage/update_mypage', methods=['post'])
def change_pofile_img_path():
    user, error_msg = auth_help.get_user_from_token()
    if error_msg:
        return jsonify({'result': 'fail', 'msg': error_msg})

    new_nickname = request.form.get('nickname', '').strip()
    if not new_nickname:
        new_nickname = user.get('nickname')
    else:
        nickname_regex = r'^[a-zA-Z가-힣]{1,16}$'
        if not re.match(nickname_regex, new_nickname):
            return jsonify({'result': 'fail', 'msg': "닉네임 형식이 올바르지 않습니다."})

    image_file = request.files.get('image')
    is_default = request.form.get('is_default') == 'true'

    if is_default:
        saved_file_path = 'assets/img/avatar.jpg'
    elif image_file and image_file.filename != '':
        saved_file_path = handle_image.save_image(request.files, type="profile")
    else:
        saved_file_path = user.get('profile_img_path')

    db.user.update_one(
        {'_id': user['_id']},
        {'$set': {
            'nickname': new_nickname,
            'profile_img_path': saved_file_path
        }}
    )
    return jsonify({'result': 'success', 'msg': '변경사항이 저장되었습니다!'})

def delete_user():
    
    return jsonify({'result': 'success', 'msg': '아이디 삭제 완료!'})

@bp.route('/logout')
def logout():
    res = make_response(jsonify({'result': 'success', 'msg': '로그아웃 되었습니다!'}))
    res.delete_cookie('mytoken')
    
    return res