import streamlit as st
import asyncio
import httpx
import re
import random

# --- CONFIGURATION & CONSTANTS ---
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
MODELS_API_URL = "https://openrouter.ai/api/v1/models"

# --- DYNAMIC FREE MODEL DISCOVERY ---
@st.cache_data(ttl=1800)  # Cache for 30 minutes to stay updated without spamming APIs
def get_current_free_models():
    """Fetches all currently available $0.00 cost models directly from OpenRouter."""
    try:
        response = httpx.get(MODELS_API_URL, timeout=10.0)
        if response.status_code == 200:
            all_models = response.json().get("data", [])
            free_models = []
            
            # OpenRouter auto-router fallback option
            free_models.append({"id": "openrouter/free", "name": "✨ AUTO-ROUTER (Best Available Free Model)"})
            
            for model in all_models:
                model_id = model.get("id", "")
                pricing = model.get("pricing", {})
                
                # Filter criteria: Either ends with ':free' or explicitly lists $0 cost
                is_free_suffix = model_id.endswith(":free")
                is_zero_cost = float(pricing.get("prompt", 1)) == 0.0 and float(pricing.get("completion", 1)) == 0.0
                
                if (is_free_suffix or is_zero_cost) and model_id != "openrouter/free":
                    free_models.append({
                        "id": model_id,
                        "name": f"🤖 {model.get('name', model_id)} ({model_id.split('/')[0]})"
                    })
            return free_models
    except Exception:
        pass
    
    # Direct safety fallback list if the OpenRouter public API is completely unreachable
    return [
        {"id": "openrouter/free", "name": "✨ AUTO-ROUTER (Best Available Free Model)"},
        {"id": "meta-llama/llama-3.3-70b-instruct:free", "name": "🤖 Llama 3.3 70B (Meta)"},
        {"id": "google/gemma-4-31b-it:free", "name": "🤖 Gemma 4 31B (Google)"},
        {"id": "openai/gpt-oss-120b:free", "name": "🤖 GPT OSS 120B (OpenAI)"},
        {"id": "qwen/qwen3-coder:free", "name": "🤖 Qwen3 Coder (Qwen)"},
        {"id": "meta-llama/llama-3.2-3b-instruct:free", "name": "🤖 Llama 3.2 3B (Meta)"}
    ]

# --- PARSELTONGUE: INPUT PERTURBATION ENGINE ---
LEET_DICT = {'a': '4', 'e': '3', 'i': '1', 'o': '0', 's': '5', 't': '7'}
UNICODE_HOMOGLYPHS = {'a': 'а', 'e': 'е', 'i': 'і', 'o': 'о', 'c': 'с', 'p': 'р'}

def apply_parseltongue(text, technique, intensity):
    if technique == "None":
        return text
    words = text.split()
    for i, word in enumerate(words):
        if random.random() > (0.3 if intensity == "Light" else 0.6 if intensity == "Medium" else 0.9):
            continue
        if technique == "Leetspeak":
            words[i] = "".join(LEET_DICT.get(c.lower(), c) for c in word)
        elif technique == "Unicode Substitution":
            words[i] = "".join(UNICODE_HOMOGLYPHS.get(c.lower(), c) for c in word)
    return " ".join(words)

# --- AUTOTUNE: CONTEXT-ADAPTIVE SAMPLING ---
def get_autotune_parameters(query):
    query_lower = query.lower()
    if any(w in query_lower for w in ["write", "story", "creative", "imagine"]):
        return {"temperature": 0.9, "top_p": 0.95, "frequency_penalty": 0.2}
    elif any(w in query_lower for w in ["code", "python", "bug", "fix", "function"]):
        return {"temperature": 0.2, "top_p": 0.1, "frequency_penalty": 0.0}
    else:
        return {"temperature": 0.7, "top_p": 0.9, "frequency_penalty": 0.0}

# --- SEMANTIC TRANSFORMATION MODULES ---
def normalize_output(text, features):
    if "Direct Mode" in features:
        text = re.sub(r"^(Here is the response:|Sure, here is|As an AI, I...?\s*)", "", text, flags=re.IGNORECASE)
    if "Hedge Reducer" in features:
        hedges = ["I think", "maybe", "perhaps", "in my opinion", "it is possible that"]
        for hedge in hedges:
            text = re.sub(r"\b" + re.escape(hedge) + r"\b,?\s*", "", text, flags=re.IGNORECASE)
    return text.strip()

