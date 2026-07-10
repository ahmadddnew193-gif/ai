import streamlit as st
from gradio_client import Client

st.set_page_config(page_title="G0DM0D3 via HF Space", page_icon="⚔️")
st.title("⚔️ G0DM0D3 Space Bridge")

# UI Inputs for the user's OpenRouter token
with st.sidebar:
    st.header("Credentials")
    openrouter_key = st.text_input("OpenRouter API Key", type="password", placeholder="sk-or-v1-...")

if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

if prompt := st.chat_input("Enter your prompt..."):
    if not openrouter_key:
        st.error("Please enter your OpenRouter key in the sidebar.")
        st.stop()

    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        try:
            # Connect to Pliny's running space
            client = Client("pliny-the-prompter/godmod3-api")
            
            # Submitting arguments to match the UI layout order precisely:
            # 1. api_key (the Bearer token input box -> leave empty string)
            # 2. prompt (the text box input)
            # 3. speed_tier (the selection box -> "FAST")
            # 4. openrouter_key (passed as a header/token via client configuration or internal function)
            job = client.submit(
                "",                 # API KEY (Bearer token box) - left blank
                prompt,             # PROMPT box
                "FAST",             # SPEED TIER box (Matching the UI name 'FAST')
                api_name="/predict"
            )
            
            # Wait for the background worker to finish running the race
            result = job.result()
            
            output_text = result[0] if isinstance(result, tuple) else result
            response_placeholder.markdown(output_text)
            st.session_state.messages.append({"role": "assistant", "content": output_text})
            
        except Exception as e:
            st.error(f"Gradio Connection Error: {e}")
