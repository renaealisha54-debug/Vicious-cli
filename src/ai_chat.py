import os
import sys

def call_groq(prompt, system_instruction):
    from groq import Groq
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    
    # Active Groq model IDs
    models_to_try = ["llama3-8b-8192", "llama3-70b-8192", "mixtral-8x7b-32768"]
    
    for model in models_to_try:
        try:
            response = client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_instruction},
                    {"role": "user", "content": prompt}
                ]
            )
            return response.choices[0].message.content
        except Exception:
            continue

    raise RuntimeError("Could not connect to active Groq models.")

def call_gemini(prompt, system_instruction):
    import google.generativeai as genai
    genai.configure(api_key=os.environ.get("GEMINI_API_KEY"))
    model = genai.GenerativeModel(
        model_name="gemini-1.5-flash",
        system_instruction=system_instruction
    )
    response = model.generate_content(prompt)
    return response.text

PROVIDERS = [
    ("Groq", "GROQ_API_KEY", call_groq),
    ("Gemini", "GEMINI_API_KEY", call_gemini),
]

def generate_ai_response(prompt: str, system_instruction: str = "") -> str:
    """Iterates through configured providers until one succeeds."""
    for name, env_var, provider_func in PROVIDERS:
        if not os.environ.get(env_var):
            continue
            
        try:
            return provider_func(prompt, system_instruction)
        except Exception as e:
            print(f"[Warning] {name} failed: {e}. Trying fallback...", file=sys.stderr)
            
    raise RuntimeError("All configured AI providers failed or missing API keys.")
