
import json
import os
import time
import sqlite3
from sqlite3 import Error
import traceback
from utils import preprocess
from db_queries import DB_PATH

def create_table(conn, create_table_sql):
    """ create a table from the create_table_sql statement
    :param conn: Connection object
    :param create_table_sql: a CREATE TABLE statement
    :return:
    """
    try:
        c = conn.cursor()
        c.execute(create_table_sql)
    except Error as e:
        print(traceback.format_exc())

conn = None
try:
    conn = sqlite3.connect(DB_PATH)
    sql_create_session_table = """ CREATE TABLE IF NOT EXISTS session (
        id integer NOT NULL PRIMARY KEY
    ); """
    create_table(conn, sql_create_session_table)

    sql_create_session_history_table = """ CREATE TABLE IF NOT EXISTS session_history (
        id integer NOT NULL PRIMARY KEY,
        session_id integer NOT NULL,
        created_at timestamp NOT NULL,
        query text NOT NULL
    ); """
    create_table(conn, sql_create_session_history_table)
except Error as e:
    print(traceback.format_exc())
finally:
    if conn:
        conn.close()