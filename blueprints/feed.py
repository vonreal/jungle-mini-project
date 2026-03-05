from flask import Blueprint, request, jsonify, render_template, redirect
from db import db
from bson import ObjectId
from utils import handle_image, handle_time, auth_help
from blueprints import mission

bp = Blueprint('feed', __name__)

# [피드 전체 목록]
@bp.route('/feeds', methods=['POST'])
def get_feeds_with_order():
    order_type = get_order_type(request.form.get('orderType', 'LATEST'))
    feeds = get_feeds(order_type)

    if len(feeds) == 0:
        return jsonify({"result": "failure", "msg": "피드가 없습니다."})
        
    return jsonify({'result': 'success', 'feeds': feeds})

def get_feeds(order_type):
    feeds = get_ordered_feeds(order_type)

    for feed in feeds:
        # [피드] 피드 아이디, 유저 아이디, 생성일, 피드 이미지, 좋아요, 댓글 수
        feed['created_date'] = handle_time.display_time(feed['created_date'])
        feed['likes'] = [str(l) for l in feed.get('likes', [])]
        feed['comment_count'] = len(feed['comments'])
        for comment in feed.get('comments', []):
            comment['created_date'] = handle_time.display_time(comment['created_date'])

        # [유저] 프로필 이미지 경로, 닉네임 
        feed = get_user_data(feed, feed['user_id'])

    return feeds

def get_ordered_feeds(order_type):
    if (now_mission := mission.get_now_mission()) == None:
        return []

    if order_type in ('likes', 'comments'):
        feeds = list(db.feeds.aggregate([
            {"$match": {'mission_id': now_mission['_id']}},
            {"$addFields": {"sort_count": {"$size": f"${order_type}"}}},
            {"$sort": {"sort_count": -1, "created_date": -1}}
        ]))
    else:
        feeds = list(db.feeds.find({'mission_id': now_mission['_id']}).sort(order_type, -1))

    return feeds

def get_order_type(order_type):
    if order_type == 'COMMENT':
        return 'comments'
    elif order_type == 'LIKE':
        return 'likes'
    else:
        return 'created_date'

# [피드 상세]
@bp.route('/feed/<feed_id>')
def show_feed_page(feed_id):
    try:
        feed_id = ObjectId(feed_id)
    except:
        return redirect('/')
    
    if (feed := db.feeds.find_one({'_id': feed_id})) == None:
        return redirect('/')

    # [User] img, nickname
    feed = get_user_data(feed, feed['user_id'])
    feed['profile_img_path'] = "/" + feed['profile_img_path']

    # [Feed] mission, img, upload_at, like, comment
    feed = get_mission_data(feed, feed['mission_id'])
    feed['likes'] = [str(l) for l in feed.get('likes', [])]
    feed['created_date'] = handle_time.display_time(feed['created_date'])
    feed['comment_count'] = len(feed['comments'])
    for comment in feed['comments']:
        comment = get_user_data(comment, comment['user_id'])
        comment['profile_img_path'] = "/" + comment['profile_img_path']
        comment['created_date'] = handle_time.display_time(comment['created_date'])

    # [Current User]
    current_user, _ = auth_help.get_user_from_token()
    current_user_id = str(current_user['_id']) if current_user else None
    feed['user_id'] = str(feed['user_id'])

    return render_template('feed_detail.html', feed=feed, current_user_id=current_user_id)

# [피드 작성]
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

# [피드 삭제]
@bp.route('/delete_feed', methods=['POST'])
def delete_feed():
    try:
        feed_id = ObjectId(request.form.get('feedId', ''))
    except:
        return jsonify({"result": "failure", "msg": "유효하지 않은 피드입니다."})
    
    result = db.feeds.delete_one({'_id': feed_id})

    if result.deleted_count == 0:
        return jsonify({"result": "failure", "msg": "존재하지 않은 피드입니다."})

    return jsonify({"result": "success", "msg": "피드를 삭제했습니다."})

# [댓글 작성]
@bp.route('/comment', methods=['POST'])
def comment_feed():
    user, msg = auth_help.get_user_from_token()

    if user == None:
        return jsonify({"result": "failure", "msg": msg})
    
    try:
        feed_id = ObjectId(request.form.get('feedId', ''))
    except:
        return jsonify({"result": "failure", "msg": "유효하지 않은 피드입니다."})
    
    if (comment := request.form.get('comment', '').strip()) == '':
        return jsonify({"result": "failure", "msg": "댓글을 입력해주세요."})
    
    result = db.feeds.update_one(
        {'_id': feed_id},
        {
            "$push": {
            "comments": {
                "_id": ObjectId(),
                "user_id": user['_id'],
                "created_date": handle_time.get_now(),
                "content": comment,
            }
        }
    })

    if result.matched_count == 0:
        return jsonify({"result": "failure", "msg": "댓글 작성에 실패했습니다."})

    return jsonify({"result": "success", "msg": "댓글을 작성했습니다."})

# [댓글 삭제]
@bp.route('/delete_comment', methods=['POST'])
def delete_comment():
    try:
        feed_id = ObjectId(request.form.get('feedId', ''))
    except:
        return jsonify({"result": "failure", "msg": "유효하지 않은 피드입니다."})
    
    try:
        comment_id = ObjectId(request.form.get('commentId', ''))
    except:
        return jsonify({"result": "failure", "msg": "유효하지 않은 댓글입니다."})
    
    result = db.feeds.update_one(
        {'_id': feed_id},
        {'$pull': {'comments': {'_id': comment_id}}}
    )

    if result.matched_count == 0:
        return jsonify({"result": "failure", "msg": "존재하지 않은 댓글입니다."})

    return jsonify({"result": "success", "msg": "댓글을 삭제했습니다."})

# [좋아요/좋아요 취소]
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
        update_result = db.feeds.update_one({"_id": feedId}, {"$pull": {"likes": uid}})
        if update_result.matched_count == 0:
            return jsonify({"result": "failure", "msg": "좋아요에 실패했습니다."}) 
        return jsonify({"result": "success", "msg": "좋아요를 취소했습니다."})
    else:
        result = db.feeds.update_one({"_id": feedId}, {"$addToSet": {"likes": uid}})
        if result.matched_count == 0:
            return jsonify({"result": "failure", "msg": "좋아요에 실패했습니다."})
        
    return jsonify({"result": "success", "msg": "좋아요를 눌렀습니다."})

# [기타]
def get_user_data(target, user_id):
    user = db.user.find_one({'_id': ObjectId(user_id)})

    if user == None:
        return target

    target['user_id'] = str(user['_id'])
    target['nickname'] = user['nickname']
    target['profile_img_path'] = user['profile_img_path']

    return target

def get_mission_data(target, mission_id):
    mission = db.missions.find_one({'_id': ObjectId(mission_id)})

    if mission == None:
        return target
    
    target['mission_id'] = mission['_id']
    target['mission'] = mission['content']

    return target
    
