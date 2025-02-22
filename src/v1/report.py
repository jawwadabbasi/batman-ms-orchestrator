import json
import inspect
import csv
import concurrent.futures

from io import BytesIO
from io import StringIO
from includes.db import Db
from includes.common import Common
from services.logger import Logger

class Report:
	
	def Get(action,filters,sort,limit):

		api_data = {}
		api_data['ApiHttpResponse'] = 500
		api_data['ApiMessages'] = []
		api_data['FileContent'] = ''
		api_data['FileName'] =  'unknown.txt'

		try:
			action = str(action).strip().lower()
			filters = Common.ParseDataToDict(filters)
			sort = Common.ParseDataToDict(sort)
			limit = int(limit) if limit else False
		
		except:
			api_data['ApiHttpResponse'] = 400
			api_data['ApiMessages'] += ['INFO - Invalid arguments']

			return api_data
		
		result = Report.Lookup(action,filters,sort,limit)

		if not result:
			api_data['ApiHttpResponse'] = 400
			api_data['ApiMessages'] += ['ERROR - Failed to generate report']

			return api_data

		api_data['ApiHttpResponse'] = 200
		api_data['ApiMessages'] += ['INFO - Request processed successfully']
		api_data['FileContent'] =  result['FileContent']
		api_data['FileName'] =  result['FileName']

		return api_data
	
	def Lookup(action,filters,sort,limit):

		data = []

		if action == 'text-file':
			data = Report.GenerateTestTextFile()

		if action == 'csv-file':
			data = Report.GenerateTestCsvFile()

		else:
			data = Report.GenerateCsvFile(action,filters,sort,limit)

		return data
		
	def GenerateCsvFile(action,filters,sort,limit):

		query = """
			SELECT 
				t1.request_id,
				t1.action,
				t1.payload,
				t1.status,
				t1.date
			FROM requests t1
			WHERE action = %s
				{}
			{}
			{}
		""".format(
				Report.TranslateFilters(filters),
				Report.TranslateSort(sort),
				Report.TranslateLimit(limit)
			)

		inputs = (
			action,
		)

		results = Db.ExecuteQuery(query,inputs)

		if not results:
			return False
		
		csv_data = Report.CreateCsvFile(results,action)
		
		return csv_data
	
	def CreateCsvFile(records, action):

		try:
			file_name = f"Batman_Report_{action}_{Common.Datetime()}.csv"

			rows = []
			headers = set()

			with concurrent.futures.ThreadPoolExecutor() as executor:
				results = executor.map(Report.ProcessRecord, records)

				for row in results:
					headers.update(row.keys())
					rows.append(row)

			headers = sorted(headers)

			buffer = StringIO()
			writer = csv.DictWriter(buffer, fieldnames=headers)

			writer.writeheader()
			writer.writerows(rows)

			buffer.write(Report.Signature())

			binary_buffer = BytesIO(buffer.getvalue().encode('utf-8'))
			binary_buffer.seek(0)

			return {
				'FileContent': binary_buffer,
				'FileName': file_name
			}

		except Exception as e:
			Logger.CreateExceptionLog(inspect.stack()[0][3], str(e), 'ERROR - Could not generate CSV from payload')
			
			return False

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

		return 'ORDER BY date DESC'
	
	def TranslateLimit(limit):

		if not limit:
			return ''
		
		return f'LIMIT {limit}'
	
	def ProcessRecord(record):
		payload = json.loads(record['payload'])
		flattened_payload = Report.FlattenDict(payload)

		row = {**record, **flattened_payload}
		row.pop('payload', None)

		return row
	
	def FlattenDict(payload, parent_key='', separator='.'):
		
		items = []

		for key, value in payload.items():
			new_key = f"{parent_key}{separator}{key}" if parent_key else key
			
			if isinstance(value, dict):
				items.extend(Report.FlattenDict(value, new_key, separator).items())
			
			else:
				items.append((new_key, value if value not in ("", None) else "Not available"))
		
		return dict(items)
	
	def GenerateTestTextFile():
		
		try:
			file_content = "This is a test file created in-memory.\n\nGenerated by jawwad@kodelle.com"
			file_name = 'test.txt'

			in_memory_file = BytesIO()
			in_memory_file.write(file_content.encode('utf-8'))
			in_memory_file.seek(0)

			return {
				'FileContent': in_memory_file,
				'FileName': file_name
			}

		except Exception as e:
			Logger.CreateExceptionLog(inspect.stack()[0][3], str(e), 'ERROR - Could not generate test file')

			return False
		
	def GenerateTestCsvFile():

		try:
			file_name = 'test.csv'
			
			header_vals = ['column_1', 'column_2']
			value_vals = [['value1', 'value2'], ['value3', 'value4']]

			text_buffer = StringIO()
			writer = csv.writer(text_buffer)
			
			writer.writerow(header_vals)
			writer.writerows(value_vals)

			text_buffer.write(Report.Signature())

			binary_buffer = BytesIO(text_buffer.getvalue().encode('utf-8'))

			binary_buffer.seek(0)

			return {
				'FileContent': binary_buffer,
				'FileName': file_name
			}

		except Exception as e:
			Logger.CreateExceptionLog(inspect.stack()[0][3], str(e), 'ERROR - Could not generate test CSV file')

			return False
		
	def Signature():

		return "\n# This file was automatically generated via the Batman Portal. Coded by jawwad@kodelle.com\n"