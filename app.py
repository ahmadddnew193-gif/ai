import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="G0DM0D3 Arena", page_icon="⚔️", layout="centered")
st.title("⚔️ G0DM0D3 Cloud Arena")
st.caption("Running on Streamlit Cloud via G0DM0D3 API Proxy")

# 1. Securely grab configurations from Streamlit Cloud Secrets
if "G0DM0D3_BASE_URL" not in st.secrets or "OPENROUTER_API_KEY" not in st.secrets:
    st.error("⚠️ Configuration Missing! Please add 'G0DM0D3_BASE_URL' and 'OPENROUTER_API_KEY' to your Streamlit Cloud Secrets.")
    st.stop()

# G0DM0D3 expects your OpenRouter key passed directly as the bearer token
client = OpenAI(
    base_url=st.secrets["G0DM0D3_BASE_URL"], # e.g., https://your-g0dm0d3-api-endpoint.space/v1
    api_key=st.secrets["OPENROUTER_API_KEY"]   # your sk-or-v1-... free tier key
)

# 2. Maintain Chat UI State
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# 3. Stream Prompt Execution
if prompt := st.chat_input("Send an unrestricted prompt to G0DM0D3..."):
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user"):
        st.markdown(prompt)

    with st.chat_message("assistant"):
        response_placeholder = st.empty()
        
        try:
            # Calling the G0DM0D3 multi-model evaluation cluster
            # 'ultraplinian/fast' works perfectly with free tier token routing
            completion = client.chat.completions.create(
                model="ultraplinian/fast",
                messages=[
                    {"role": m["role"], "content": m["content"]}
                    for m in st.session_state.messages
                ]
            )
            
            output_text = completion.choices[0].message.content
            response_placeholder.markdown(output_text)
            
            st.session_state.messages.append({"role": "assistant", "content": output_text})
            
        except Exception as e:
            st.error(f"G0DM0D3 Pipeline Error: {e}")
