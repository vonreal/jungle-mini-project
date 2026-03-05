from flask import Blueprint, request, jsonify, render_template
from db import db
from bson import ObjectId
from utils import handle_image, handle_time
from blueprints import mission

bp = Blueprint('feed', __name__)

# 현재 진행중인 미션 주제에 맞는 피드 전체 조회
# @bp.route('/feeds', methods=['GET'])
def get_feeds():
    feeds = list(db.feeds.find({}).sort('created_date', -1))

    if len(feeds) == 0:
        return []
        # return jsonify({"result": "failure", "msg": "피드가 없습니다."})

    for feed in feeds:
        feed['_id'] = str(feed['_id'])
        feed['user_id'] = str(feed['user_id'])

        # user = db.user.find_one({'_id': ObjectId(feed['user_id'])})

        # feed['profile_img'] = user['profile_img']
        # feed['nickname'] = user['nickname']

        feed['profile_img_path'] = ''
        feed['created_date'] = handle_time.display_time(feed['created_date'])
        feed['comment_count'] = len(feed['comments'])
        del feed['comments']
        del feed['mission_id']
        
    
    return feeds
    # return jsonify({'feed_total': len(feeds), 'feeds': feeds})

@bp.route('/feed')
def show_feed_page():
    return render_template('feed_detail.html')

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
        # user = db.user.find_one({'_id': ObjectId(comment['user_id'])})
        # feed['profile_img'] = user['profile_img']
        # feed['nickname'] = user['nickname']
    feed['mission_id'] = str(feed['mission_id'])
    mission = db.missions.find_one({'_id': ObjectId(feed['mission_id'])})
    if mission:
        feed['mission'] = mission['content']

    del feed['mission_id']
    feed['comment_count'] = len(feed['comments'])

    return jsonify({"result": feed})

@bp.route('/post')
def show_post_html():
    today_mission = mission.get_mission()
    return render_template('create.html', mission=today_mission)

@bp.route('/post', methods=['POST'])
def write_feed():
    try:
        user_id = ObjectId(request.form.get('userId', ''))
    except:
        return {'result': 'failure', 'msg': '올바르지 않은 사용자입니다.'}
    
    try:
        mission_id = ObjectId(request.form.get('missionId', ''))
    except:
        return {'result': 'failure', 'msg': '올바르지 않은 미션입니다.'}
        
    try:
        image_url = handle_image.save_image(request.files)
    except:
        return jsonify({'result': 'failure', 'msg': '이미지가 필요합니다.'})
    
    # existed_feed = db.feeds.find_one({'mission_id': mission_id, 'user_id': user_id})
    # if existed_feed:
    #     return jsonify({'result': 'failure', 'msg': '오늘은 이미 참여했습니다.\n하루에 한 번만 참여할 수 있습니다.'})

    try:
        db.feeds.insert_one({
            'mission_id': mission_id,
            'user_id': user_id,
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
    try:
        userId = ObjectId(request.form.get('userId', ''))
    except:
        return jsonify({"result": "failure", "msg": "유효하지 않은 사용자입니다."})
    
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
                "user_id": userId,
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
    try:
        userId = ObjectId(request.form.get('userId', ''))
    except:
        return jsonify({"result": "failure", "msg": "유효하지 않은 사용자입니다."})
    
    try:
        feedId = ObjectId(request.form.get('feedId', ''))
    except:
        return jsonify({"result": "failure", "msg": "유효하지 않은 피드입니다."})
    
    result = db.feeds.find_one({"_id": feedId, "likes": {"$in": [userId]}})

    if result:
        db.feeds.update_one({"_id": feedId}, {
        "$pull": {
            "likes": userId
        }
    })
        return jsonify({"result": "success", "msg": "좋아요를 취소했습니다."})
    
    result = db.feeds.update_one({"_id": feedId}, {
        "$addToSet": {
            "likes": userId
        }
    })

    if result.matched_count == 0:
        return jsonify({"result": "failure", "msg": "좋아요에 실패했습니다."})
    
    return jsonify({"result": "success", "msg": "좋아요를 눌렀습니다."})