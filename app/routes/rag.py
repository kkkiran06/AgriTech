"""
KrishiMitra Agricultural Knowledge & Gemini AI Voice Assistant
Routes:
  GET  /rag/        - Voice Assistant & Knowledge Chat web page
  POST /rag/ask     - JSON endpoint answering farmer agronomy queries
  GET  /rag/search  - Search knowledge base
  GET  /rag/topics  - List all agronomy topics
"""
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
    data = request.get_json(silent=True) or {}
    query = data.get('query') or data.get('question') or request.form.get('query', '')
    crop = data.get('crop') or request.form.get('crop')
    result = rag_engine.answer_query(query, crop_context=crop)
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
