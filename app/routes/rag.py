"""
KrishiMitra Agricultural Knowledge & Gemini AI Voice Assistant
Routes:
  GET  /rag/        - Voice Assistant & Knowledge Chat web page
  POST /rag/ask     - JSON endpoint answering farmer agronomy queries
  GET  /rag/search  - Search knowledge base
  GET  /rag/topics  - List all agronomy topics
"""
import base64
from flask import Blueprint, render_template, request, jsonify, flash
from app.rag.engine import rag_engine
from app.routes.helpers import get_current_farmer

rag_bp = Blueprint('rag', __name__)

@rag_bp.route('/')
def index():
    farmer = get_current_farmer()
    topics = [
        {
            "id": doc["id"],
            "crop": doc["crop"],
            "category": doc["category"],
            "title": doc["title"],
            "source": doc["source"],
            "tags": doc["tags"],
        }
        for doc in rag_engine.documents
    ]
    return render_template('rag/index.html', farmer=farmer, topics=topics)

@rag_bp.route('/ask', methods=['POST'])
def ask():
    # 1. Check if audio file or base64 audio is provided
    audio_file = request.files.get('audio') or request.files.get('audio_file')
    audio_bytes = None
    mime_type = "audio/webm"

    if audio_file and audio_file.filename != '':
        audio_bytes = audio_file.read()
        mime_type = audio_file.content_type or "audio/webm"
    else:
        data = request.get_json(silent=True) or {}
        audio_b64 = data.get('audio_b64') or request.form.get('audio_b64')
        if audio_b64:
            try:
                if ',' in audio_b64:
                    header, encoded = audio_b64.split(',', 1)
                    if 'audio/' in header:
                        mime_type = header.split(';')[0].replace('data:', '')
                    audio_bytes = base64.b64decode(encoded)
                else:
                    audio_bytes = base64.b64decode(audio_b64)
            except Exception:
                pass

    if audio_bytes:
        lang = request.args.get('lang', request.form.get('lang', 'en'))
        result = rag_engine.answer_audio_query(audio_bytes, mime_type=mime_type, language=lang)
        return jsonify(result)

    # 2. Text query processing
    data = request.get_json(silent=True) or {}
    query = data.get('query') or data.get('question') or request.form.get('query', '')
    crop = data.get('crop') or request.form.get('crop')
    result = rag_engine.answer_query(query, crop_context=crop)
    return jsonify(result)

@rag_bp.route('/ask_audio', methods=['POST'])
def ask_audio():
    audio_file = request.files.get('audio') or request.files.get('audio_file')
    audio_bytes = None
    mime_type = "audio/webm"

    if audio_file and audio_file.filename != '':
        audio_bytes = audio_file.read()
        mime_type = audio_file.content_type or "audio/webm"
    else:
        data = request.get_json(silent=True) or {}
        audio_b64 = data.get('audio_b64') or request.form.get('audio_b64')
        if audio_b64:
            try:
                if ',' in audio_b64:
                    header, encoded = audio_b64.split(',', 1)
                    if 'audio/' in header:
                        mime_type = header.split(';')[0].replace('data:', '')
                    audio_bytes = base64.b64decode(encoded)
                else:
                    audio_bytes = base64.b64decode(audio_b64)
            except Exception:
                pass

    if not audio_bytes:
        return jsonify({
            'error': 'No audio file or data received',
            'answer': 'Please record or select an audio file to ask your question.',
            'transcript': ''
        }), 400

    lang = request.args.get('lang', request.form.get('lang', 'en'))
    result = rag_engine.answer_audio_query(audio_bytes, mime_type=mime_type, language=lang)
    return jsonify(result)

@rag_bp.route('/search')
def search():
    q = request.args.get('q', '').strip()
    top_k = int(request.args.get('top_k', 5))
    results = rag_engine.search(q, top_k=top_k)
    return jsonify(results)

@rag_bp.route('/topics')
def topics():
    return jsonify([
        {
            "id": doc["id"],
            "crop": doc["crop"],
            "category": doc["category"],
            "title": doc["title"],
            "source": doc["source"],
            "tags": doc["tags"],
        }
        for doc in rag_engine.documents
    ])
