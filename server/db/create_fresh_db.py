import json
import os
import time
import sqlite3
from sqlite3 import Error
import traceback
from utils import preprocess
from db_queries import DB_PATH, N_PAPERS

EARLY_STOP = 10000

if os.path.exists(DB_PATH):
    os.remove(DB_PATH)

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

def create_paper(conn, paper):
    """
    Create a new paper into the projects table
    :param conn:
    :param paper:
    :return: paper id
    """
    sql = """ INSERT INTO papers(id,title,authors,abstract,preprocessed_title,preprocessed_authors,preprocessed_abstract)
              VALUES(?,?,?,?,?,?,?) """
    cur = conn.cursor()
    cur.execute(sql, paper)
    conn.commit()
    return cur.lastrowid

def remove_duplicates(conn):
    """
    Delete duplicate row where duplicate is defined as having the same title.
    Keep row with max(ID).
    :param conn:
    """
    sql = """ DELETE FROM papers
    WHERE id NOT IN (
        SELECT max(id) FROM papers
        GROUP BY title
        );  """
    cur = conn.cursor()
    cur.execute(sql)
    conn.commit()
    return

conn = None
try:
    conn = sqlite3.connect(DB_PATH)

    sql_create_papers_table = """ CREATE TABLE IF NOT EXISTS papers (
        id text NOT NULL PRIMARY KEY,
        title text NOT NULL,
        authors text NOT NULL,
        abstract text NOT NULL,
        preprocessed_title text NOT NULL,
        preprocessed_authors text NOT NULL,
        preprocessed_abstract text NOT NULL
    ); """
    create_table(conn, sql_create_papers_table)

    sql_interactions_table = """ CREATE TABLE IF NOT EXISTS interactions (
        id integer NOT NULL PRIMARY KEY,
        created_at timestamp NOT NULL,
        session_id integer NOT NULL,
        paper_id text NOT NULL
    ); """
    create_table(conn, sql_interactions_table)

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
    
    start = time.time()
    i = 0
    with open('arxiv-metadata-oai-snapshot.json') as f:
        for line in f:
            # id: ArXiv ID (can be used to access the paper, see below)
            # - https://arxiv.org/abs/{id}: Page for this paper including its abstract and further links
            # - https://arxiv.org/pdf/{id}: Direct link to download the PDF
            # submitter: Who submitted the paper
            # authors: Authors of the paper
            # title: Title of the paper
            # comments: Additional info, such as number of pages and figures
            # journal-ref: Information about the journal the paper was published in
            # doi: [https://www.doi.org](Digital Object Identifier)
            # abstract: The abstract of the paper
            # categories: Categories / tags in the ArXiv system
            # versions: A version history
            paper = json.loads(line)
            id = paper["id"]
            title = paper["title"]
            authors = paper["authors"]
            abstract = paper["abstract"]
            preprocessed_title = preprocess(title)
            preprocessed_authors = authors.lower()
            preprocessed_abstract = preprocess(abstract)
            try:
                create_paper(conn, (id, title, authors, abstract, preprocessed_title, preprocessed_authors, preprocessed_abstract))
            except Error as e:
                print(traceback.format_exc())
            i += 1
            print(f"\rProcessed {i} out of {N_PAPERS} papers ({i/N_PAPERS * 100:0.3f}%).", end="")
            if i == EARLY_STOP:
                break
    print(f"\nTook {time.time() - start:0.3f}s to process {i} papers.")
    start = time.time()
    remove_duplicates(conn)
    print(f"Took {time.time() - start:0.3f}s to deduplicate {i} papers.")
except Error as e:
    print(traceback.format_exc())
finally:
    if conn:
        conn.close()