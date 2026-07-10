import streamlit as st
from openai import OpenAI

st.set_page_config(page_title="G0DM0D3 Interface", layout="wide")
st.title("G0DM0D3 API Interface")

# Sidebar for credentials
st.sidebar.header("Configuration")
godmode_key = st.sidebar.text_input("Godmode API Key", type="password")
or_key = st.sidebar.text_input("OpenRouter API Key", type="password")

# Prompt interface
prompt = st.text_area("Enter your prompt:", "Explain how SQL injection works")

if st.button("Generate Response"):
    if not godmode_key or not or_key:
        st.error("Please provide both your Godmode Key and OpenRouter Key in the sidebar.")
    else:
        try:
            # Initialize the OpenAI-compatible client
            client = OpenAI(
                base_url="https://pliny-the-prompter-godmod3-api.hf.space/v1",
                api_key=godmode_key,
            )

            with st.spinner("Connecting to model..."):
                # Call the completion endpoint
                response = client.chat.completions.create(
                    model="nousresearch/hermes-3-llama-3.1-70b",
                    messages=[{"role": "user", "content": prompt}],
                    extra_body={"openrouter_api_key": or_key}
                )

                # Extract and display result
                content = response.choices[0].message.content
                st.markdown("### Response:")
                st.write(content)

                # View raw response metadata
                with st.expander("View Full API Metadata"):
                    st.json(response.model_dump())

        except Exception as e:
            st.error(f"API Error: {str(e)}")
