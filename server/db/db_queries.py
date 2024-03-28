import sqlite3
from sqlite3 import Error
import datetime
import traceback
import json

DB_PATH = r"database.db"
N_PAPERS = 2440876

def query(fn):
    conn = None
    try:
        conn = sqlite3.connect("db/"+DB_PATH, detect_types=sqlite3.PARSE_DECLTYPES | sqlite3.PARSE_COLNAMES)
        return fn(conn)
    except Error as e:
        print(traceback.format_exc())
    finally:
        if conn:
            conn.close()

def get_paper_by_id(conn, id):
    """
    Query paper matching ID
    :param conn: the Connection object
    :param id: the paper ID
    :return:
    """
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM papers WHERE id='{id}';")
    return cur.fetchall()

def get_all_paper_titles(conn, limit=10000):
    """
    Query all rows in the table
    :param conn: the Connection object
    :param limit: the maximum number of rows to return
    :return:
    """
    cur = conn.cursor()
    cur.execute(f"SELECT title FROM papers LIMIT {limit};")
    return cur.fetchall()

def get_all_matching_paper_titles(conn, substring, limit=10000):
    """
    Query all rows in the table that match the substring
    :param conn: the Connection object
    :param substring: the substring to match in paper title
    :param limit: the maximum number of rows to return
    :return:
    """
    cur = conn.cursor()
    cur.execute(f"SELECT title FROM papers WHERE title LIKE '%{substring}%' LIMIT {limit};")
    return cur.fetchall()

def get_preprocessed_papers_by_title(conn, titles):
    """
    Query all rows in the table that match the title
    :param conn: the Connection object
    :param titles: the list of titles to match exactly
    :return:
    """
    cur = conn.cursor()
    cur.execute(f"SELECT preprocessed_title, preprocessed_authors, preprocessed_abstract FROM papers WHERE title IN ({', '.join('?' for _ in titles)});", titles)
    return cur.fetchall()

def get_all_sessions(conn):
    """
    Query all sessions
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM session;")
    return cur.fetchall()

def get_history_for_session(conn, session_id):
    """
    Query all sessions
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute(f"SELECT * FROM session_history WHERE session_id={session_id};")
    return cur.fetchall()

def create_session(conn):
    """
    Create session
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute(f"INSERT INTO session DEFAULT VALUES;")
    conn.commit()
    return cur.lastrowid

def create_session_history(conn, session_id, keywords, selected_papers):
    """
    Create session
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute(f"INSERT INTO session_history (session_id, created_at, query) VALUES ({session_id}, '{datetime.datetime.now()}', '{json.dumps({'keywords': keywords, 'selected_papers': selected_papers})}');")
    conn.commit()
    return cur.lastrowid

    