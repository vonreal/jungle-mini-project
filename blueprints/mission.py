from flask import Blueprint, request, jsonify
from db import db
from utils import handle_time

bp = Blueprint('mission', __name__)

def get_mission():
    if (mission := get_now_mission()) == None:
        return None

    feeds = list(db.feeds.find({'mission_id': mission['_id']}))
    mission['participants'] = len(feeds)

    return mission

def get_now_mission():
    now = handle_time.get_now()

    mission = db.missions.find_one({
        'start_date': {'$lte': now},
        'end_date': {'$gt': now}
    })

    return mission

# 미션을 생성한다.
@bp.route('/mission', methods=['POST'])
def save_mission():
    try:
        db.missions.insert_one({
            'content': request.form.get('content'),
            'start_date': handle_time.convert_datetime(request.form.get('start_date')),
            'end_date': handle_time.convert_datetime(request.form.get('end_date'))
        })
    except:
        return jsonify({'result': 'failure', 'msg': '미션 생성이 실패했습니다.'})
    return jsonify({'result': 'success', 'msg': '미션 생성이 성공했습니다.'})