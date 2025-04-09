import re
import ollama

def summarize_text(text, model_name="deepseek-r1:8b"):
    """Summarize text using DeepSeek model."""
    # Compute target length (~1/3rd of original)
    target_length = max(len(text.split()) // 3, 50)

    # Construct prompt
    prompt = (
        f"Summarize the following text to approximately 1/3rd of its length while maintaining quality. "
        f"Ensure key concepts and keywords remain intact but simplify explanations where possible. "
        f"The summary should be concise yet informative, structured in a professional manner. "
        f"Do not include greetings, conversational phrases, or additional thoughts. "
        f"Answer in the style of a professionally trained summarization model.\n\n"
        f"Original Text:\n{text}\n\n"
        f"Ensure the summary is about {target_length} words long."
    )

    # Generate summary
    response = ollama.chat(model=model_name, messages=[{"role": "user", "content": prompt}])
    summary = response['message']['content']

    # Remove any "<think>...</think>" sections (if generated)
    summary = re.sub(r"<think>.*?</think>", "", summary, flags=re.DOTALL).strip()

    return summary