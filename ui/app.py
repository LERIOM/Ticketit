"""Interface analyste. Squelette : file des tickets, validation, audit à l'étape 4."""
import os

import httpx
import streamlit as st

ENGINE_URL = os.environ.get("ENGINE_URL", "http://localhost:8000")

st.set_page_config(page_title="TicketIt", layout="wide")
st.title("TicketIt")
try:
    st.success(f"Moteur : {httpx.get(f'{ENGINE_URL}/health', timeout=3).json()}")
except httpx.HTTPError as exc:
    st.error(f"Moteur injoignable : {exc}")
