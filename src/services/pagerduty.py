import settings
import requests

class Pagerduty:

	api_endpoint = 'http://batman-ms-pagerduty'

	def CreateIncident(request_id,task_id):

		data = {
			'Service': settings.SVC_NAME,
			'Meta': {
				'RequestId': request_id,
				'TaskId': task_id
			}
		}

		try:
			result = requests.post(f'{Pagerduty.api_endpoint}/api/v1/Incident/Create',json = data,stream = True)

			return True if result.ok else False

		except:
			return False