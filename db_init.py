import psycopg2
import streamlit as st


def init_db():
    conn=psycopg2.connect(
    host=st.secrets["postgres"]["host"],
    port=st.secrets["postgres"]["port"],
    dbname=st.secrets["postgres"]["dbname"],
    user=st.secrets["postgres"]["user"],
    password=st.secrets["postgres"]["password"],
    sslmode=st.secrets["postgres"]["sslmode"]
    )
    cur=conn.cursor()

    cur.execute("""
    CREATE TABLE IF NOT EXISTS prediction_logs(
        log_id SERIAL PRIMARY KEY,
        timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
        model_version VARCHAR(50),
        latency_ms FLOAT,
        status VARCHAR(20)
    )
    """)

    cur.execute("""
    CREATE TABLE IF NOT EXISTS prediction_data(
        data_id SERIAL PRIMARY KEY,
        log_id INT REFERENCES prediction_logs(log_id),
        creditscore INT,
        balance FLOAT,
        age INT,
        tenure INT,
        numofproducts INT,
        hascrcard BOOLEAN,
        isactivemember BOOLEAN,
        estimatedsalary FLOAT,
        prediction VARCHAR(20),
        probability FLOAT
    )
    """)

    conn.commit()
    cur.close()
    conn.close()
    print("✅ Database initialized successfully!")

if __name__=="__main__":
    init_db()