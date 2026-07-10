import streamlit as st
from openai import OpenAI

# Page setup
st.set_page_config(page_title="G0DM0D3 Interface", layout="wide")
st.title("G0DM0D3 API Interface")

# Configuration
st.sidebar.header("Configuration")
openrouter_key = st.sidebar.text_input("OpenRouter API Key", type="password")

# Prompt interface
prompt = st.text_area("Enter your prompt:", "Explain how SQL injection works")

if st.button("Generate Response"):
    if not openrouter_key:
        st.error("Please enter your OpenRouter API Key in the sidebar.")
    else:
        try:
            # Initialize the OpenAI-compatible client
            # The API extracts your credentials from this client initialization
            client = OpenAI(
                base_url="https://pliny-the-prompter-godmod3-api.hf.space/v1",
                api_key=openrouter_key, 
            )

            with st.spinner("Communicating with G0DM0D3..."):
                # Make the request
                # extra_body is where G0DM0D3 expects the OpenRouter key for routing/billing
                response = client.chat.completions.create(
                    model="nousresearch/hermes-3-llama-3.1-70b",
                    messages=[{"role": "user", "content": prompt}],
                    extra_body={"openrouter_api_key": openrouter_key}
                )

                # Output
                st.markdown("### Response:")
                st.write(response.choices[0].message.content)
                
        except Exception as e:
            st.error(f"API Error: {str(e)}")
