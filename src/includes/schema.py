import settings

from includes.db import Db

class Schema:

	def CreateDatabase():

		query = f"CREATE DATABASE IF NOT EXISTS {settings.DB_NAME} CHARACTER SET = utf8mb4 COLLATE = utf8mb4_unicode_ci"

		return Db.ExecuteQuery(query,None,True,True)

	def CreateTables():
		
		#########################################################################################
		query = """
			CREATE TABLE IF NOT EXISTS requests (
				request_id BIGINT NOT NULL PRIMARY KEY AUTO_INCREMENT,
				user_id VARCHAR(255) NOT NULL,
				action VARCHAR(255) NOT NULL,
				display VARCHAR(255) NOT NULL,
				payload JSON NOT NULL,
				status VARCHAR(255) DEFAULT 'wip',
				lu_date DATETIME NOT NULL,
				date DATETIME NOT NULL
			) ENGINE=INNODB;
		"""

		if Db.ExecuteQuery(query,None,True) is False:
			return False
		
		Db.ExecuteQuery("ALTER TABLE requests ADD INDEX request_id (request_id);",None,True)
		Db.ExecuteQuery("ALTER TABLE requests ADD INDEX user_id (user_id);",None,True)
		Db.ExecuteQuery("ALTER TABLE requests ADD INDEX action (action);",None,True)
		Db.ExecuteQuery("ALTER TABLE requests ADD INDEX display (display);",None,True)
		Db.ExecuteQuery("ALTER TABLE requests ADD INDEX status (status);",None,True)
		Db.ExecuteQuery("ALTER TABLE requests ADD INDEX lu_date (lu_date);",None,True)
		Db.ExecuteQuery("ALTER TABLE requests ADD INDEX date (date);",None,True)

		#########################################################################################

		#########################################################################################
		query = """
			CREATE TABLE IF NOT EXISTS tasks (
				request_id BIGINT NOT NULL,
				task_id INT NOT NULL,
				action VARCHAR(255) NOT NULL,
				display VARCHAR(255) NOT NULL,
				microservice JSON DEFAULT NULL,
				meta JSON DEFAULT NULL,
				status VARCHAR(255) DEFAULT NULL,
				lu_date DATETIME NOT NULL,
				date DATETIME NOT NULL,
				PRIMARY KEY (request_id, task_id)
			) ENGINE=INNODB;
		"""

		if Db.ExecuteQuery(query,None,True) is False:
			return False
		
		Db.ExecuteQuery("ALTER TABLE tasks ADD INDEX request_id (request_id);",None,True)
		Db.ExecuteQuery("ALTER TABLE tasks ADD INDEX task_id (task_id);",None,True)
		Db.ExecuteQuery("ALTER TABLE tasks ADD INDEX action (action);",None,True)
		Db.ExecuteQuery("ALTER TABLE tasks ADD INDEX display (display);",None,True)
		Db.ExecuteQuery("ALTER TABLE tasks ADD INDEX status (status);",None,True)
		Db.ExecuteQuery("ALTER TABLE tasks ADD INDEX lu_date (lu_date);",None,True)
		Db.ExecuteQuery("ALTER TABLE tasks ADD INDEX date (date);",None,True)
		#########################################################################################

		return True