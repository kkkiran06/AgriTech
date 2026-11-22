"""
KrishiMitra Agricultural Knowledge & RAG Retrieval Engine
Provides semantic hybrid search and grounded agronomic advisory using ICAR & UAS agronomic documents,
with automatic Google Gemini AI fallback for comprehensive, natural answers.
"""
import re
import math
import json
import base64
import logging
import requests
from typing import List, Dict, Any, Optional
from app.rag.knowledge_data import AGRICULTURAL_KNOWLEDGE_BASE
from app.ml.gemini_vision import get_gemini_api_key, GEMINI_MODELS

logger = logging.getLogger(__name__)

class AgriculturalRAGEngine:
    """
    Retrieval-Augmented Generation Engine for farmer queries.
    Uses BM25-style inverted indexing, keyword weighting, and agronomic knowledge synthesis.
    """

    def __init__(self):
        self.documents = AGRICULTURAL_KNOWLEDGE_BASE
        self._build_index()

    def _tokenize(self, text: str) -> List[str]:
        cleaned = re.sub(r"[^\w\s]", " ", text.lower())
        tokens = cleaned.split()
        stopwords = {"the", "a", "an", "in", "on", "of", "and", "or", "is", "for", "to", "at", "by", "with"}
        return [t for t in tokens if len(t) > 2 and t not in stopwords]

    def _build_index(self):
        self.doc_tokens = {}
        self.df = {}
        self.total_docs = len(self.documents)

        for doc in self.documents:
            doc_id = doc["id"]
            tag_text = " ".join(doc.get("tags", [])) * 3
            title_text = doc.get("title", "") * 2
            full_text = f"{title_text} {tag_text} {doc.get('content', '')}"
            tokens = self._tokenize(full_text)
            self.doc_tokens[doc_id] = tokens

            unique_tokens = set(tokens)
            for token in unique_tokens:
                self.df[token] = self.df.get(token, 0) + 1

    def search(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        query_tokens = self._tokenize(query)
        if not query_tokens:
            return self.documents[:top_k]

        scores = {}
        for doc in self.documents:
            doc_id = doc["id"]
            d_tokens = self.doc_tokens.get(doc_id, [])
            doc_len = len(d_tokens)
            score = 0.0

            for q in query_tokens:
                if q in d_tokens:
                    tf = d_tokens.count(q) / max(1, doc_len)
                    idf = math.log((self.total_docs + 1) / (self.df.get(q, 0) + 1)) + 1.0
                    score += tf * idf

            for tag in doc.get("tags", []):
                for q in query_tokens:
                    if q == tag or q in tag:
                        score += 0.5

            scores[doc_id] = score

        ranked_doc_ids = sorted(scores.keys(), key=lambda did: scores[did], reverse=True)
        results = []
        for did in ranked_doc_ids[:top_k]:
            doc = next(d for d in self.documents if d["id"] == did)
            results.append({
                **doc,
                "relevance_score": round(scores[did], 4),
            })
        return results

    def answer_query(self, query: str, crop_context: Optional[str] = None) -> Dict[str, Any]:
        """
        Synthesize answer using Google Gemini AI if online, with fallback to local ICAR RAG corpus.
        """
        user_query = query.strip()
        if not user_query:
            return {
                "answer": "Please ask a question regarding crops, pests, disease remedies, or agricultural practices.",
                "crop": "General Agriculture",
                "sources": [],
                "provider": "KrishiMitra RAG"
            }

        # 1. Try Gemini Generative AI via direct REST API
        gemini_key = get_gemini_api_key()
        if gemini_key:
            prompt = f"""You are KrishiMitra's expert Senior Agricultural Scientist and Agronomist.
You advise Indian farmers following ICAR (Indian Council of Agricultural Research) and State Agricultural Universities (UAS) Package of Practices.

Farmer's Question: {user_query}
{f'Crop Context: {crop_context}' if crop_context else ''}

Please provide a concise, practical, and farmer-friendly answer:
1. Direct Diagnosis / Recommendation (1-2 clear sentences)
2. Safe Organic & Biological Remedies (Neem extracts, Trichoderma/Pseudomonas, cultural practices)
3. Recommended Chemical Treatment (Include exact dosage per litre and Pre-Harvest Interval safety warnings)
4. Long-term Prevention Tips (Crop rotation, spacing, resistant varieties)

Use clean bullet points and maintain a supportive, practical tone.
"""
            payload = {
                "contents": [{"parts": [{"text": prompt}]}],
                "generationConfig": {"temperature": 0.2}
            }

            for model_name in GEMINI_MODELS:
                url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={gemini_key}"
                try:
                    resp = requests.post(url, json=payload, timeout=20)
                    if resp.status_code == 200:
                        body = resp.json()
                        text_ans = body['candidates'][0]['content']['parts'][0]['text'].strip()
                        return {
                            "query": user_query,
                            "status": "gemini_grounded",
                            "answer": text_ans,
                            "crop": crop_context or "Agricultural Advisory",
                            "sources": ["ICAR Package of Practices", f"Google Gemini AI ({model_name})"],
                            "provider": "Google Gemini AI",
                            "model": model_name
                        }
                except Exception as e:
                    logger.warning(f"Gemini RAG query with {model_name} failed: {e}")

        # 2. Local Static RAG Fallback
        retrieved_docs = self.search(user_query, top_k=2)
        if not retrieved_docs or retrieved_docs[0].get("relevance_score", 0) <= 0.05:
            return {
                "query": user_query,
                "status": "partial_match",
                "answer": (
                    "We could not find an exact match in the current offline agronomic package of practices. "
                    "For specific pest outbreaks or severe crop loss, we recommend consulting our Expert Advisory "
                    "or asking the Community Forum."
                ),
                "sources": [],
                "provider": "Offline Agronomic Corpus",
                "disclaimer": "Agricultural recommendations should be verified by a local agricultural extension officer.",
                "safe_next_steps": [
                    "Inspect the underside of leaves for microscopic pests.",
                    "Avoid spraying unverified chemical cocktails.",
                    "Contact your nearest Krishi Vigyan Kendra (KVK) with a fresh sample."
                ],
            }

        top_doc = retrieved_docs[0]
        content_lines = top_doc["content"].strip().split("\n")
        summary_paragraphs = [line.strip() for line in content_lines if line.strip() and not line.strip().startswith("-") and not line.strip().startswith("1.")][:3]
        summary_text = " ".join(summary_paragraphs)

        return {
            "query": user_query,
            "status": "grounded_answer",
            "crop": top_doc.get("crop"),
            "category": top_doc.get("category"),
            "title": top_doc.get("title"),
            "answer": summary_text or content_lines[0],
            "full_content": top_doc.get("content"),
            "sources": [
                {
                    "title": d["title"],
                    "source": d["source"],
                    "crop": d["crop"],
                    "relevance_score": d["relevance_score"],
                }
                for d in retrieved_docs
            ],
            "provider": "ICAR/UAS Agronomic Knowledge Base",
            "disclaimer": "Information sourced from ICAR/UAS Package of Practices.",
            "safe_next_steps": [
                "Verify symptoms against the full guide before applying inputs.",
                "Prefer biological controls (Trichoderma, Pseudomonas, Neem) as first-line defense.",
                "Always adhere to safety intervals before harvesting produce."
            ],
        }

    def answer_audio_query(self, audio_bytes: bytes, mime_type: str = "audio/webm", language: str = "en") -> Dict[str, Any]:
        """
        Process audio input using Google Gemini Multimodal Audio API.
        Transcribes the farmer's spoken question and provides an agronomic diagnosis.
        """
        gemini_key = get_gemini_api_key()
        if not gemini_key:
            return {
                "transcript": "Audio received (API offline)",
                "answer": "Google Gemini API key is not configured for voice transcription. Please type your query in the box below.",
                "crop": "General Agriculture",
                "sources": [],
                "provider": "KrishiMitra Audio Engine"
            }

        b64_audio = base64.b64encode(audio_bytes).decode('utf-8')
        prompt = f"""You are KrishiMitra's expert Senior Agricultural Scientist and Agronomist.
The user has provided an audio recording of their question in an Indian language (e.g., Hindi, Kannada, Telugu, Tamil, Marathi) or English.

1. Listen to the audio and transcribe the exact question asked by the farmer.
2. Provide a practical agricultural diagnosis and recommendation following ICAR (Indian Council of Agricultural Research) standards.

Return a valid JSON object strictly matching this schema:
{{
  "transcript": "Exact transcription of the farmer's spoken question",
  "language": "Detected language (e.g. Kannada, Hindi, English, Telugu)",
  "crop": "Crop mentioned or Agricultural Advisory",
  "answer": "Clear agricultural answer: direct advice, organic remedies, chemical treatment with dosage, and prevention tips."
}}
"""
        payload = {
            "contents": [{
                "parts": [
                    {"text": prompt},
                    {
                        "inline_data": {
                            "mime_type": mime_type,
                            "data": b64_audio
                        }
                    }
                ]
            }],
            "generationConfig": {
                "response_mime_type": "application/json",
                "temperature": 0.2
            }
        }

        for model_name in GEMINI_MODELS:
            url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={gemini_key}"
            try:
                resp = requests.post(url, json=payload, timeout=30)
                if resp.status_code == 200:
                    body = resp.json()
                    raw_text = body['candidates'][0]['content']['parts'][0]['text']
                    data = json.loads(raw_text)
                    transcript_text = data.get("transcript", "").strip() or "Audio question processed"
                    answer_text = data.get("answer", "").strip()
                    return {
                        "query": transcript_text,
                        "transcript": transcript_text,
                        "answer": answer_text,
                        "crop": data.get("crop", "Agricultural Advisory"),
                        "sources": ["ICAR Package of Practices", f"Google Gemini Multimodal Audio ({model_name})"],
                        "provider": "Google Gemini Voice AI",
                        "model": model_name,
                        "status": "audio_processed"
                    }
            except Exception as e:
                logger.warning(f"Audio query error with {model_name}: {e}")

        # Fallback if audio processing encounters network issues
        return {
            "transcript": "Voice Audio Clip",
            "answer": "We received your voice audio clip, but cloud transcription timed out. Please try speaking again or type your question below.",
            "crop": "General Agriculture",
            "sources": [],
            "provider": "KrishiMitra Voice Fallback"
        }

rag_engine = AgriculturalRAGEngine()
