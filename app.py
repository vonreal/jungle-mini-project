# [Import]
from flask import Flask, render_template, jsonify, request, send_from_directory
from flask.json.provider import JSONProvider
from bson import ObjectId
import json

from blueprints import auth, feed, mission, mypage

app = Flask(__name__)

# [Blueprint]
app.register_blueprint(auth.bp)
app.register_blueprint(feed.bp)
app.register_blueprint(mission.bp)
app.register_blueprint(mypage.bp)

# [Utils] JSON 처리
class CustomJSONEncoder(json.JSONEncoder):
    def default(self, o):
        if isinstance(o, ObjectId):
            return str(o)
        return json.JSONEncoder.default(self, o)


class CustomJSONProvider(JSONProvider):
    def dumps(self, obj, **kwargs):
        return json.dumps(obj, **kwargs, cls=CustomJSONEncoder)

    def loads(self, s, **kwargs):
        return json.loads(s, **kwargs)

app.json = CustomJSONProvider(app)

# 파일 크기 제한 (10MB)
app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024

@app.route('/assets/<path:filename>')
def serve_assets(filename):
    return send_from_directory('templates/assets', filename)

@app.route('/')
def hello_world():
    return render_template('./index.html')

if __name__ == '__main__':
    app.run('0.0.0.0', port=5001, debug=True)