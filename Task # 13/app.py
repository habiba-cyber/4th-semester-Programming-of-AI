import os
from flask import Flask, render_template, request, redirect, url_for, session, jsonify
from werkzeug.utils import secure_filename
from PIL import Image

from utils.ocr import extract_text_from_image, extract_text_from_pdf
from utils.embeddings import get_embeddings
from utils.vector_db import create_faiss_index, search
from utils.text_splitter import chunk_text
from utils.gemini import get_ai_answer


app = Flask(__name__)
app.secret_key = "hadith-scanner-secret"         
app.config['UPLOAD_FOLDER'] = 'data'
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)


current_chunks = []
current_index  = None



@app.route('/')
def home():
    message = session.pop('message', None)        
    msg_type = session.pop('msg_type', 'success')
    has_index = current_index is not None
    return render_template('index.html',
                           message=message,
                           msg_type=msg_type,
                           has_index=has_index)



@app.route('/upload', methods=['POST'])
def upload():
    global current_chunks, current_index

    # Make sure a file was actually sent
    if 'file' not in request.files or request.files['file'].filename == '':
        session['message'] = "No file selected. Please choose a PDF or image."
        session['msg_type'] = 'error'
        return redirect(url_for('home'))

    file     = request.files['file']
    filename = secure_filename(file.filename)
    filepath = os.path.join(app.config['UPLOAD_FOLDER'], filename)
    file.save(filepath)

    try:
        #  STEP 1: Extract text 
        if filename.lower().endswith(('.png', '.jpg', '.jpeg')):
            image = Image.open(filepath)
            text  = extract_text_from_image(image)
        elif filename.lower().endswith('.pdf'):
            text = extract_text_from_pdf(filepath)
        else:
            session['message'] = "Unsupported file type. Upload a PDF, PNG, JPG, or JPEG."
            session['msg_type'] = 'error'
            return redirect(url_for('home'))

        if not text.strip():
            session['message'] = "Could not extract any text from the file."
            session['msg_type'] = 'error'
            return redirect(url_for('home'))

        #  STEP 2: Chunk the text 
        current_chunks = chunk_text(text)

        #  STEP 3: Generate embeddings
        embeddings = get_embeddings(current_chunks)

        # STEP 4: Build FAISS index 
        current_index = create_faiss_index(embeddings)

        session['message'] = f" '{filename}' processed! {len(current_chunks)} chunks indexed."
        session['msg_type'] = 'success'

    except Exception as e:
        session['message'] = f"Error processing file: {e}"
        session['msg_type'] = 'error'

    return redirect(url_for('home'))



@app.route('/search', methods=['POST'])
def search_query():
    global current_chunks, current_index

    query = request.form.get('query', '').strip()

    if not query:
        return jsonify({'error': 'Please enter a question.'})

    if current_index is None or not current_chunks:
        return jsonify({'error': 'No document indexed yet. Please upload a file first.'})

    try:
        # ── STEP 1: Embed the user's query ────────────
        query_vector = get_embeddings([query])

        # ── STEP 2: Search FAISS for top-3 chunks ─────
        distances, indices = search(current_index, query_vector, count=3)

        matched_chunks = []
        for idx in indices[0]:
            if 0 <= idx < len(current_chunks):
                matched_chunks.append(current_chunks[idx])

        if not matched_chunks:
            return jsonify({'error': 'No relevant content found for your query.'})

        # ── STEP 3: Ask Gemini (logic lives in utils/gemini.py) ──
        ai_answer = get_ai_answer(query, matched_chunks)

        return jsonify({
            'answer': ai_answer,
            'chunks': matched_chunks
        })

    except Exception as e:
        return jsonify({'error': f"Search failed: {e}"})


if __name__ == '__main__':
    app.run(debug=True)
