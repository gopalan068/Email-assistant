import os
import google.genai as genai

def call_llm(prompt: str, system_instruction: str = None, json_mode: bool = False) -> str:
    """
    Abstracted LLM call wrapper. Currently wires to the Gemini API.
    To swap to another provider (e.g. OpenAI), change only the logic inside this function.
    """
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        raise ValueError("GEMINI_API_KEY environment variable is not set. Please set it in your .env file.")
        
    # Configure Gemini SDK
    genai.configure(api_key=api_key)
    
    # Model defaults to gemini-1.5-flash
    model_name = os.environ.get("GEMINI_MODEL", "gemini-1.5-flash")
    
    # Configure optional response type (e.g., JSON mode)
    generation_config = {}
    if json_mode:
        generation_config["response_mime_type"] = "application/json"
        
    # Initialize model
    model = genai.GenerativeModel(
        model_name=model_name,
        generation_config=generation_config,
        system_instruction=system_instruction
    )
    
    # Generate content
    response = model.generate_content(prompt)
    return response.text.strip()
