
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
    sql_interactions_table = """ CREATE TABLE IF NOT EXISTS interactions (
        id integer NOT NULL PRIMARY KEY,
        created_at timestamp NOT NULL,
        session_id integer NOT NULL,
        paper_id text NOT NULL
    ); """
    create_table(conn, sql_interactions_table)
except Error as e:
    print(traceback.format_exc())
finally:
    if conn:
        conn.close()