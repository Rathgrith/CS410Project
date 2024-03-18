import json
import os
import sqlite3
from sqlite3 import Error
import traceback
from utils import preprocess
from db_queries import DB_PATH, N_PAPERS

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
            create_paper(conn, (id, title, authors, abstract, preprocessed_title, preprocessed_authors, preprocessed_abstract))
            i += 1
            print(f"\rProcessed {i} out of {N_PAPERS} papers ({i/N_PAPERS * 100:0.3f}%).", end="")
            if i == 500:
                break
    remove_duplicates(conn)
except Error as e:
    print(traceback.format_exc())
finally:
    if conn:
        conn.close()