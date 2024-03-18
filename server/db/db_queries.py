import sqlite3
from sqlite3 import Error
import traceback

DB_PATH = r"database.db"
N_PAPERS = 2440876

def query(fn):
    conn = None
    try:
        conn = sqlite3.connect("db/"+DB_PATH)
        return fn(conn)
    except Error as e:
        print(traceback.format_exc())
    finally:
        if conn:
            conn.close()

def get_all_paper_titles(conn, limit=10000):
    """
    Query all rows in the table
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute(f"SELECT title FROM papers LIMIT {limit};")
    return cur.fetchall()

def get_all_matching_paper_titles(conn, substring, limit=10000):
    """
    Query all rows in the table that match the substring
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute(f"SELECT title FROM papers WHERE title LIKE '%{substring}%' LIMIT {limit};")
    return cur.fetchall()

def get_preprocessed_papers_by_title(conn, titles):
    """
    Query all rows in the table that match the title
    :param conn: the Connection object
    :return:
    """
    cur = conn.cursor()
    cur.execute(f"SELECT preprocessed_title, preprocessed_authors, preprocessed_abstract FROM papers WHERE title IN ({', '.join('?' for _ in titles)});", titles)
    return cur.fetchall()


    