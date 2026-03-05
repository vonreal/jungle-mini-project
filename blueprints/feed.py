from flask import Blueprint, request, jsonify, render_template, redirect
from db import db
from bson import ObjectId
from utils import handle_image, handle_time, auth_help
from blueprints import mission

bp = Blueprint('feed', __name__)

# 현재 진행중인 미션 주제에 맞는 피드 전체 조회
# @bp.route('/feeds', methods=['GET'])
def get_feeds():
    now = handle_time.get_now()

    mission = db.missions.find_one({
        'start_date': {'$lte': now},
        'end_date': {'$gt': now}
    })

    if mission == None:
        return []

    feeds = list(db.feeds.find({'mission_id': mission['_id']}).sort('created_date', -1))

    if len(feeds) == 0:
        return []
        # return jsonify({"result": "failure", "msg": "피드가 없습니다."})

    for feed in feeds:
        feed['_id'] = str(feed['_id'])
        feed['user_id'] = str(feed['user_id'])

        user = db.user.find_one({'_id': ObjectId(feed['user_id'])})

        feed['nickname'] = user['nickname']

        feed['profile_img_path'] = ''
        feed['created_date'] = handle_time.display_time(feed['created_date'])
        feed['comment_count'] = len(feed['comments'])
        feed['likes'] = [str(l) for l in feed.get('likes', [])]
        del feed['comments']
        del feed['mission_id']


    return feeds
    # return jsonify({'feed_total': len(feeds), 'feeds': feeds})

@bp.route('/feeds', methods=['GET'])
def get_feeds_with_order():
    now = handle_time.get_now()

    mission = db.missions.find_one({
        'start_date': {'$lte': now},
        'end_date': {'$gt': now}
    })

    if mission == None:
        return []
    
    order_type = request.form.get('order_type', 'LATEST')

    if order_type == 'COMMNET':
        order_type = 'comments'
    elif order_type == 'LIKE':
        order_type = 'likes'
    else:
        order_type = 'created_date'

    if order_type in ('likes', 'comments'):
        feeds = list(db.feeds.aggregate([
            {"$addFields": {"sort_count": {"$size": f"${order_type}"}}},
            {"$sort": {"sort_count": -1}}
        ]))
    else:
        feeds = list(db.feeds.find({'mission_id': mission['_id']}).sort(order_type, -1))

    if len(feeds) == 0:
        return jsonify({"result": "failure", "msg": "피드가 없습니다."})

    for feed in feeds:
        feed['_id'] = str(feed['_id'])
        feed['user_id'] = str(feed['user_id'])

        user = db.user.find_one({'_id': ObjectId(feed['user_id'])})

        feed['profile_img'] = user['profile_img']
        feed['nickname'] = user['nickname']

        feed['profile_img_path'] = ''
        feed['created_date'] = handle_time.display_time(feed['created_date'])
        feed['comment_count'] = len(feed['comments'])
        del feed['comments']
        del feed['mission_id']
        
    return jsonify({'result': 'success', 'feed_total': len(feeds), 'feeds': feeds})

@bp.route('/feed/<feed_id>')
def show_feed_page(feed_id):
    feed = db.feeds.find_one({'_id': ObjectId(feed_id)})

    if feed == None:
        return redirect('/')

    mission = db.missions.find_one({'_id': ObjectId(feed['mission_id'])})
    if mission:
        feed['mission'] = mission['content']

    user = db.user.find_one({'_id': ObjectId(feed['user_id'])})
    feed['nickname'] = user['nickname']
    feed['user_id'] = str(feed['user_id'])
    feed['likes'] = [str(l) for l in feed.get('likes', [])]

    feed['created_date'] = handle_time.display_time(feed['created_date'])
    for comment in feed['comments']:
        user = db.user.find_one({'_id': ObjectId(comment['user_id'])})
        comment['nickname'] = user['nickname']
        comment['created_date'] = handle_time.display_time(comment['created_date'])

    current_user, _ = auth_help.get_user_from_token()
    current_user_id = str(current_user['_id']) if current_user else None

    return render_template('feed_detail.html', feed=feed, current_user_id=current_user_id)

def get_feed_data():
    try:
        feedId = ObjectId(request.form.get('feedId', ''))
    except:
        return None
    
    feed = db.feeds.find_one({"_id": feedId})

    if feed == None:
        return None
    feed['user_id'] = str(feed['user_id'])
    # user = db.user.find_one({'_id': ObjectId(feed['user_id'])})
    # feed['profile_img'] = user['profile_img']
    # feed['nickname'] = user['nickname']

    feed['created_date'] = handle_time.display_time(feed['created_date'])
    for comment in feed['comments']:
        comment['created_date'] = handle_time.display_time(comment['created_date'])
        # user = db.user.find_one({'_id': ObjectId(comment['user_id'])})
        # feed['profile_img'] = user['profile_img']
        # feed['nickname'] = user['nickname']
    feed['mission_id'] = str(feed['mission_id'])
    mission = db.missions.find_one({'_id': ObjectId(feed['mission_id'])})
    if mission:
        feed['mission'] = mission['content']

    del feed['mission_id']
    feed['comment_count'] = len(feed['comments'])

    return feed

