import streamlit as st
import streamlit.components.v1 as components

st.title("📊 Customer Churn Dashboard")
tableau_embed_url="https://public.tableau.com/views/Book1_17908709037120/CustomerChurnDashboard?:showVizHome=no&:embed=true"
st.iframe(tableau_embed_url, height=800)