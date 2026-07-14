import os
import requests
import time

def call_llm(prompt: str, system_instruction: str = None, json_mode: bool = False) -> str:
    """
    Abstracted LLM call wrapper. Wires to the Gemini API via Google's OpenAI-compatible
    endpoint so no SDK change is required. Includes exponential backoff retry logic
    (3 retries: 1s, 2s, 4s).
    """
    # Prefer GEMINI_API_KEY; fall back to GROQ_API_KEY for backward compatibility
    # during transition so old deployments don't break immediately.
    api_key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GROQ_API_KEY")
    if not api_key:
        raise ValueError(
            "GEMINI_API_KEY environment variable is not set. "
            "Get a key from https://aistudio.google.com/ and add it to your .env file."
        )

    # Model defaults to Gemini 2.5 Flash (migrated from Groq)
    model_name = os.environ.get("GEMINI_MODEL", "gemini-3.1-flash-lite")

    # Google's OpenAI-compatible endpoint — same request/response shape as OpenAI.
    # No SDK change needed; only URL and auth header differ from the Groq version.
    url = "https://generativelanguage.googleapis.com/v1beta/openai/chat/completions"
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
                raise RuntimeError(
                    f"Gemini API call failed with status code {response.status_code}: {response.text}"
                )

            data = response.json()
            return data["choices"][0]["message"]["content"].strip()
        except Exception as e:
            last_exception = e
            if attempt < retries:
                sleep_time = backoff[attempt]
                print(f"[Gemini LLM Client] Attempt {attempt + 1} failed: {e}. Retrying in {sleep_time}s...")
                time.sleep(sleep_time)
            else:
                raise RuntimeError(f"Failed to call Gemini API after {retries} retries: {last_exception}")
