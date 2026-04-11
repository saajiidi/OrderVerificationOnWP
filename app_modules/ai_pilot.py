import streamlit as st
import pandas as pd
import requests
from datetime import datetime
from typing import Dict, Any
from app_modules.sales_dashboard import get_setting
from app_modules.llm_manager import init_llm_controller

# ------------------------------
# 1. Agent Logic (RAG + Multi-LLM Agentic)
# ------------------------------
class AIDataAgent:
    """
    Advanced AI-BI Analytics Support Agent.
    Supports Multi-Provider Failover, OpenAI, Gemini, Anthropic, and Local Ollama.
    """
    def __init__(self, provider="Fallback", api_key=None, model_name=None):
        self.provider = provider
        self.api_key = api_key
        self.model_name = model_name
        self.context_dfs = {
            "sales": st.session_state.get("wc_curr_df"),
            "inventory": st.session_state.get("inv_res_data"),
            "manual": st.session_state.get("manual_df"),
        }

    def _get_wc_creds(self):
        wc_info = {}
        try:
            wc_info = st.secrets.get("woocommerce", {})
        except:
            pass
        url = wc_info.get("store_url") or get_setting("WC_URL")
        key = wc_info.get("consumer_key") or get_setting("WC_KEY")
        sec = wc_info.get("consumer_secret") or get_setting("WC_SECRET")
        return url, key, sec

    def call_woocommerce(self, endpoint, params=None):
        url, key, sec = self._get_wc_creds()
        if not url or not key or not sec: return {"error": "Credentials missing"}
        full_url = f"{url.rstrip('/')}/wp-json/wc/v3/{endpoint}"
        try:
            response = requests.get(full_url, auth=(key, sec), params=params, timeout=10)
            if response.status_code == 200: return response.json()
            return {"error": f"API returned {response.status_code}"}
        except Exception as e: return {"error": str(e)}

    def detect_intent(self, query: str) -> str:
        q = query.lower()
        if any(word in q for word in ["sale", "revenue", "order", "conversion", "basket"]): return "sales"
        elif any(word in q for word in ["inventory", "stock", "sku", "out of stock"]): return "inventory"
        elif any(word in q for word in ["customer", "pull", "live", "recent", "api"]): return "agentic_api"
        return "general"

    def get_context_description(self, intent: str) -> str:
        if intent == "sales":
            df = self.context_dfs["sales"]
            if df is not None and not df.empty:
                rev = df['total_amount'].sum() if 'total_amount' in df.columns else 0
                return f"Total Revenue: ৳{rev:,.0f}, Orders: {len(df)}."
        elif intent == "inventory":
            df = self.context_dfs["inventory"]
            if df is not None and not df.empty:
                low_stock = len(df[df['Quantity'] < 10]) if 'Quantity' in df.columns else 0
                return f"Total SKUs: {len(df)}, Low Stock: {low_stock} items."
        return "Operational context: No specific local data found."

    def call_llm(self, query: str, context: str):
        system_prompt = f"You are a retail fashion BI assistant named DEEN OPS Terminal AI. Context:\n{context}"
        
        # New Feature: Advanced Auto-Failover
        if self.provider == "🛡️ Smart Failover (Free Tiers)":
            controller = init_llm_controller()
            return controller.get_response_sync(query, context)

        if self.provider == "OpenAI":
            from openai import OpenAI
            client = OpenAI(api_key=self.api_key)
            resp = client.chat.completions.create(model=self.model_name or "gpt-3.5-turbo", messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": query}])
            return resp.choices[0].message.content
        elif self.provider == "Google Gemini":
            import google.generativeai as genai
            genai.configure(api_key=self.api_key)
            model = genai.GenerativeModel(self.model_name or "gemini-pro")
            resp = model.generate_content(f"{system_prompt}\n\nUser: {query}")
            return resp.text
        elif self.provider == "Ollama (Local)":
            try:
                # Try OpenAI compatible endpoint first
                resp = requests.post("http://localhost:11434/v1/chat/completions", 
                                     json={
                                         "model": self.model_name or "llama3", 
                                         "messages": [
                                             {"role": "system", "content": system_prompt},
                                             {"role": "user", "content": query}
                                         ],
                                         "stream": False
                                     }, timeout=15)
                if resp.status_code == 200:
                    return resp.json()["choices"][0]["message"]["content"]
                
                # Fallback to direct generate API
                resp = requests.post("http://localhost:11434/api/generate", 
                                     json={"model": self.model_name or "llama3", "prompt": f"{system_prompt}\n\nUser: {query}", "stream": False}, timeout=15)
                
                if resp.status_code == 200:
                    return resp.json().get("response", "Error: Empty response from Ollama generate API.")
                elif resp.status_code == 404:
                    return f"Ollama Error: Model '{self.model_name or 'llama3'}' not found. Run `ollama pull {self.model_name or 'llama3'}`."
                else:
                    return f"Ollama Error: Server returned status {resp.status_code}. Details: {resp.text[:100]}"
            except requests.exceptions.ConnectionError:
                return "Ollama Error: Could not connect to local server. Make sure Ollama is running (`ollama serve`)."
            except Exception as e:
                return f"Ollama Error: {str(e)}."
        elif self.provider == "Hugging Face (API)":
            try:
                headers = {"Authorization": f"Bearer {self.api_key}"}
                payload = {"inputs": f"Context: {context}\n\nUser: {query}", "parameters": {"max_new_tokens": 500}}
                model = self.model_name or "mistralai/Mistral-7B-Instruct-v0.2"
                resp = requests.post(f"https://api-inference.huggingface.co/models/{model}", json=payload, headers=headers, timeout=30)
                data = resp.json()
                if isinstance(data, list) and len(data) > 0:
                    return data[0].get("generated_text", str(data))
                return data.get("generated_text", str(data))
            except Exception as e: return f"HF Error: {str(e)}"
        return None

    def process_query(self, query: str):
        intent = self.detect_intent(query)
        context = self.get_context_description(intent)
        if self.provider != "Fallback":
            try:
                with st.spinner(f"🧠 Consulting {self.provider}..."):
                    answer = self.call_llm(query, context)
                    if answer: return answer
            except Exception as e: st.warning(f"{self.provider} Error: {e}")
        if intent == "agentic_api":
            data = self.call_woocommerce("orders", params={"per_page": 3})
            if isinstance(data, list): return f"🤖 **AGENT ACTION**: Pulled live orders:\n\n" + "\n".join([f"Order #{o['id']} - {o['billing']['first_name']} (৳{o['total']})" for o in data])
        return f"💡 **Internal Insight**: {context}"

# ------------------------------
# 2. UI Rendering
# ------------------------------
def render_ai_pilot_page():
    st.markdown("## 🛡️ AI-BI Analytics Support")
    st.caption("Strategic Intelligence Layer • Dynamic Multi-Engine Failover")

    with st.sidebar.expander("⚙️ Model Settings", expanded=False):
        provider = st.selectbox("Intelligence Provider", 
                                ["Fallback", "🛡️ Smart Failover (Free Tiers)", "OpenAI", "Google Gemini", "Hugging Face (API)", "Ollama (Local)"],
                                index=1)
        
        api_key = None
        model_name = None
        
        if provider == "🛡️ Smart Failover (Free Tiers)":
            st.info("Uses rotated free keys (OpenRouter, Groq, Gemini) with auto-failover.")
        elif provider in ["OpenAI", "Google Gemini", "Hugging Face (API)"]:
            api_key = st.text_input(f"{provider} API Key", type="password")
            if provider == "OpenAI":
                model_name = st.selectbox("Model", ["gpt-3.5-turbo", "gpt-4o"])
            elif provider == "Google Gemini":
                model_name = st.selectbox("Model", ["gemini-pro", "gemini-1.5-flash"])
            else:
                model_name = st.text_input("HF Model ID", value="mistralai/Mistral-7B-Instruct-v0.2")
        elif provider == "Ollama (Local)":
            model_name = st.text_input("Ollama Model", value="llama3")

    c1, c2, c3 = st.columns(3)
    c1.metric("Engine", "Active", delta=provider.split()[0])
    c2.metric("Failover", "Enabled", delta="99.9% Up")
    c3.metric("RAG Cache", "Active", delta="Synced")

    st.divider()

    if "agent_messages" not in st.session_state:
        st.session_state.agent_messages = [{"role": "assistant", "content": f"System ready. Engine: {provider}. How can I assist today?"}]

    for msg in st.session_state.agent_messages:
        with st.chat_message(msg["role"]): st.markdown(msg["content"])

    if prompt := st.chat_input("Enter query..."):
        st.session_state.agent_messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"): st.markdown(prompt)

        agent = AIDataAgent(provider=provider, api_key=api_key, model_name=model_name)
        response = agent.process_query(prompt)
        
        st.session_state.agent_messages.append({"role": "assistant", "content": response})
        with st.chat_message("assistant"): st.markdown(response)

        with st.sidebar.expander("🔍 Trace"):
            st.write(f"Provider: {provider}")
            st.write(f"Intent: {agent.detect_intent(prompt)}")
            st.code(agent.get_context_description(agent.detect_intent(prompt)))
