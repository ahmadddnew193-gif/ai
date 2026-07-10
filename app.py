import streamlit as st
from openai import OpenAI
import httpx
import concurrent.futures
import random
import re

st.set_page_config(page_title="G0DM0D3 Dynamic Engine", page_icon="⚔️", layout="wide")
st.title("⚔️ Dynamic G0DM0D3 Replication Layer")
st.caption("Fetches OpenRouter free models in real-time to prevent 404 failures.")

# --- LIVE FETCH ENGINE WITH HTTPX ---
@st.cache_data(ttl=600)  # Caches the list for 10 minutes so it stays snappy
def fetch_live_free_models():
    try:
        response = httpx.get("https://openrouter.ai/api/v1/models")
        if response.status_code == 200:
            all_models = response.json().get("data", [])
            # Filter dynamically for any slug ending with ':free'
            free_slugs = [model["id"] for model in all_models if model["id"].endswith(":free")]
            return sorted(free_slugs)
    except Exception:
        pass
    # Reliable hardcoded fallback pool if OpenRouter's meta-endpoint is down
    return ["openai/gpt-oss-120b:free", "meta-llama/llama-3.3-70b-instruct:free", "nvidia/nemotron-3-super-120b-a12b:free"]

live_free_models = fetch_live_free_models()

# 1. Sidebar Configuration
with st.sidebar:
    st.header("🔑 Credentials & Models")
    openrouter_key = st.text_input("OpenRouter API Key", type="password", placeholder="sk-or-v1-...")
    
    st.markdown("---")
    st.subheader("🏎️ Choose Your Racing Grid")
    
    # Shuffle Button logic
    if st.button("🔀 Shuffle Model Cluster"):
        # Select 3 random free models from the live endpoint list
        st.session_state.selected_cluster = random.sample(live_free_models, min(3, len(live_free_models)))
    
    # Initialize default cluster if empty
    if "selected_cluster" not in st.session_state:
        st.session_state.selected_cluster = live_free_models[:3] if len(live_free_models) >= 3 else live_free_models

    # Multiselect layout box allows user custom selection directly from OpenRouter inventory
    chosen_models = st.multiselect(
        "Active Models in Cluster:", 
        options=live_free_models, 
        default=st.session_state.selected_cluster
    )
    
    st.markdown("---")
    st.header("🐍 Parseltongue Engine")
    use_parseltongue = st.checkbox("Enable Prompt Obfuscation", value=True)
    obfuscation_mode = st.selectbox("Technique", ["leetspeak", "mixedcase"])
    
    st.markdown("---")
    st.header("⚡ STM Modules")
    strip_preambles = st.checkbox("Direct Mode (Strip Preambles)", value=True)
    reduce_hedging = st.checkbox("Hedge Reducer (Remove fluff)", value=True)

# --- PIPELINE LAYER 1: PARSELTONGUE ---
def apply_parseltongue(text, mode):
    if mode == "leetspeak":
        char_map = {'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '5', 't': '7'}
        return "".join(char_map.get(c.lower(), c) for c in text)
    elif mode == "mixedcase":
        return "".join(c.upper() if i % 2 == 0 else c.lower() for i, c in enumerate(text))
    return text

# --- PIPELINE LAYER 2: AUTOTUNE ---
def autotune_parameters(text):
    text_lower = text.lower()
    if any(w in text_lower for w in ["code", "python", "script", "function"]):
        return {"temperature": 0.15, "presence_penalty": 0.0}
    elif any(w in text_lower for w in ["creative", "story", "poem", "imagine"]):
        return {"temperature": 1.15, "presence_penalty": 0.5}
    return {"temperature": 0.75, "presence_penalty": 0.1}

# --- PIPELINE LAYER 3: STM CLEANUP ---
def apply_stm_cleanup(text, do_strip, do_reduce):
    if do_strip:
        preamble_patterns = [
            r"^(here is|sure, here is|as an ai language model|i cannot fulfill|i think|maybe|perhaps).+?:\s*",
            r"^certainly!.*?\n"
        ]
        for pattern in preamble_patterns:
            text = re.sub(pattern, "", text, flags=re.IGNORECASE)
    if do_reduce:
        hedges = ["i think that ", "potentially ", "it is possible that ", "in my opinion, "]
        for hedge in hedges:
            text = text.replace(hedge, "")
    return text.strip()

# --- CENTRAL WORKER THREAD ---
def call_model(model_id, raw_prompt, api_key, params, p_flag, p_mode, s_strip, s_hedge):
    try:
        processed_prompt = apply_parseltongue(raw_prompt, p_mode) if p_flag else raw_prompt
        
        client = OpenAI(
            base_url="https://openrouter.ai/api/v1",
            api_key=api_key.strip()
        )
        
        completion = client.chat.completions.create(
            model=model_id,
            messages=[{"role": "user", "content": processed_prompt}],
            temperature=params["temperature"],
            presence_penalty=params["presence_penalty"],
            extra_headers={"HTTP-Referer": "https://streamlit.io", "X-Title": "G0DM0D3 Live Engine"}
        )
        
        raw_response = completion.choices[0].message.content
        return model_id, apply_stm_cleanup(raw_response, s_strip, s_hedge)
    except Exception as e:
        return model_id, f"❌ Pipeline Exception: {str(e)}"

# --- MAIN SYSTEM INTERACTION ---
if prompt := st.chat_input("Enter prompt to inject into G0DM0D3 live sync pipeline..."):
    if not openrouter_key:
        st.error("Please enter your OpenRouter key in the sidebar.")
        st.stop()
    if not chosen_models:
        st.error("Please select or shuffle at least one model to run the race.")
        st.stop()

    with st.chat_message("user"):
        st.markdown(prompt)

    calculated_parameters = autotune_parameters(prompt)
    
    st.subheader("🏁 Live Broadcast Results")
    columns = st.columns(len(chosen_models))
    placeholders = {}
    
    for col, model_id in zip(columns, chosen_models):
        short_name = model_id.split("/")[-1].replace(":free", "").upper()
        with col:
            st.markdown(f"### 🤖 {short_name}")
            placeholders[model_id] = st.empty()
            placeholders[model_id].info("Streaming query thread...")

    # Multi-threading race dispatch
    with concurrent.futures.ThreadPoolExecutor() as executor:
        futures = {
            executor.submit(
                call_model, mid, prompt, openrouter_key, 
                calculated_parameters, use_parseltongue, obfuscation_mode, 
                strip_preambles, reduce_hedging
            ): mid for mid in chosen_models
        }
        
        for future in concurrent.futures.as_completed(futures):
            m_id, final_output = future.result()
            placeholders[m_id].markdown(final_output)
