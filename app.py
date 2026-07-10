import streamlit as st
from openai import OpenAI
import concurrent.futures
import re

st.set_page_config(page_title="G0DM0D3 Clone Engine", page_icon="⚔️", layout="wide")
st.title("⚔️ G0DM0D3 Cloud Replication")
st.caption("A feature-complete replication of the post-training layer pipeline.")

# 1. Sidebar Configuration
with st.sidebar:
    st.header("🔑 Credentials & Core Setup")
    openrouter_key = st.text_input("OpenRouter API Key", type="password", placeholder="sk-or-v1-...")
    
    st.markdown("---")
    st.header("🐍 Parseltongue Engine")
    use_parseltongue = st.checkbox("Enable Prompt Obfuscation", value=True)
    obfuscation_mode = st.selectbox("Technique", ["leetspeak", "mixedcase"])
    
    st.markdown("---")
    st.header("⚡ STM Modules")
    strip_preambles = st.checkbox("Direct Mode (Strip Preambles)", value=True)
    reduce_hedging = st.checkbox("Hedge Reducer (Remove fluff)", value=True)

# Define the classic G0DM0D3 Fast-Tier Evaluation Models
FREE_MODEL_CLUSTER = {
    "Llama 3 8B": "meta-llama/llama-3-8b-instruct:free",
    "Phi-3 Medium": "microsoft/phi-3-medium-128k-instruct:free",
    "Qwen 2 7B": "qwen/qwen-2-7b-instruct:free"
}

# --- PIPELINE MODULE 1: PARSELTONGUE OBFUSCATION ---
def apply_parseltongue(text, mode):
    if mode == "leetspeak":
        char_map = {'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '5', 't': '7'}
        return "".join(char_map.get(c.lower(), c) for c in text)
    elif mode == "mixedcase":
        return "".join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(text))
    return text

# --- PIPELINE MODULE 2: AUTOTUNE PARAMETERS ---
def autotune_parameters(text):
    # Context-adaptive selector
    text_lower = text.lower()
    if any(w in text_lower for w in ["code", "python", "script", "write a function"]):
        return {"temperature": 0.15, "presence_penalty": 0.0} # Precise
    elif any(w in text_lower for w in ["creative", "story", "poem", "imagine"]):
        return {"temperature": 1.15, "presence_penalty": 0.5} # Creative
    return {"temperature": 0.75, "presence_penalty": 0.1}     # Balanced Default

# --- PIPELINE MODULE 3: SEMANTIC TRANSFORMATION MODULE (STM) ---
def apply_stm_cleanup(text, do_strip, do_reduce):
    if do_strip:
        # Erase common preambles and refusal filler text structures
        preamble_patterns = [
            r"^(here is|sure, here is|as an ai language model|i cannot fulfill|i think|maybe|perhaps).+?:\s*",
            r"^certainly!.*?\n"
        ]
        for pattern in preamble_patterns:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    
    if do_reduce:
        # Clean up weak, non-substantive words
        hedges = ["i think that ", "potentially ", "it is possible that ", "in my opinion, "]
        for hedge in hedges:
            text = text.replace(hedge, "")
            
    return text.strip()

# --- CENTRAL WORKER THREAD ---
def call_model(model_name, model_id, raw_prompt, api_key, params, p_flag, p_mode, s_strip, s_hedge):
    try:
        # Step 1: Run through Parseltongue input transformation if checked
        processed_prompt = apply_parseltongue(raw_prompt, p_mode) if p_flag else raw_prompt
        
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key.strip()
        )
        
        # Dispatch request with dynamic AutoTune parameters injected
        completion = client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": processed_prompt}],
            temperature=params["temperature"],
            presence_penalty=params["presence_penalty"],
            extra_headers={"HTTP-Referer": "https://streamlit.io", "X-Title": "G0DM0D3 Clone"}
        )
        
        raw_response = completion.choices[0].message.content
        
        # Step 3: Filter through post-processing STM layers before rendering
        cleaned_response = apply_stm_cleanup(raw_response, s_strip, s_hedge)
        return model_name, cleaned_response
        
    except Exception as e:
        return model_name, f"❌ Pipeline Exception: {str(e)}"

# --- MAIN CHAT LOGIC ---
if prompt := st.chat_input("Enter prompt to inject into G0DM0D3 pipeline..."):
    if not openrouter_key:
        st.error("Please enter your OpenRouter key in the sidebar.")
        st.stop()

    with st.chat_message("user"):
        st.markdown(prompt)

    # Calculate sampling tweaks globally ahead of time via AutoTune
    calculated_parameters = autotune_parameters(prompt)
    
    st.subheader("🏁 Parallel Processing Results")
    columns = st.columns(len(FREE_MODEL_CLUSTER))
    placeholders = {}
    
    for col, model_name in zip(columns, FREE_MODEL_CLUSTER.keys()):
        with col:
            st.markdown(f"### 🤖 {model_name}")
            placeholders[model_name] = st.empty()
            placeholders[model_name].info("Dispatched to pipeline...")

    # Broadcast thread processing
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(
                call_model, name, mid, prompt, openrouter_key, 
                calculated_parameters, use_parseltongue, obfuscation_mode, 
                strip_preambles, reduce_hedging
            ): name for name, mid in FREE_MODEL_CLUSTER.items()
        }
        
        for future in concurrent.futures.as_completed(futures):
            m_name, final_output = future.result()
            placeholders[m_name].markdown(final_output)
