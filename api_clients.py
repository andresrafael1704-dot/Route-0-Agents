"""
Clientes HTTP ultra-ligeros para las APIs de IA (Gemini, Groq, DeepSeek).
No utiliza librerías pesadas ni gRPC, garantizando compatibilidad 100% con Termux (Android).
"""

import os
import requests
from dotenv import load_dotenv

load_dotenv()

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY", "")
GROQ_API_KEY = os.getenv("GROQ_API_KEY", "")
DEEPSEEK_API_KEY = os.getenv("DEEPSEEK_API_KEY", "")

def call_gemini(prompt: str, system_prompt: str = "") -> str:
    """
    Llama a Gemini 2.0 Flash vía Google AI Studio REST API.
    Nivel gratuito disponible.
    """
    if not GEMINI_API_KEY:
        return "[Error: Falta configurar GEMINI_API_KEY en el archivo .env]"
    
    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.0-flash:generateContent?key={GEMINI_API_KEY}"
    
    payload = {
        "contents": [{"parts": [{"text": prompt}]}]
    }
    if system_prompt:
        payload["system_instruction"] = {
            "parts": [{"text": system_prompt}]
        }

    try:
        res = requests.post(url, json=payload, timeout=25)
        res.raise_for_status()
        data = res.json()
        return data["candidates"][0]["content"]["parts"][0]["text"]
    except Exception as e:
        return f"[Error al consultar Gemini: {str(e)}]"

def call_groq(prompt: str, system_prompt: str = "", model: str = "llama-3.3-70b-versatile") -> str:
    """
    Llama a Groq Cloud (ultra-rápido y gratuito para Llama 3.3 70B).
    """
    if not GROQ_API_KEY:
        # Fallback a Gemini si Groq no está configurado
        if GEMINI_API_KEY:
            return call_gemini(prompt, system_prompt)
        return "[Error: Falta configurar GROQ_API_KEY en el archivo .env]"

    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }
    
    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "temperature": 0.3,
        "max_tokens": 1024
    }

    try:
        res = requests.post(url, json=payload, headers=headers, timeout=15)
        res.raise_for_status()
        data = res.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[Error al consultar Groq: {str(e)}]"

def call_deepseek(prompt: str, system_prompt: str = "", use_reasoning: bool = True) -> str:
    """
    Llama a DeepSeek (V3 o R1 Reasoning).
    Si no hay key de DeepSeek, usa Gemini 2.0 Flash como alternativa gratuita.
    """
    if not DEEPSEEK_API_KEY:
        # Fallback inteligente a Gemini gratuito
        return call_gemini(prompt, system_prompt)

    model = "deepseek-reasoner" if use_reasoning else "deepseek-chat"
    url = "https://api.deepseek.com/chat/completions"
    headers = {
        "Authorization": f"Bearer {DEEPSEEK_API_KEY}",
        "Content-Type": "application/json"
    }

    messages = []
    if system_prompt:
        messages.append({"role": "system", "content": system_prompt})
    messages.append({"role": "user", "content": prompt})

    payload = {
        "model": model,
        "messages": messages,
        "max_tokens": 2048
    }

    try:
        res = requests.post(url, json=payload, headers=headers, timeout=40)
        res.raise_for_status()
        data = res.json()
        return data["choices"][0]["message"]["content"]
    except Exception as e:
        return f"[Error al consultar DeepSeek: {str(e)}]"
