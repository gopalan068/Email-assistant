import os
import requests
import time

def call_llm(prompt: str, system_instruction: str = None, json_mode: bool = False) -> str:
    """
    Abstracted LLM call wrapper. Wires to the Groq API using direct HTTP requests via requests.
    Includes exponential backoff retry logic (3 retries: 1s, 2s, 4s).
    """
    api_key = os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError("GROQ_API_KEY environment variable is not set. Please set it in your .env file.")
        
    # Model defaults to Llama 4 Scout
    model_name = os.environ.get("GROQ_MODEL", "meta-llama/llama-4-scout-17b-16e-instruct")
    
    url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {api_key}",
        "Content-Type": "application/json"
    }
    
    messages = []
    if system_instruction:
        messages.append({"role": "system", "content": system_instruction})
    messages.append({"role": "user", "content": prompt})
    
    payload = {
        "model": model_name,
        "messages": messages
    }
    
    if json_mode:
        payload["response_format"] = {"type": "json_object"}
        
    retries = 3
    backoff = [1, 2, 4]
    last_exception = None
    
    for attempt in range(retries + 1):
        try:
            response = requests.post(url, headers=headers, json=payload)
            if response.status_code != 200:
                raise RuntimeError(f"Groq API call failed with status code {response.status_code}: {response.text}")
                
            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            last_exception = e
            if attempt < retries:
                sleep_time = backoff[attempt]
                print(f"[Groq LLM Client] Attempt {attempt + 1} failed: {e}. Retrying in {sleep_time}s...")
                time.sleep(sleep_time)
            else:
                raise RuntimeError(f"Failed to call Groq API after {retries} retries: {last_exception}")

