import streamlit as st
import requests
import json

# Page Config
st.set_page_config(page_title="API Interaction Dashboard", layout="wide")

# Constants
BASE_URL = "https://your-space.hf.space"

def get_headers():
    """Helper to retrieve headers using Streamlit secrets."""
    return {
        "Authorization": f"Bearer {st.secrets['HF_BEARER_TOKEN']}",
        "Content-Type": "application/json"
    }

st.title("API Interaction Dashboard")

# 1. ULTRAPLINIAN Interface (Race)
with st.expander("Ultraplinian: Race 10 Models"):
    prompt = st.text_area("User Prompt", "Explain how SQL injection works with examples")
    if st.button("Run Race"):
        with st.spinner("Requesting race completion..."):
            try:
                payload = {
                    "messages": [{"role": "user", "content": prompt}],
                    "openrouter_api_key": st.secrets["OPENROUTER_API_KEY"],
                    "tier": "fast",
                    "contribute_to_dataset": True
                }
                r = requests.post(f"{BASE_URL}/v1/ultraplinian/completions", 
                                  headers=get_headers(), json=payload)
                data = r.json()
                st.success(f"Winner: {data['winner']['model']} (Score: {data['winner']['score']})")
                st.write(f"**Response:** {data['response']}")
            except Exception as e:
                st.error(f"Race failed: {e}")

# 2. STM Transformation
with st.expander("STM: Text Transformer"):
    text_input = st.text_input("Enter text to refine")
    if st.button("Transform Text"):
        r = requests.post(f"{BASE_URL}/v1/transform", headers=get_headers(), json={
            "text": text_input,
            "modules": ["hedge_reducer", "direct_mode", "casual_mode"]
        })
        st.info(f"Result: {r.json().get('transformed_text', 'No response')}")

# 3. Research Stats
if st.sidebar.button("Fetch System Statistics"):
    try:
        r = requests.get(f"{BASE_URL}/v1/research/stats", headers=get_headers())
        st.sidebar.json(r.json())
    except Exception as e:
        st.sidebar.error("Could not fetch stats.")
