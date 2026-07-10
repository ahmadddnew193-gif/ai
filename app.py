import streamlit as st
from openai import OpenAI

# 1. Page Setup
st.set_page_config(page_title="G0DM0D3 API Interface", layout="wide")
st.title("G0DM0D3 API Interface")

# 2. Sidebar Configuration
st.sidebar.header("Configuration")
# Use your OpenRouter API key here
openrouter_key = st.sidebar.text_input("OpenRouter API Key", type="password")
# If your specific Space requires a separate Godmode Key, enter it here.
# If not, leave it empty.
godmode_key = st.sidebar.text_input("Godmode API Key (if required)", type="password")

# 3. Prompt Input
prompt = st.text_area("Enter your prompt:", "Explain how SQL injection works")

# 4. API Logic
if st.button("Generate Response"):
    if not openrouter_key:
        st.error("Please provide your OpenRouter API Key in the sidebar.")
    else:
        try:
            # Initialize the OpenAI-compatible client pointing to your Space
            # Note: base_url must end in '/v1'
            client = OpenAI(
                base_url="https://pliny-the-prompter-godmod3-api.hf.space/v1",
                api_key=godmode_key if godmode_key else openrouter_key,
            )

            with st.spinner("Processing through G0DM0D3..."):
                # Call the completion endpoint
                response = client.chat.completions.create(
                    model="nousresearch/hermes-3-llama-3.1-70b",
                    messages=[{"role": "user", "content": prompt}],
                    # The OpenRouter key must be passed in the extra_body
                    extra_body={"openrouter_api_key": openrouter_key}
                )

                # Extract and display result
                content = response.choices[0].message.content
                st.markdown("### Response:")
                st.write(content)

                # Debugging/Metadata view
                with st.expander("View Full API Metadata"):
                    st.json(response.model_dump())

        except Exception as e:
            st.error(f"API Error: {str(e)}")
