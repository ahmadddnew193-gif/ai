import streamlit as st
import requests

st.set_page_config(page_title="GodMod3 Interface", layout="wide")

st.title("GodMod3 API Interface")

# --- Sidebar: API Configuration ---
st.sidebar.header("API Configuration")
# We use input fields so you can provide keys if secrets aren't set
hf_token = st.sidebar.text_input("Hugging Face Token", type="password", value=st.secrets.get("HF_TOKEN", ""))
or_key = st.sidebar.text_input("OpenRouter API Key", type="password", value=st.secrets.get("OPENROUTER_API_KEY", ""))

BASE_URL = "https://pliny-the-prompter-godmod3-api.hf.space"

def call_api(endpoint, payload):
    headers = {
        "Authorization": f"Bearer {hf_token}",
        "Content-Type": "application/json"
    }
    # Inject OpenRouter key if needed by the specific endpoint
    payload["openrouter_api_key"] = or_key
    
    response = requests.post(f"{BASE_URL}/{endpoint}", headers=headers, json=payload)
    return response

# --- Main App ---
prompt = st.text_area("Enter your prompt:", "Explain how SQL injection works")

if st.button("Send Request"):
    if not hf_token or not or_key:
        st.error("Please provide both your HF Token and OpenRouter Key in the sidebar.")
    else:
        with st.spinner("Communicating with GodMod3..."):
            try:
                # Example using a common endpoint
                payload = {"messages": [{"role": "user", "content": prompt}]}
                response = call_api("v1/chat/completions", payload)
                
                if response.status_code == 200:
                    data = response.json()
                    st.success("API Success!")
                    
                    # Display the full output dictionary for inspection
                    with st.expander("View Full API Response"):
                        st.json(data)
                        
                    # Display extracted content if available
                    if "choices" in data:
                        st.write("### Response:")
                        st.write(data['choices'][0]['message']['content'])
                else:
                    st.error(f"Error {response.status_code}: {response.text}")
                    
            except Exception as e:
                st.error(f"An unexpected error occurred: {e}")
