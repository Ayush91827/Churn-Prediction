import psycopg2
import pandas as pd
import streamlit as st
import plotly.express as px

def load_predictions():
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
        SELECT pl.timestamp, pl.model_version, pl.latency_ms, pl.status,
               pd.age, pd.creditscore, pd.balance, pd.numofproducts,
               pd.hascrcard, pd.isactivemember, pd.estimatedsalary,
               pd.tenure, pd.prediction, pd.probability
        FROM prediction_logs pl
        JOIN prediction_data pd ON pl.log_id=pd.log_id
        ORDER BY pl.timestamp ASC
    """)

    rows=cur.fetchall()
    colnames=[desc[0] for desc in cur.description]
    cur.close()
    conn.close()

    return pd.DataFrame(rows, columns=colnames)

st.markdown("<h1 style='text-align: center;'>📈 Prediction Trends</h1>", unsafe_allow_html=True)
df=load_predictions()

latency_fig=px.line(
    df, x="timestamp", y="latency_ms", color="model_version",
    title="Model Latency Over Time"
)
st.plotly_chart(latency_fig, use_container_width=True)

prob_fig=px.line(
    df, x="timestamp", y="probability", color="prediction",
    title="Prediction Probability Trend"
)
st.plotly_chart(prob_fig, use_container_width=True)

count_fig=px.histogram(
    df, x="prediction",y="probability", color="prediction",
    title="Distribution Of Predictions"
)
st.plotly_chart(count_fig, use_container_width=True)