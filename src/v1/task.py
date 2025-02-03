import concurrent.futures

from includes.db import Db
from services.broadcast import Broadcast
from services.pagerduty import Pagerduty
from v1.handler import Handler
from v1.wrapper import Wrapper

class Task:

	def Update(request_id,task_id,status,payload,meta):

		api_data = {}
		api_data['ApiHttpResponse'] = 500
		api_data['ApiMessages'] = []
		api_data['ApiResult'] = []

		try:
			request_id = str(request_id)
			task_id = str(task_id)
			status = str(status).strip().lower()
		
		except:
			api_data['ApiHttpResponse'] = 400
			api_data['ApiMessages'] += ['INFO - Invalid arguments']

			return api_data
		
		if payload and type(payload) != dict:
			api_data['ApiHttpResponse'] = 400
			api_data['ApiMessages'] += ['INFO - Invalid payload']

			return api_data
		
		if meta and type(meta) != dict:
			api_data['ApiHttpResponse'] = 400
			api_data['ApiMessages'] += ['INFO - Invalid meta']

			return api_data
		
		executor = concurrent.futures.ThreadPoolExecutor()
		
		status = Task.AdjustStatus(status)

		if payload:
			executor.submit(Handler.MergePayload,request_id,task_id,payload)
		
		if meta:
			executor.submit(Handler.MergeMeta,request_id,task_id,meta)

		if status in ['wip','polling','failed']:
			result = Handler.SetStatus(request_id,task_id,status)
		
		if status in ['completed']:
			result = Handler.SetCompletedStatus(request_id,task_id)

		if not result:
			api_data['ApiHttpResponse'] = 500
			api_data['ApiMessages'] += ['ERROR - Could not update record']

			return api_data

		api_data['ApiHttpResponse'] = 204
		api_data['ApiMessages'] += ['INFO - Request processed successfully']

		return api_data

	def Process():
		
		api_data = {}
		api_data['ApiHttpResponse'] = 500
		api_data['ApiMessages'] = []
		api_data['ApiResult'] = []

		with concurrent.futures.ThreadPoolExecutor() as executor:
			executor.submit(Task.ProcessWip)
			executor.submit(Task.ProcessFailed)

		api_data['ApiHttpResponse'] = 202
		api_data['ApiMessages'] += ['INFO - Request processed successfully']

		return api_data
	
	def ProcessWip():
		
		query = """
			SELECT
				t1.request_id,
				t1.task_id,
				t1.action,
				t1.display,
				t1.meta,
				t1.microservice->>'$.Service' AS ms_service,
				t1.microservice->>'$.Endpoint' AS ms_endpoint,
				t1.microservice->>'$.Method' AS ms_method,
				t2.payload
			FROM tasks t1
			INNER JOIN requests t2 ON t1.request_id = t2.request_id
			WHERE t1.status = 'wip'
				AND t2.status = 'wip'
				AND t1.request_id NOT IN (
					SELECT request_id
					FROM tasks
					WHERE status IN ('failed', 'polling')
				)
			ORDER BY t1.task_id ASC
		"""

		tasks = Db.ExecuteQuery(query,None)

		if not tasks:
			return True
		
		with concurrent.futures.ThreadPoolExecutor() as executor:
			{executor.submit(Task.ManageWip, Handler.TransformData(task)): task for task in tasks}

		return True
	
	def ProcessFailed():
		
		query = """
			SELECT
				t1.request_id,
				t1.task_id,
				t1.action,
				t1.display,
				t1.microservice,
				t1.meta,
				t2.action AS request_action,
				t2.payload,
				t2.date
			FROM tasks t1
			INNER JOIN requests t2 ON t1.request_id = t2.request_id
			WHERE t1.status = 'failed'
				AND t1.meta->>'$.IncidentRequired' = '1'
				AND t1.meta->>'$.IncidentNumber' IS NULL
		"""

		tasks = Db.ExecuteQuery(query,None)

		if not tasks:
			return True
		
		with concurrent.futures.ThreadPoolExecutor() as executor:
			{executor.submit(Task.ManageFailed, Handler.TransformData(task)): task for task in tasks}

		return True
		
	def ManageWip(task):

		request_body = Handler.BuildRequestBody(
			task['request_id'],
			task['task_id'],
			task['action'],
			task['payload']
		)

		Handler.UpdatePayload(
			task['request_id'],
			task['task_id'],
			task['payload'],
			request_body
		)

		api_x, api_data = Handler.InvokeApi(
			task['ms_method'],
			task['ms_service'],
			task['ms_endpoint'],
			request_body,
			task['request_id'],
			task['task_id'],
		)

		if api_data is False:
			return Handler.SetStatus(
				task['request_id'],
				task['task_id'],
				'failed'
			)
		
		if int(api_x) in {209}:
			return Handler.SetCompletedStatus(
				task['request_id'],
				task['task_id']
			)
		
		if api_data and task['meta']['MergeIntoPayload'] == 1:
			Handler.MergePayload(
				task['request_id'],
				task['task_id'],
				api_data
			)

		if api_data and task['meta']['MergeIntoMeta'] == 1:
			Handler.MergeMeta(
				task['request_id'],
				task['task_id'],
				api_data
			)

		if task['meta']['PollingRequired'] == 1:
			return Handler.SetStatus(
				task['request_id'],
				task['task_id'],
				'polling'
			)
		
		return Handler.SetCompletedStatus(
			task['request_id'],
			task['task_id']
		)
	
	def ManageFailed(task):
		
		incident = Pagerduty.CreateIncident(
			task['request_id'],
			task['task_id'],
			task['payload']
		)

		if not incident:
			return False

		executor = concurrent.futures.ThreadPoolExecutor()
		executor.submit(Broadcast.AlertAlfred, Wrapper.ListIncident(incident, task))
		
		query = """
			UPDATE tasks
			SET meta = JSON_SET(meta, %s, %s)
			WHERE request_id = %s
				AND task_id = %s
		"""

		inputs = (
			"$.IncidentNumber",
			incident,
			task['request_id'],
			task['task_id']
		)

		return Db.ExecuteQuery(query,inputs,True)
	
	def AdjustStatus(status):

		data = {
			'complete': 'completed',
			'completed': 'completed',
			'success': 'completed',
			'skip': 'completed',
			'skipped': 'completed',
			'continue': 'completed',
			'continued': 'completed',
			'wip': 'polling',
			'restart': 'wip',
			'failed': 'failed',
			'fail': 'failed',
			'timeout': 'failed',
			'polling': 'polling',
		}

		return data.get(status,'failed')