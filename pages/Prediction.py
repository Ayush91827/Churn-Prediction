import streamlit as st
import pandas as pd
import joblib
import numpy as np
import psycopg2
import streamlit as st
import time

model = joblib.load("random_forest_pipeline.pkl")
threshold = joblib.load("rf_best_threshold.pkl")

def save_prediction(creditscore, balance, age, tenure, numofproducts, hascrcard, isactivemember, estimatedsalary, prediction, probability, model_version="rf_v1", latency_ms=0.0, status="success"):
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
           INSERT INTO prediction_logs (model_version, latency_ms, status)
           VALUES(%s,%s,%s)
           RETURNING log_id
       """,(model_version, latency_ms, status))
       log_id=cur.fetchone()[0]

       cur.execute("""
           INSERT INTO prediction_data(
               log_id, creditscore, balance, age, tenure, numofproducts, hascrcard, isactivemember, estimatedsalary, prediction, probability
           )
           VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)
       """, (log_id, creditscore, balance, age, tenure, numofproducts, hascrcard, isactivemember, estimatedsalary, prediction, probability))

       conn.commit()
       cur.close()
       conn.close()

       st.success("✅ Prediction Saved To Database")

st.markdown("<h1 style='text-align: center;'>📊 Prediction Page</h1>", unsafe_allow_html=True)

age = st.number_input("Age", 18, 100, 30)
gender = st.selectbox("Gender", ["Male", "Female"])
creditscore = st.slider("Credit Score", 350, 850, 500)
geography = st.selectbox("Geography", ["France", "Spain", "Germany"])
tenure = st.number_input("Tenure", 0, 10, 1)
balance = st.number_input("Balance", 0.0, 200000.0, 1000.0)
numofproducts = st.selectbox("Number Of Products", ["1", "2", "3", "4"])
hascrcard = st.selectbox("Has Credit Card ?", ["Yes", "No"])
isactivemember = st.selectbox("Is Active Member ?", ["Yes", "No"])
estimatedsalary = st.number_input("Estimated Salary", 0, 200000, 10000)


def create_features(df):
    df["creditscore_band"] = pd.cut(
        df["creditscore"], bins=[300, 500, 650, 850],
        labels=["Low", "Medium", "High"]
    )
    df["age_band"] = pd.cut(
            df["age"], bins=[18, 30, 40, 50, 60, 100],
            labels=["18-29", "30-39", "40-49", "50-59", "60+"]
    )
    df["tenure_band"] = pd.cut(
            df["tenure"], bins=[0, 3, 6, 10],
            labels=["0-3", "4-6", "7-10"]
    )

    balances = df.loc[df["balance"] > 0, "balance"]
    if balances.nunique() < 3:
            df.loc[df["balance"] == 0, "balance_band"] = "Zero"
            df.loc[df["balance"] > 0, "balance_band"] = "Medium"
    else:
            df.loc[df["balance"] == 0, "balance_band"] = "Zero"
            df.loc[df["balance"] > 0, "balance_band"] = pd.qcut(
                balances, q=3, labels=["Low", "Medium", "High"]
            ).astype(str)

    df["num_products_bands"] = df["numofproducts"].replace({
            1: "One", 2: "Two", 3: "ThreePlus", 4: "ThreePlus"
    })

    salaries = df["estimatedsalary"]
    if salaries.nunique() < 4:
            df["salary_band_model"] = "Q2"
    else:
            df["salary_band_model"] = pd.qcut(
                salaries, q=4, labels=["Q1", "Q2", "Q3", "Q4"]
            )
    df["salary_band_business"] = pd.cut(
            df["estimatedsalary"],
            bins=[0, 50000, 100000, 150000, 200000],
            labels=["Low", "Medium", "High", "Very High"],
            include_lowest=True
    )

    df["has_balance"] = (df["balance"] > 0).astype(int)

        # Add anomaly flags expected by pipeline
    df["surname_invalid"] = 0
    df["customerid_duplicate"] = 0
    return df

col1, col2, col3 =st.columns([1,2,1])
with col2:
       run_prediction=st.button("Run Prediction")
if run_prediction:
     input_data = pd.DataFrame({
            "creditscore": [creditscore],
            "geography": [geography],   # categorical
            "gender": [gender],         # categorical
            "age": [age],
            "tenure": [tenure],
            "balance": [balance],
            "numofproducts": [int(numofproducts)],  # ✅ numeric
            "hascrcard": [1 if hascrcard == "Yes" else 0],  # ✅ numeric
            "isactivemember": [1 if isactivemember == "Yes" else 0],  # ✅ numeric
            "estimatedsalary": [estimatedsalary]
        })

     hascrcard_bool=True if hascrcard=="Yes" else False
     isactivemember_bool=True if isactivemember=="Yes" else False

    
     input_data = create_features(input_data)

     start_time=time.time()

     proba = float(model.predict_proba(input_data)[:, 1][0])
     prediction = int(proba >= threshold)

     end_time=time.time()
     latency_ms=(end_time-start_time)*1000

    # --- Display Results ---
     st.metric("Churn Probability", f"{proba:.2f}")
     st.metric("Prediction", "Churn" if prediction == 1 else "No Churn")

     save_prediction(creditscore, balance, age, tenure, int(numofproducts), hascrcard_bool, isactivemember_bool, estimatedsalary, "Churn" if prediction==1 else "No Churn", proba, model_version="rf_v1", latency_ms=latency_ms, status="success")