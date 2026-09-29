import psycopg2
from psycopg2 import pool
import streamlit as st

if "db_pool" not in st.session_state:
    st.session_state.db_pool=psycopg2.pool.SimpleConnectionPool(
        minconn=1,
        maxconn=10,
        host=st.secrets["postgres"]["host"],
        port=st.secrets["postgres"]["port"],
        dbname=st.secrets["postgres"]["dbname"],
        user=st.secrets["postgres"]["user"],
        password=st.secrets["postgres"]["password"],
        sslmode=st.secrets["postgres"]["sslmode"]
    )

def run_query(sql, params=None):
    pool=st.session_state.db_pool
    conn=pool.getconn()
    try:
        cur=conn.cursor()
        cur.execute(sql,params)
        rows=cur.fetchall()
        cur.close()
        return rows
    finally:
        pool.putconn(conn)