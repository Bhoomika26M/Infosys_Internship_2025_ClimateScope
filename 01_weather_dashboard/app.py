import streamlit as st

st.set_page_config(page_title="Redirecting...", layout="wide")

st.markdown("""
    <meta http-equiv="refresh" content="0; url=./Home" />
""", unsafe_allow_html=True)
