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
            # 1. Connect directly to Pliny's public Hugging Face Space
            client = Client("pliny-the-prompter/godmod3-api")
            
            # 2. Query the Space endpoint using Gradio notation instead of OpenAI
            # Note: You can view the exact parameter names by clicking 'Use via API' 
            # at the very bottom of Pliny's Hugging Face Space page.
            result = client.predict(
                message=prompt,
                api_key=openrouter_key,
                model_tier="ultraplinian/fast", # Passing the free-tier racing engine string
                api_name="/predict" 
            )
            
            # 3. Handle and display the text output string
            output_text = result[0] if isinstance(result, tuple) else result
            response_placeholder.markdown(output_text)
            st.session_state.messages.append({"role": "assistant", "content": output_text})
            
        except Exception as e:
            st.error(f"Gradio Space Connection Failed: {e}")
