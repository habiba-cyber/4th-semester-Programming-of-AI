from google import genai



GEMINI_API_KEY = "AIzaSyCN50UJiUhjNEherLkfA625Y-L70jdjd2Y" 


client = genai.Client(api_key=GEMINI_API_KEY)

def get_ai_answer(query: str, matched_chunks: list) -> str:
    """
    Takes the user's question and the top matching chunks from FAISS,
    builds a prompt, and asks Gemini to answer using only that context.
    Returns the AI‑generated answer as a string.
    """
    context = "\n\n".join(matched_chunks)

    prompt = (
        f"You are a helpful AI assistant. Answer the following question "
        f"using ONLY the context provided below. Be concise and clear.\n\n"
        f"Context:\n{context}\n\n"
        f"Question: {query}"
    )

    # Generate the answer via the Gemini client
    response = client.models.generate_content(
        model="gemini-3-flash-preview",
        contents=prompt
    )
    return response.text
