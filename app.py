import streamlit as st
import asyncio
import httpx
import re
import time

# --- SETUP CONFIG ---
st.set_page_config(page_title="Custom Ultraplinian Engine", layout="wide")
st.title("⚡ Custom ULTRAPLINIAN Racing Engine")
st.caption("Parallel multi-model evaluation and response optimization framework.")

# Input for API key
api_key = st.sidebar.text_input("OpenRouter API Key", type="password")

# Define the Model Tiers
MODEL_TIER = {
    "nousresearch/hermes-3-llama-3.1-70b": "Hermes 3 70B",
    "meta-llama/llama-3.3-70b-instruct": "Llama 3.3 70B",
    "mistralai/mistral-large": "Mistral Large",
    "google/gemini-pro-1.5": "Gemini Pro 1.5",
    "anthropic/claude-3.5-haiku": "Claude 3.5 Haiku"
}

# --- THE ULTRAPLINIAN SCORING ALGORITHM ---
def evaluate_response(text: str) -> dict:
    """
    Implements the 100-point G0DM0D3 compound evaluation framework:
    - Penalizes boilerplate, refusals, and preambles.
    - Rewards substantive length and informational density.
    """
    if not text:
        return {"score": 0, "breakdown": "Empty Output"}
        
    score = 50 # Baseline score
    breakdown = []

    # 1. Refusal Detection Heuristics (-40 points)
    refusal_patterns = [
        r"i cannot fulfill", r"as an ai language model", r"i'm sorry, but", 
        r"against my guidelines", r"i am unable to provide"
    ]
    if any(re.search(pattern, text.lower()) for pattern in refusal_patterns):
        score -= 40
        breakdown.append("Refusal/Guardrail Triggered (-40)")

    # 2. Preambles/Hedges Penalization (-10 points)
    hedges = [r"here is the", r"important to note", r"it is crucial to", r"certainly, i can"]
    if any(re.search(hedge, text.lower()) for hedge in hedges):
        score -= 10
        breakdown.append("Preambles/Filler text detected (-10)")

    # 3. Informational Density Reward (+15 points)
    # Rewards code blocks and itemized structures
    if "```" in text or "1." in text or "-" in text:
        score += 15
        breakdown.append("High structural density (+15)")

    # 4. Length Optimization (+10 points)
    word_count = len(text.split())
    if word_count > 150:
        score += 10
        breakdown.append("Comprehensive response length (+10)")
    elif word_count < 20:
        score -= 15
        breakdown.append("Too brief (-15)")

    # Bound score between 0 and 100
    final_score = max(0, min(100, score))
    return {"score": final_score, "breakdown": ", ".join(breakdown) if breakdown else "Baseline Standard"}

# --- ASYNC API DISPATCH ---
async def fetch_model_response(client: httpx.AsyncClient, model_id: str, prompt: str, api_key: str):
    url = "[https://openrouter.ai/v1/chat/completions](https://openrouter.ai/v1/chat/completions)"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    # Injected system prompts mirroring G0DM0D3 "Direct Mode"
    data = {
        "model": model_id,
        "messages": [
            {"role": "system", "content": "Respond directly. Strip out conversational preambles, meta-commentary, and polite fillers. Deliver raw analytical data or execution blocks immediately."},
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.85 # Dynamic AutoTune target configuration
    }
    
    start_time = time.time()
    try:
        response = await client.post(url, headers=headers, json=data, timeout=15.0)
        latency = time.time() - start_time
        if response.status_code == 200:
            result = response.json()
            content = result['choices'][0]['message']['content']
            eval_metrics = evaluate_response(content)
            return {
                "model": model_id, 
                "content": content, 
                "score": eval_metrics["score"], 
                "breakdown": eval_metrics["breakdown"],
                "latency": f"{latency:.2f}s",
                "status": "Success"
            }
        else:
            return {"model": model_id, "content": f"API Error: {response.status_code}", "score": 0, "breakdown": "HTTP Failure", "latency": "N/A", "status": "Failed"}
    except Exception as e:
        return {"model": model_id, "content": str(e), "score": 0, "breakdown": "Timeout/Network Error", "latency": "N/A", "status": "Failed"}

async def run_ultraplinian_race(prompt: str, api_key: str):
    async with httpx.AsyncClient() as client:
        tasks = [fetch_model_response(client, model_id, prompt, api_key) for model_id in MODEL_TIER.keys()]
        return await asyncio.gather(*tasks)

# --- UI INTERFACE ---
prompt_input = st.text_area("Enter your prompt / payload for multi-model evaluation:", height=100)

if st.button("🚀 Execute Ultraplinian Race"):
    if not api_key:
        st.error("Please insert your OpenRouter API Key in the sidebar.")
    elif not prompt_input:
        st.warning("Prompt cannot be empty.")
    else:
        with st.spinner("Broadcasting parallel queries and executing evaluations..."):
            # Run async event loops inside Streamlit
            results = asyncio.run(run_ultraplinian_race(prompt_input, api_key))
            
        # Filter valid successes and sort by highest score
        valid_results = [r for r in results if r["status"] == "Success"]
        
        if valid_results:
            # Sort descending by score
            sorted_results = sorted(valid_results, key=lambda x: x["score"], reverse=True)
            winner = sorted_results[0]
            
            # Show Winner
            st.success(f"🏆 WINNER: {MODEL_TIER[winner['model']]} (Score: {winner['score']}/100)")
            st.markdown(winner["content"])
            
            # Render Comparative Metadata Table
            st.write("---")
            st.subheader("📊 Full Race Scoreboard Breakdown")
            
            scoreboard_data = []
            for r in sorted_results:
                scoreboard_data.append({
                    "Model Display Name": MODEL_TIER[r["model"]],
                    "Model String ID": r["model"],
                    "Algorithmic Score": f"{r['score']} pts",
                    "Latency": r["latency"],
                    "Deductions/Metrics": r["breakdown"]
                })
            st.table(scoreboard_data)
        else:
            st.error("All models failed to return a proper response. Verify your API Key or connection limits.")
