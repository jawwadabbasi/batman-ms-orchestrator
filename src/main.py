# Built with ingenuity,
# by Jawwad Abbasi (jawwad@kodelle.com)

# Initiates a Flask app to handle managed endpoints
# and relays to corresponding controller and module
# for processing.

import json
import settings
import sentry_sdk

from flask import Flask,Response,request,send_file
from sentry_sdk.integrations.flask import FlaskIntegration
from v1.controller import Ctrl_v1
from v2.controller import Ctrl_v2

sentry_sdk.init(
    dsn=settings.SENTRY_DSN,
    traces_sample_rate=settings.SENTRY_TRACES_SAMPLE_RATE,
    profiles_sample_rate=settings.SENTRY_PROFILES_SAMPLE_RATE,
    environment=settings.SENTRY_ENV,
    enable_tracing=True,
    integrations=[
        FlaskIntegration(transaction_style="url",),
    ]
)

app = Flask(__name__)

@app.errorhandler(404)
def RouteNotFound(e):
    return Response(None, status=400, mimetype='application/json')

####################################
# Supported endpoints for API v1
####################################
@app.route('/api/v1/Request/Create', methods=['POST'])
def CreateRequest():
    data = Ctrl_v1.CreateRequest(request.json)
    return Response(json.dumps(data), status=data['ApiHttpResponse'], mimetype='application/json')

@app.route('/api/v1/Request/Update', methods=['POST'])
def UpdateRequest():
    data = Ctrl_v1.UpdateRequest(request.json)
    return Response(json.dumps(data), status=data['ApiHttpResponse'], mimetype='application/json')

@app.route('/api/v1/Request/Get', methods=['GET'])
def GetRequest():
    data = Ctrl_v1.GetRequest(request.args)
    return Response(json.dumps(data), status=data['ApiHttpResponse'], mimetype='application/json')

@app.route('/api/v1/Request/List', methods=['GET'])
def ListRequests():
    data = Ctrl_v1.ListRequests(request.args)
    return Response(json.dumps(data), status=data['ApiHttpResponse'], mimetype='application/json')

@app.route('/api/v1/Task/Update', methods=['POST'])
def UpdateTask():
    data = Ctrl_v1.UpdateTask(request.json)
    return Response(json.dumps(data), status=data['ApiHttpResponse'], mimetype='application/json')

@app.route('/api/v1/Report/Get', methods=['GET'])
def GetReport():
    data = Ctrl_v1.GetReport(request.args)

    if data['ApiHttpResponse'] != 200:
        return Response(json.dumps(data), status=data['ApiHttpResponse'], mimetype='application/json')
    
    return send_file(data['FileContent'], mimetype='application/octet-stream', as_attachment=True, download_name=data['FileName'])

####################################
# Initiate web server
####################################
app.run(host='0.0.0.0', port=settings.FLASK_PORT, debug=settings.FLASK_DEBUG)