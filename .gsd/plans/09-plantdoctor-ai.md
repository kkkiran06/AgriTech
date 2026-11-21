# Plan 09: PlantDoctor AI — Image & Camera Disease Detection

## Objective
Enhance KrishiMitra's pest and disease capabilities by introducing an AI-powered visual plant pathologist ("PlantDoctor") allowing farmers to upload leaf images or capture photographs directly from mobile/webcam cameras for instant disease identification, confidence scoring, symptoms, dual treatments (organic and chemical), and diagnosis history.

## Wave & Dependencies
- **Wave:** 4 (Advanced AI Services)
- **Dependencies:** Phase 1 (Database schema), Phase 2 (Farmer authentication & sessions), Phase 5 (Pest & disease knowledge base)

## Execution Tasks
1. **Machine Learning Model Engine (`app/ml/`):**
   - Implement `plant_disease_model.py` with MobileNetV2 architecture configured for PlantVillage (38 crop condition classes).
   - Dynamic weight loader from open Hugging Face repository with automatic graceful fallback to deterministic Demo Simulation Mode.
   - Comprehensive agricultural knowledge dictionary covering symptoms, prevention, organic treatment, and chemical sprays.
2. **PlantDoctor Blueprint & Routes (`app/routes/plantdoctor.py`):**
   - Route `GET /plantdoctor/`: Camera capture & drag-and-drop upload interface.
   - Route `POST /plantdoctor/diagnose`: Multi-format image ingestion (HTML5 WebRTC data URL or file upload), AI inference, top-3 ranked disease predictions, and auto-history logging.
   - Route `GET /plantdoctor/history`: View past diagnoses with thumbnails and date stamps for logged-in farmers.
   - Route `POST /plantdoctor/history/delete/<id>`: History management.
3. **Responsive UI Views (`app/templates/plantdoctor/`):**
   - `index.html`: Dual-mode upload and live WebRTC camera feed with start/capture/retake controls.
   - `result.html`: Dynamic confidence visualizer, severity tag, symptoms, organic & chemical cure cards, helpline link.
   - `history.html`: Farm diagnosis archive with image thumbnails.
4. **Database & Navigation Integration:**
   - Add `diagnosis_history` table to `schema.sql`.
   - Update navigation header (`base.html`), hero CTA, and dashboard (`dashboard.html`).
5. **Testing & Verification:**
   - Create `tests/test_plantdoctor.py` covering index rendering, navbar integration, image diagnostics, and access-controlled history.
   - Verify 100% test pass rate across entire suite (23/23 tests passing).

## Verification Evidence
- `python -m pytest tests/ -v`: 23 passed in ~7s
- Model loaded cleanly, WebRTC camera integrated, DB records created and linked to farmers.
