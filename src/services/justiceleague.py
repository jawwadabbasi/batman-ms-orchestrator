import requests

class JusticeLeague:

	api_endpoint = 'http://batman-ms-justiceleague'

	def GetCompanyData(company_id):

		data = {
			'CompanyId': company_id
		}

		try:
			result = requests.get(f'{JusticeLeague.api_endpoint}/api/v1/Internal/Data',params = data,stream = True)

			return result.json()['ApiResult'] if result.ok else False

		except:
			return False
		
	def GetUser(user_id):

		data = {
			'UserId': user_id
		}

		try:
			result = requests.get(f'{JusticeLeague.api_endpoint}/api/v1/Internal/Get',params = data,stream = True)

			return result.json()['ApiResult'] if result.ok else False

		except:
			return False