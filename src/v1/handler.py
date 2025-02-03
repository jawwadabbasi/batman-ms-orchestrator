import requests
import inspect
import json

from services.logger import Logger
from services.justiceleague import JusticeLeague
from includes.common import Common
from includes.db import Db

class Handler:

	def InvokeApi(method,service,endpoint,request_body,rid,tid):

		if method == 'GET':

			try:
				result = requests.get(f"http://{service}{endpoint}",params=request_body,stream=True,timeout=30)

				return (result.status_code, result.json().get('ApiResult', True)) if result.ok else (result.status_code, False)

			except Exception as e:
				Logger.CreateExceptionLog(inspect.stack()[0][3], str(e), f"ERROR - {method} request to microservice {service} failed (RID{rid}, TID{tid})")

				return False, False
		
		if method == 'POST':

			try:
				result = requests.post(f"http://{service}{endpoint}",json=request_body,stream=True,timeout=30)

				return (result.status_code, result.json().get('ApiResult', True)) if result.ok else (result.status_code, False)
			
			except Exception as e:
				Logger.CreateExceptionLog(inspect.stack()[0][3], str(e), f"ERROR - {method} request to microservice {service} failed (RID{rid}, TID{tid})")

				return False, False
		
		Logger.CreateExceptionLog(inspect.stack()[0][3], f"ERROR - {method} request to microservice {service} failed (RID{rid}, TID{tid})", json.dumps(request_body))

		return False, False
	
	def PopulateTasks(request_id,tasks):

		query = """
			INSERT INTO tasks
			SET request_id = %s,
				task_id = %s,
				status = %s,
				action = %s,
				display = %s,
				microservice = %s,
				meta = %s,
				lu_date = NOW(),
				date = NOW()
		"""

		inputs = []

		for index, x in enumerate(tasks, start=1):
			status = 'wip' if index == 1 else None

			inputs.append((
				request_id,
				index,
				status,
				x['Action'],
				x['Display'],
				json.dumps(x['Microservice']),
				json.dumps(x['Meta'])
			))

		return Db.ExecuteQuery(query,inputs)
	
	def SetStatus(request_id,task_id,new_status):

		query = """
			SELECT status
			FROM tasks
			WHERE request_id = %s
				AND task_id = %s
		"""

		inputs = (
			request_id,
			task_id
		)

		result = Db.ExecuteQuery(query,inputs,True)
		
		if not result:
			return False
		
		if result[0]['status'] == 'completed':
			return True

		if result[0]['status'] == 'polling' and new_status == 'wip':
			return True

		query = """
			UPDATE tasks
			SET status = %s,
				lu_date = NOW()
			WHERE request_id = %s
				AND task_id = %s
		"""

		inputs = (
			new_status,
			request_id,
			task_id
		)

		if not Db.ExecuteQuery(query,inputs,True):
			return False
		
		if new_status in ['wip', 'failed']:
			query = """
				UPDATE requests
				SET status = %s,
					lu_date = NOW()
				WHERE request_id = %s
			"""

			inputs = (
				new_status,
				request_id,
			)

			return Db.ExecuteQuery(query,inputs,True)
		
		return True
	
	def SetCompletedStatus(request_id,task_id):

		query = """
			UPDATE tasks
			SET status = CASE 
				WHEN task_id = %s THEN 'completed'
				WHEN task_id = %s THEN 'wip'
			END,
			lu_date = NOW()
			WHERE request_id = %s
				AND task_id IN (%s, %s)
		"""

		inputs = (
			task_id,
			int(task_id) + 1,
			request_id,
			task_id,
			int(task_id) + 1
		)

		if not Db.ExecuteQuery(query,inputs,True):
			return False
		
		query = """
			UPDATE requests t1
			SET t1.status = CASE
				WHEN EXISTS (
					SELECT 1
					FROM tasks t2
					WHERE t2.request_id = t1.request_id 
					AND t2.status != 'completed'
				) THEN 'wip'
				ELSE 'completed'
			END,
			lu_date = NOW()
			WHERE t1.request_id = %s
		"""

		inputs = (
			request_id,
		)

		return Db.ExecuteQuery(query,inputs,True)
	
	def MergePayload(request_id,task_id,payload):
		
		query = """
			SELECT payload
			FROM requests
			WHERE request_id = %s
		"""

		inputs = (
			request_id,
		)

		result = Db.ExecuteQuery(query,inputs)

		if not result:
			return False
		
		try:
			c_payload = json.loads(result[0]['payload']) | payload

		except Exception as e:
			Logger.CreateExceptionLog(inspect.stack()[0][3], str(e), f"ERROR - Could not merge payload for RID#{request_id}, TID#{task_id}")

			return False

		query = """
			UPDATE requests
			SET payload = %s,
				lu_date = NOW()
			WHERE request_id = %s
		"""

		inputs = (
			json.dumps(c_payload),
			request_id
		)

		return Db.ExecuteQuery(query,inputs,True)
	
	def MergeMeta(request_id,task_id,meta):
		
		query = """
			SELECT meta
			FROM tasks
			WHERE request_id = %s
				AND task_id = %s
		"""

		inputs = (
			request_id,
			task_id,
		)

		result = Db.ExecuteQuery(query,inputs)

		if not result:
			return False
		
		try:
			c_meta = json.loads(result[0]['meta']) | meta

		except Exception as e:
			Logger.CreateExceptionLog(inspect.stack()[0][3], str(e), f"ERROR - Could not merge task for RID#{request_id}, TID#{task_id}")

			return False

		query = """
			UPDATE tasks
			SET meta = %s,
				lu_date = NOW()
			WHERE request_id = %s
				AND task_id = %s
		"""

		inputs = (
			json.dumps(c_meta),
			request_id,
			task_id
		)

		return Db.ExecuteQuery(query,inputs,True)
	
	def UpdatePayload(request_id,task_id,payload,request_body):

		if not isinstance(request_body, dict) or not isinstance(payload, dict):
			return False
		
		try:
			c_payload = payload | request_body

		except Exception as e:
			Logger.CreateExceptionLog(inspect.stack()[0][3], str(e), f"ERROR - Could not merge payload for RID#{request_id}, TID#{task_id}")

			return False

		query = """
			UPDATE requests
			SET payload = %s,
				lu_date = NOW()
			WHERE request_id = %s
		"""

		inputs = (
			json.dumps(c_payload),
			request_id
		)

		return Db.ExecuteQuery(query,inputs,True)
	
	def ExtractRelevantMeta(meta, exclude_keys=None):

		if exclude_keys is None:
			exclude_keys = {
				"IncidentRequired", 
				"MergeIntoPayload", 
				"MergeIntoMeta", 
				"PollingRequired"
			}
		
		return {key: value for key, value in meta.items() if key not in exclude_keys}
	
	def TransformData(data):

		if 'payload' in data:
			data['payload'] = Common.ParseDataToDict(data['payload'])

		if 'meta' in data:
			data['meta'] = Common.ParseDataToDict(data['meta'])

		return data

	def BuildInitialPayload(action,user_data,payload):

		if not 'RequestAction' in payload:
			payload['RequestAction'] = action

		if not 'UserData' in payload:
			payload['UserData'] = user_data
		
		return Handler.CompileData(payload)
	
	def BuildRequestBody(request_id,task_id,task_action,payload):

		payload = Handler.CompileData(payload)

		payload = Handler.CompileUniqueParameters(request_id,task_id,task_action,payload)
		
		return payload

	def CompileData(payload):

		if not 'JusticeLeague' in payload and 'JusticeLeagueId' in payload:
			payload['JusticeLeague'] = JusticeLeague.GetCompanyData(payload['JusticeLeagueId'])

		return payload
	
	def CompileUniqueParameters(request_id,task_id,task_action,payload):

		try:
			unique_params = {
				'RequestId': request_id,
				'TaskId': task_id,
				'TaskAction': task_action
			}
			
			payload.update(unique_params)

			return payload
		
		except Exception as e:
			Logger.CreateExceptionLog(inspect.stack()[0][3], str(e), "ERROR - Failed to compile unique parameters")

			return payload