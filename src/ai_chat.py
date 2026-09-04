import os
import sys

def call_groq(prompt, system_instruction):
    from groq import Groq
    client = Groq(api_key=os.environ.get("GROQ_API_KEY"))
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_instruction},
            {"role": "user", "content": prompt}
        ]
    )
    return response.choices[0].message.content

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
            continue  # Skip if API key is not exported
            
        try:
            return provider_func(prompt, system_instruction)
        except Exception as e:
            print(f"[Warning] {name} failed: {e}. Trying fallback...", file=sys.stderr)
            
    raise RuntimeError("All configured AI providers failed or missing API keys.")
