import concurrent.futures
import inspect
import json

from includes.common import Common
from services.logger import Logger
from v1.handler import Handler

class Wrapper:

	def ListRequestWithTasks(x):

		try:
			tasks = []
			api_results = {}

			for t in json.loads(x['tasks']):
				api_results.update(Handler.ExtractRelevantMeta(t['meta']))
				
				tasks.append({
					'TaskId': str(t['task_id']),
					'Action': str(t['action']),
					'Display': str(t['display']),
					'Status': str(t['status']) if t['status'] else False,
					'Microservice': t['microservice'],
					'Meta': t['meta'],
					'LastUpdated': str(Common.FormatDateTime(t['lu_date'])),
					'Date': str(Common.FormatDateTime(t['date'])),
				})
			
			return {
				'RequestId': str(x['request_id']),
				'UserId': str(x['user_id']),
				'Action': str(x['action']),
				'Display': str(x['display']),
				'Status': str(x['status']) if x['status'] else False,
				'PercentageCompleted': round(x['percentage_completed']) if x['percentage_completed'] is not None else 0,
				'Payload': json.loads(x['payload']),
				'LastUpdated': str(Common.FormatDateTime(x['lu_date'])),
				'Date': str(Common.FormatDateTime(x['date'])),
				'Tasks': tasks,
				'Results': api_results
			}

		except Exception as e:
			Logger.CreateExceptionLog(inspect.stack()[0][3], str(e), 'ERROR - Could not wrap data')

			return False
	
	def ListRequest(x):
		
		try:
			return {
				'RequestId': str(x['request_id']),
				'UserId': str(x['user_id']),
				'Action': str(x['action']),
				'Display': str(x['display']),
				'Status': str(x['status']),
				'PercentageCompleted': round(x['percentage_completed']) if x['percentage_completed'] is not None else 0,
				'Payload': json.loads(x['payload']),
				'LastUpdated': str(x['lu_date']),
				'Date': str(x['date']),
			}
		
		except Exception as e:
			Logger.CreateExceptionLog(inspect.stack()[0][3],str(e),'ERROR - Could not wrap data')

			return False
		
	def ListTask(x):

		try:
			microservice = json.loads(x['microservice'])

			return {
				'RequestId': str(x['request_id']),
				'TaskId': str(x['task_id']),
				'Action': str(x['action']),
				'Status': str(x['status']),
				'Display': str(x['display']),
				'Service': microservice.get('Service'),
				'Endpoint': microservice.get('Endpoint'),
				'Method': microservice.get('Method'), 
				'Meta': json.loads(x['meta']),
				'Date': str(x['date']),
			}
		
		except Exception as e:
			Logger.CreateExceptionLog(inspect.stack()[0][3],str(e),'ERROR - Could not wrap data')

			return False
		
	def ListIncident(inc,x):

		try:
			microservice = json.loads(x['microservice'])

			return {
				'IncidentNumber': str(inc),
				'RequestId': str(x['request_id']),
				'TaskId': str(x['task_id']),
				'Microservice': microservice.get('Service'),
				'Endpoint': microservice.get('Endpoint')
			}
		
		except Exception as e:
			Logger.CreateExceptionLog(inspect.stack()[0][3],str(e),'ERROR - Could not wrap data')

			return False
		
	def Pagination(limit,offset,sort,result):

		return {
			"Page": offset,
			"Size": limit,
			"Total": result[0]['Total'] if result else 0,
			"Sort": sort if sort else {}
		}
		
	def Package(result,kind):

		data = []

		if type(result) != list:
			return data
		
		if kind not in [
			'list-requests',
			'list-tasks'
		]:
			return data

		threads = []
		
		with concurrent.futures.ThreadPoolExecutor() as executor:
			for x in result:
				if kind == 'list-requests':
					threads.append(executor.submit(Wrapper.ListRequest,x))

				if kind == 'list-tasks':
					threads.append(executor.submit(Wrapper.ListTask,x))

		for x in threads:
			z = x.result()

			if z:
				data.append(z)

		return data