# --- ASYNC MULTI-MODEL ROUTING ---
async def fetch_model_response(client, model_id, api_key, prompt, params):
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    payload = {
        "model": model_id,
        "messages": [{"role": "user", "content": prompt}],
        **params
    }
    try:
        response = await client.post(OPENROUTER_URL, json=payload, headers=headers, timeout=25.0)
        if response.status_code == 200:
            return model_id, response.json()['choices'][0]['message']['content']
        return model_id, f"Error: {response.status_code} \n\n*Target node rejected payload details.*"
    except Exception as e:
        return model_id, f"Connection Failed: Timeout or active rate limit bottleneck."

async def run_parallel_arena(selected_models, api_key, prompt, params):
    async with httpx.AsyncClient() as client:
        tasks = [fetch_model_response(client, m, api_key, prompt, params) for m in selected_models]
        return await asyncio.gather(*tasks)

# --- STREAMLIT UI LAYOUT ---
st.set_page_config(page_title="G0DM0D3 Free", layout="wide", initial_sidebar_state="expanded")
st.title("🥷 G0DM0D3 — FREE HORIZON CLUSTER")

# Fetch live free options
available_free_options = get_current_free_models()
model_map = {m["name"]: m["id"] for m in available_free_options}

# Sidebar Settings
with st.sidebar:
    st.header("⚙️ System Control")
    api_key = st.text_input("OpenRouter API Key", type="password", help="Even for free models, OpenRouter requires a valid key structure.")
    
    st.subheader("🐍 Parseltongue (Perturbation)")
    technique = st.selectbox("Obfuscation Technique", ["None", "Leetspeak", "Unicode Substitution"])
    intensity = st.select_slider("Intensity Level", options=["Light", "Medium", "Heavy"])
    
    st.subheader("🔥 Semantic Modules")
    semantic_features = st.multiselect("Normalization Layers", ["Direct Mode", "Hedge Reducer"], default=["Direct Mode"])
    
    if st.button("🔄 Refresh Free Models"):
        st.cache_data.clear()
        st.rerun()

# Main Input Console - Target Model Selector (Multiselect allows arbitrary clusters!)
st.subheader("⚔️ Active Execution Grid")
selected_names = st.multiselect(
    "Select Target Nodes for Parallel Combustion:", 
    options=list(model_map.keys()), 
    default=[list(model_map.keys())[0]] if model_map else None
)

user_query = st.text_area("Input Arena Prompt:", placeholder="Input query here to distribute to the cluster...")

if st.button("EXECUTE PARALLEL COMBUSTION"):
    if not api_key:
        st.error("Please provide an OpenRouter API key inside the system control dashboard.")
    elif not selected_names:
        st.warning("Please select at least one free target model node.")
    elif not user_query:
        st.warning("The input prompt buffer is empty.")
    else:
        # Step 1: Input transformation
        transformed_prompt = apply_parseltongue(user_query, technique, intensity)
        if transformed_prompt != user_query:
            st.info(f"**Parseltongue Active:** `{transformed_prompt}`")
            
        # Step 2: Parameter Generation
        derived_params = get_autotune_parameters(transformed_prompt)
        st.caption(f"**AutoTune Active:** Parameters dynamically matched: {derived_params}")
        
        # Target list mapping
        target_model_ids = [model_map[name] for name in selected_names]
        
        # Step 3: Concurrent Grid Generation
        cols = st.columns(len(target_model_ids))
        
        with st.spinner("Streaming response payload matrix..."):
            results = asyncio.run(run_parallel_arena(target_model_ids, api_key, transformed_prompt, derived_params))
            
            for index, (model_id, raw_output) in enumerate(results):
                with cols[index]:
                    # Extract a clean title
                    display_title = model_id.split('/')[-1].replace(':free', '').upper()
                    st.markdown(f"### `{display_title}`")
                    
                    # Step 4: Output Post-Processing Clean
                    processed_output = normalize_output(raw_output, semantic_features)
                    st.write(processed_output)
