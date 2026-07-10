import streamlit as st
import requests

# The URL of the Hugging Face Space
BASE_URL = "https://pliny-the-prompter-godmod3-api.hf.space"

def call_api(endpoint, payload):
    headers = {"Authorization": f"Bearer {st.secrets['HF_TOKEN']}"}
    response = requests.post(f"{BASE_URL}/{endpoint}", headers=headers, json=payload)
    return response.json()

st.title("My App using GodMod3 API")
if st.button("Run Model"):
    result = call_api("v1/completions", {"prompt": "Hello AI"})
    st.write(result)
