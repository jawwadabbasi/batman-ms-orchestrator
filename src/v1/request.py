import inspect
import json
import settings

from includes.db import Db
from includes.common import Common
from services.logger import Logger
from services.justiceleague import JusticeLeague
from v1.sequence import Sequence
from v1.wrapper import Wrapper
from v1.handler import Handler

class Request:

	def Create(user_id,action,payload):

		api_data = {}
		api_data['ApiHttpResponse'] = 500
		api_data['ApiMessages'] = []
		api_data['ApiResult'] = []

		try:
			user_id = str(user_id)
			action = str(action).strip().lower()
		
		except:
			api_data['ApiHttpResponse'] = 400
			api_data['ApiMessages'] += ['INFO - Invalid arguments']

			return api_data
		
		if payload and type(payload) != dict:
			api_data['ApiHttpResponse'] = 400
			api_data['ApiMessages'] += ['INFO - Invalid payload']

			return api_data
		
		tasks = Sequence.Tasks(action)

		if not tasks:
			api_data['ApiHttpResponse'] = 400
			api_data['ApiMessages'] += ['INFO - Action not supported']

			return api_data
		
		user_data = JusticeLeague.GetUser(user_id)

		if not user_data:
			api_data['ApiHttpResponse'] = 400
			api_data['ApiMessages'] += ['ERROR - Failed to get user data']

			return api_data
		
		payload = Handler.BuildInitialPayload(action,user_data,payload)

		if not payload:
			api_data['ApiHttpResponse'] = 500
			api_data['ApiMessages'] += ['ERROR - Failed to create request payload']

			return api_data

		query = """
			INSERT INTO requests
			SET user_id = %s,
				action = %s,
				display = %s,
				payload = %s,
				lu_date = NOW(),
				date = NOW()
		"""

		inputs = (
			user_id,
			action,
			Request.Display(action),
			json.dumps(payload)
		)

		request_id = Db.ExecuteQuery(query,inputs,True,row_id=True)

		if not request_id:
			api_data['ApiHttpResponse'] = 500
			api_data['ApiMessages'] += ['ERROR - Failed to insert request']

			return api_data
		
		result = Handler.PopulateTasks(request_id,tasks)

		if not result:
			Request.Delete(request_id)

			api_data['ApiHttpResponse'] = 500
			api_data['ApiMessages'] += ['ERROR - Could not create records']

			return api_data

		api_data['ApiHttpResponse'] = 201
		api_data['ApiMessages'] += ['INFO - Request processed successfully']

		return api_data
	
	def Update(request_id,status):

		api_data = {}
		api_data['ApiHttpResponse'] = 500
		api_data['ApiMessages'] = []
		api_data['ApiResult'] = []

		try:
			request_id = str(request_id)
			status = str(status).strip().lower()
		
		except:
			api_data['ApiHttpResponse'] = 400
			api_data['ApiMessages'] += ['INFO - Invalid arguments']

			return api_data
		
		query = """
			UPDATE requests
			SET status = %s,
				lu_date = NOW()
			WHERE request_id = %s
		"""

		inputs = (
			status,
			request_id,
		)

		result = Db.ExecuteQuery(query,inputs,True)

		if not result:
			api_data['ApiHttpResponse'] = 500
			api_data['ApiMessages'] += ['ERROR - Could not update record']

			return api_data

		api_data['ApiHttpResponse'] = 204
		api_data['ApiMessages'] += ['INFO - Request processed successfully']

		return api_data
	
	def Get(request_id):

		api_data = {}
		api_data['ApiHttpResponse'] = 500
		api_data['ApiMessages'] = []
		api_data['ApiResult'] = []

		try:
			request_id = str(request_id)
		
		except:
			api_data['ApiHttpResponse'] = 400
			api_data['ApiMessages'] += ['INFO - Invalid arguments']

			return api_data
		
		query = """
			SELECT
				t1.*,
				(
					SELECT JSON_ARRAYAGG(JSON_OBJECT(
						'request_id', t2.request_id,
						'task_id', t2.task_id,
						'action', t2.action,
						'display', t2.display,
						'status', t2.status,
						'microservice', t2.microservice,
						'meta', t2.meta,
						'lu_date', t2.lu_date,
						'date', t2.date
					))
					FROM tasks t2
					WHERE t2.request_id = t1.request_id
					ORDER BY t2.task_id ASC
				) AS tasks,
				(COUNT(CASE WHEN t2.status = 'completed' THEN 1 END) / COUNT(*)) * 100 AS percentage_completed
			FROM requests t1
			JOIN tasks t2 on t1.request_id = t2.request_id
			WHERE t1.request_id = %s
			GROUP BY t1.request_id
			ORDER BY t1.request_id ASC
		"""

		inputs = (
			request_id,
		)

		result = Db.ExecuteQuery(query,inputs)

		if result is False:
			api_data['ApiHttpResponse'] = 500
			api_data['ApiMessages'] += ['ERROR - Could not retrieve record']

			return api_data

		if not result:
			api_data['ApiHttpResponse'] = 409
			api_data['ApiMessages'] += ['INFO - No records found']

			return api_data

		api_data['ApiHttpResponse'] = 200
		api_data['ApiMessages'] += ['INFO - Request processed successfully']
		api_data['ApiResult'] = Wrapper.ListRequestWithTasks(result[0])

		return api_data
	
	def List(filters,sort,limit,offset,datetime):

		api_data = {}
		api_data['ApiHttpResponse'] = 500
		api_data['ApiMessages'] = []
		api_data['ApiResult'] = []
		api_data['ApiMeta'] = []

		try:
			limit = int(limit) if limit else settings.REQUESTS_LIMIT
			offset = int(offset) if offset else 1
			datetime = str(datetime) if datetime else Common.Datetime()
			filters = Common.ParseDataToDict(filters)
			sort = Common.ParseDataToDict(sort)
		
		except:
			api_data['ApiHttpResponse'] = 400
			api_data['ApiMessages'] += ['INFO - Invalid arguments']

			return api_data
		
		query = """
			SELECT 
				t1.*,
				COUNT(*) OVER() as Total,
				(
					SELECT (COUNT(CASE WHEN t2.status = 'completed' THEN 1 END) / COUNT(*)) * 100
					FROM tasks t2 
					WHERE t2.request_id = t1.request_id
				) AS percentage_completed
			FROM requests t1
			WHERE date < %s
				{}
			{}
			LIMIT %s
			OFFSET %s
		""".format(
				Request.TranslateFilters(filters),
				Request.TranslateSort(sort)
			)

		inputs = (
			datetime,
			limit,
			(offset - 1) * limit
		)

		result = Db.ExecuteQuery(query,inputs)

		if result is False:
			api_data['ApiHttpResponse'] = 500
			api_data['ApiMessages'] += ['ERROR - Could not retrieve records']

			return api_data

		if not result:
			api_data['ApiHttpResponse'] = 200
			api_data['ApiMessages'] += ['INFO - No records found']

			return api_data

		if result:
			api_data['ApiHttpResponse'] = 200
			api_data['ApiMessages'] += ['INFO - Request processed successfully']
			api_data['ApiResult'] =  Wrapper.Package(result,'list-requests')
			api_data['ApiMeta'] = Wrapper.Pagination(limit,offset,sort,result)

			return api_data
	
	def Group(filters,datetime):

		api_data = {}
		api_data['ApiHttpResponse'] = 500
		api_data['ApiMessages'] = []
		api_data['ApiResult'] = []
		api_data['ApiMeta'] = []

		try:
			datetime = str(datetime) if datetime else Common.Datetime()
			filters = Common.ParseDataToDict(filters)
		
		except:
			api_data['ApiHttpResponse'] = 400
			api_data['ApiMessages'] += ['INFO - Invalid arguments']

			return api_data
		
		query = """
			SELECT 
				t1.action,
				COUNT(*) AS request_count
			FROM requests t1
			WHERE date < %s
				{}
			GROUP BY
				action
		""".format(
				Request.TranslateFilters(filters)
			)

		inputs = (
			datetime,
		)

		result = Db.ExecuteQuery(query,inputs)

		if result is False:
			api_data['ApiHttpResponse'] = 500
			api_data['ApiMessages'] += ['ERROR - Could not retrieve records']

			return api_data

		if not result:
			api_data['ApiHttpResponse'] = 409
			api_data['ApiMessages'] += ['INFO - No records found']

			return api_data

		api_data['ApiHttpResponse'] = 200
		api_data['ApiMessages'] += ['INFO - Request processed successfully']
		api_data['ApiResult'] =  Wrapper.Package(result,'group-requests')

		return api_data
	
	def Delete(request_id):

		query = """
			DELETE
			FROM requests
			WHERE request_id = %s
		"""

		inputs = (
			request_id,
		)

		return Db.ExecuteQuery(query,inputs,True)
	
	def TranslateFilters(filters):
		
		if not filters:
			return ''
		
		try:
			query = ''

			for k, v in filters.items():

				if not v:
					continue
				
				if isinstance(v, (list, tuple)):
					or_query = ' OR '.join([f"{k} = '{val}'" for val in v])

					query += f" AND ({or_query})"
				
				else:
					query += f" AND {k} = '{v}'"

			return query.strip()

		except Exception as e:
			Logger.CreateExceptionLog(inspect.stack()[0][3], str(e), 'ERROR - Could not translate filters')

			return ''
		
	def TranslateSort(sort):

		if not sort:
			return ''

		try:
			clause = []

			for k, v in sort.items():

				clause.append(f"{k} {v}")

			return 'ORDER BY ' + ', '.join(clause)

		except Exception as e:
			Logger.CreateExceptionLog(inspect.stack()[0][3], str(e), 'ERROR - Could not translate sorting criteria')

			return ''
		
	def Display(action):

		data = {
			'batcave-secure': 'Securing the Batcave',
			'batmobile-deploy': 'Deploying the Batmobile',
			'batmobile-refuel': 'Refueling the Batmobile',
			'batmobile-auto-repair': 'Auto-repairing the Batmobile',
			'batmobile-stealth-mode': 'Activating Batmobile Stealth Mode',
			'batwing-launch': 'Launching the Batwing',
			'batwing-cloak': 'Engaging Batwing Cloaking System',
			'batcomputer-scan': 'Scanning with the Batcomputer',
			'batcomputer-hack': 'Hacking Gothams criminal networks',
			'batcomputer-data-retrieve': 'Retrieving intelligence data',
			'batcomputer-enhance': 'Enhancing surveillance footage',
			'bat-signal-activate': 'Activating the Bat-Signal',
			'bat-signal-disable': 'Disabling the Bat-Signal',
			'batgrapple-launch': 'Launching Batgrapple',
			'batarang-deploy': 'Deploying Batarang',
			'bat-smoke-bomb': 'Detonating Smoke Bomb',
			'bat-stealth-mode': 'Entering Stealth Mode',
			'bat-tracking-device': 'Planting a Tracking Device',
			'bat-detective-mode': 'Enabling Detective Mode',
			'bat-utility-belt-reload': 'Reloading Utility Belt',
			'bat-combat-engage': 'Engaging in Combat',
			'bat-evade': 'Performing an Evasive Maneuver',
			'bat-interrogation-mode': 'Activating Interrogation Mode',
			'bat-shield-deploy': 'Deploying Bat Shield',
			'bat-code-encrypt': 'Encrypting Bat Network',
			'bat-code-decrypt': 'Decrypting Enemy Data',
			'bat-network-sweep': 'Performing a Network Sweep',
			'bat-satellite-link': 'Connecting to Bat-Satellite',
			'bat-city-patrol': 'Patrolling Gotham City',
			'bat-villain-identify': 'Identifying a Villain',
			'bat-trap-set': 'Setting up a Bat Trap',
			'bat-escape-route': 'Planning an Escape Route',
			'bat-justice-execute': 'Delivering Gotham Justice',
		}

		return data.get(action, 'Executing Batman Protocol')