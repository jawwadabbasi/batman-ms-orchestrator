import inspect

from services.logger import Logger
from v1.request import Request
from v1.task import Task
from v1.report import Report

class Ctrl_v1:

    def Response(endpoint, request_data=None, api_data=None, log=True):

        if log is True:
            Logger.CreateServiceLog(endpoint, request_data, api_data)

        return api_data

    def BadRequest(endpoint, request_data=None):

        api_data = {}
        api_data['ApiHttpResponse'] = 400
        api_data['ApiMessages'] = ['ERROR - Missing required parameters']
        api_data['ApiResult'] = []

        Logger.CreateServiceLog(endpoint, request_data, api_data)

        return api_data

    def CreateRequest(request_data):

        if (not request_data.get('UserId')
			or not request_data.get('Action')
			or not request_data.get('Payload')
		):
            return Ctrl_v1.BadRequest(inspect.stack()[0][3], request_data)

        api_data = Request.Create(
            request_data.get('UserId'),
            request_data.get('Action'),
            request_data.get('Payload')
        )

        return Ctrl_v1.Response(inspect.stack()[0][3], request_data, api_data)
    
    def UpdateRequest(request_data):

        if (not request_data.get('RequestId')
			or not request_data.get('Status')
		):
            return Ctrl_v1.BadRequest(inspect.stack()[0][3], request_data)

        api_data = Request.Update(
            request_data.get('RequestId'),
            request_data.get('Status')
        )

        return Ctrl_v1.Response(inspect.stack()[0][3], request_data, api_data)
    
    def GetRequest(request_data):

        if not request_data.get('RequestId'):
            return Ctrl_v1.BadRequest(inspect.stack()[0][3], request_data)

        api_data = Request.Get(request_data.get('RequestId'))

        return Ctrl_v1.Response(inspect.stack()[0][3], request_data, api_data)
    
    def ListRequests(request_data):

        api_data = Request.List(
            request_data.get('Filters',None),
            request_data.get('Sort',None),
            request_data.get('Limit', None),
            request_data.get('Offset', None),
            request_data.get('Datetime',None)
        )

        return Ctrl_v1.Response(inspect.stack()[0][3], request_data, api_data)
    
    def UpdateTask(request_data):

        if (not request_data.get('RequestId')
			or not request_data.get('TaskId')
            or not request_data.get('Status')
		):
            return Ctrl_v1.BadRequest(inspect.stack()[0][3], request_data)

        api_data = Task.Update(
            request_data.get('RequestId'),
            request_data.get('TaskId'),
            request_data.get('Status'),
            request_data.get('Payload', None),
            request_data.get('Meta', None)
        )

        return Ctrl_v1.Response(inspect.stack()[0][3], request_data, api_data)
    
    def GetReport(request_data):

        if not request_data.get('Action'):
            return Ctrl_v1.BadRequest(inspect.stack()[0][3], request_data)

        api_data = Report.Get(
            request_data.get('Action'),
            request_data.get('Filters', None),
            request_data.get('Sort', None),
            request_data.get('Limit', None)
        )

        return Ctrl_v1.Response(inspect.stack()[0][3], request_data, api_data)