@bp.route('/feed', methods=['GET'])
def get_feed():
    try:
        feedId = ObjectId(request.form.get('feedId', ''))
    except:
        return jsonify({"result": "failure", "msg": "유효하지 않은 피드입니다."})
    
    feed = db.feeds.find_one({"_id": feedId})

    if feed == None:
        return jsonify({"result": "failure", "msg": "존재하지 않는 피드입니다."})
    feed['user_id'] = str(feed['user_id'])
    # user = db.user.find_one({'_id': ObjectId(feed['user_id'])})
    # feed['profile_img'] = user['profile_img']
    # feed['nickname'] = user['nickname']

    feed['created_date'] = handle_time.display_time(feed['created_date'])
    for comment in feed['comments']:
        comment['created_date'] = handle_time.display_time(comment['created_date'])
        user = db.user.find_one({'_id': ObjectId(comment['user_id'])})
        feed['profile_img'] = user['profile_img']
        feed['nickname'] = user['nickname']
    feed['mission_id'] = str(feed['mission_id'])
    mission = db.missions.find_one({'_id': ObjectId(feed['mission_id'])})
    if mission:
        feed['mission'] = mission['content']

    del feed['mission_id']
    feed['comment_count'] = len(feed['comments'])

    return jsonify({"result": feed})

@bp.route('/post')
def show_post_html():
    user, _ = auth_help.get_user_from_token()
    if user == None:
        return redirect('/')
    
    today_mission = mission.get_mission()
    return render_template('create.html', mission=today_mission)

@bp.route('/post', methods=['POST'])
def write_feed():
    user, msg = auth_help.get_user_from_token()

    if user == None:
        return jsonify({"result": "failure", "msg": msg})
    
    uid = user['_id']
    
    try:
        mission_id = ObjectId(request.form.get('missionId', ''))
    except:
        return {'result': 'failure', 'msg': '올바르지 않은 미션입니다.'}
        
    try:
        image_url = handle_image.save_image(request.files)
    except:
        return jsonify({'result': 'failure', 'msg': '이미지가 필요합니다.'})
    
    existed_feed = db.feeds.find_one({'mission_id': mission_id, 'user_id': uid})
    if existed_feed:
        return jsonify({'result': 'failure', 'msg': '오늘은 이미 참여했습니다.\n하루에 한 번만 참여할 수 있습니다.'})

    try:
        db.feeds.insert_one({
            'mission_id': mission_id,
            'user_id': uid,
            'feed_img_path': image_url,
            'likes': [],
            'comments': [],
            'created_date': handle_time.get_now(),
        })
    except:
        return jsonify({'result': 'failure', 'msg': '피드 작성에 실패했습니다.'})

    return jsonify({'result': 'success', 'msg': '피드를 작성했습니다.'})

@bp.route('/delete_feed', methods=['POST'])
def delete_feed():
    try:
        feedId = ObjectId(request.form.get('feedId', ''))
    except:
        return jsonify({"result": "failure", "msg": "유효하지 않은 피드입니다."})
    
    result = db.feeds.delete_one({'_id': feedId})

    if result.deleted_count == 0:
        return jsonify({"result": "failure", "msg": "존재하지 않은 피드입니다."})

    return jsonify({"result": "success", "msg": "피드를 삭제했습니다."})

@bp.route('/delete_comment', methods=['POST'])
def delete_comment():
    try:
        feedId = ObjectId(request.form.get('feedId', ''))
    except:
        return jsonify({"result": "failure", "msg": "유효하지 않은 피드입니다."})
    
    try:
        commentId = ObjectId(request.form.get('commentId', ''))
    except:
        return jsonify({"result": "failure", "msg": "유효하지 않은 댓글입니다."})
    
    result = db.feeds.update_one(
        {'_id': feedId},
        {'$pull': {'comments': {'_id': commentId}}}
    )

    if result.matched_count == 0:
        return jsonify({"result": "failure", "msg": "존재하지 않은 댓글입니다."})

    return jsonify({"result": "success", "msg": "댓글을 삭제했습니다."})

@bp.route('/comment', methods=['POST'])
def comment_feed():
    user, msg = auth_help.get_user_from_token()

    if user == None:
        return jsonify({"result": "failure", "msg": msg})
    
    uid = user['_id']
    
    try:
        feedId = ObjectId(request.form.get('feedId', ''))
    except:
        return jsonify({"result": "failure", "msg": "유효하지 않은 피드입니다."})
    
    comment = request.form.get('comment', '').strip()

    if comment == '':
        return jsonify({"result": "failure", "msg": "댓글을 입력해주세요."})
    
    result = db.feeds.update_one({'_id': feedId},{
        "$push": {
            "comments": {
                "_id": ObjectId(),
                "user_id": uid,
                "created_date": handle_time.get_now(),
                "content": comment,
            }
        }
    })

    if result.matched_count == 0:
        return jsonify({"result": "failure", "msg": "댓글 작성에 실패했습니다."})

    return jsonify({"result": "success", "msg": "댓글을 작성했습니다."})

@bp.route('/like', methods=['POST'])
def like_feed():
    user, msg = auth_help.get_user_from_token()

    if user == None:
        return jsonify({"result": "failure", "msg": msg})
    
    try:
        feedId = ObjectId(request.form.get('feedId', ''))
    except:
        return jsonify({"result": "failure", "msg": "유효하지 않은 피드입니다."})
    
    uid = user['_id']
    
    result = db.feeds.find_one({"_id": feedId, "likes": {"$in": [uid]}})

    if result:
        db.feeds.update_one({"_id": feedId}, {
        "$pull": {
            "likes": uid
        }
    })
        return jsonify({"result": "success", "msg": "좋아요를 취소했습니다."})
    
    result = db.feeds.update_one({"_id": feedId}, {
        "$addToSet": {
            "likes": uid
        }
    })

    if result.matched_count == 0:
        return jsonify({"result": "failure", "msg": "좋아요에 실패했습니다."})
    
    return jsonify({"result": "success", "msg": "좋아요를 눌렀습니다."})