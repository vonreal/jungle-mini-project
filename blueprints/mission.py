from flask import Blueprint, request, jsonify
from db import db
from utils import handle_time

bp = Blueprint('mission', __name__)

# 현재 시간에 활성화 된 미션을 불러온다.
@bp.route('/mission', methods=['GET'])
def load_mission():
    now = handle_time.get_now()

    mission = db.missions.find_one({
        'start_date': {'$lte': now},
        'end_date': {'$gt': now}
    })
    
    if mission:
        mission['_id'] = str(mission['_id'])
        mission['start_date'] = mission['start_date'].isoformat()
        mission['end_date'] = mission['end_date'].isoformat()
    else:
        return jsonify({'result': 'failure', 'msg': '오늘의 미션이 없습니다.'})

    return jsonify(mission)

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