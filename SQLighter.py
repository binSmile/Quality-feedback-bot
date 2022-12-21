import sqlite3

conn = sqlite3.connect('database.db', check_same_thread=False)
cursor = conn.cursor()

# def db_table_val(user_id: int, user_name: str, user_surname: str, username: str):
# 	cursor.execute('INSERT INTO answers (user_id, Goodway, CleanShowroom, WaitingQueueTerminal,WaitingQueueDispatcher,CleanWaitingQueue) VALUES (?, ?, ?, ?, ?, ?, ?)', (user_id, Goodway, CleanShowroom, WaitingQueueTerminal,WaitingQueueDispatcher,CleanWaitingQueue))
# 	conn.commit()




def db_admin_init(conn, adminslist):
	"""
	create table with admin list
	:param conn: sql connection cursor
	:param adminslist: telegram's id of admins
	:return:
	"""

    cursor.execute('CREATE TABLE "admins" ( \
	"id"	INTEGER UNIQUE, \
	"admin_id"	INTEGER, \
	PRIMARY KEY("id") );')
    conn.commit()
    defadmins = adminslist
    for adid in defadmins:
        cursor.execute(
            'INSERT INTO admins (admin_id) VALUES (%s)' % adid)
        conn.commit()


""" 
Initialize SQL-queary table
"""


AnswerTableQuery = """CREATE TABLE "answers" (
	"id"	INTEGER NOT NULL,
	"user_name"	TEXT,
	"user_surname"	TEXT,
	"username"	TEXT,
	"user_id"	INTEGER,
	"Goodway"	TEXT,
	"CleanShowroom"	TEXT,
	"WaitingQueueTerminal"	TEXT,
	"WaitingQueueDispatcher"	TEXT,
	"CleanWaitingQueue"	TEXT,
	"datetime"	TEXT,
	"ShowRoomPhoto"	INTEGER,
	"WaitingQueuePhoto"	INTEGER,
	PRIMARY KEY("id" AUTOINCREMENT)
);"""


# AnswerTableQuery = """CREATE TABLE "answers" (
# "id"	INTEGER NOT NULL,
# "user_id"	INTEGER,
# "Goodway"	INTEGER,
# "CleanShowroom"	INTEGER,
# "WaitingQueueTerminal"	INTEGER,
# "WaitingQueueDispatcher"	INTEGER,
# "CleanWaitingQueue"	INTEGER,
# PRIMARY KEY("id" AUTOINCREMENT)
# )"""