from flask import Flask, render_template, request
from sentence_transformers import SentenceTransformer
import numpy as np
import faiss

app_service = Flask(__name__)

embedder = SentenceTransformer('paraphrase-MiniLM-L6-v2')

faq_questions = [
    "hospital visiting time",
    "how to get appointment",
    "emergency service details",
    "available doctors list",
    "room categories in hospital"
]

faq_answers = [
    "Hospital visiting time is from 5 PM to 8 PM daily.",
    "You can book appointments online or at reception counter.",
    "Emergency department is available 24/7 for critical cases.",
    "Doctors are available in Cardiology, Neurology, Orthopedics and more.",
    "We provide General, Private and ICU room facilities."
]

vector_space = embedder.encode(faq_questions)

dimension_size = vector_space.shape[1]
search_index = faiss.IndexFlatL2(dimension_size)
search_index.add(np.array(vector_space))

def find_best_match(user_text):
    query_vec = embedder.encode([user_text])
    dist, idx = search_index.search(np.array(query_vec), 1)

    return faq_answers[idx[0][0]]

@app_service.route("/", methods=["GET", "POST"])
def interface():
    bot_reply = "Ask something related to hospital services"

    if request.method == "POST":
        user_query = request.form["question"]
        bot_reply = find_best_match(user_query.lower())

    return render_template("home.html", result=bot_reply)

if __name__ == "__main__":
    app_service.run(debug=True)