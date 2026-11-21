# Plan 10: Multi-Language & Regional Indian Languages Support

## Objective
Enable accessibility for all Indian farmers by providing seamless multi-language selection supporting at least 5 regional languages of India in addition to English:
1. Hindi (हिन्दी)
2. Marathi (मराठी)
3. Telugu (తెలుగు)
4. Kannada (ಕನ್ನಡ)
5. Tamil (தமிழ்)
6. Punjabi (ਪੰਜਾਬੀ)
7. Bengali (বাংলা)
8. English

## Implementation Details
1. **Translation Engine (`app/translations/languages.py`):**
   - Dictionary of navigation, labels, tags, alerts, and common agricultural terms across all 8 languages.
   - `get_translation(key, lang)` helper.
2. **Context Processor (`app/__init__.py`):**
   - Injects `t(key)`, `current_lang`, and `supported_languages` into all Jinja2 templates.
3. **Language Switcher & Routes:**
   - Route `GET /set-language/<lang_code>` in `app/routes/main.py`.
   - Header dropdown with native scripts and flags in `app/templates/base.html`.
4. **Instant In-Browser Full Page Translation:**
   - Integrated Google Translate Element for dynamic content (crop guides, symptoms, mandis).
   - Seamless CSS styling suppressing intrusive header banners.
5. **Testing (`tests/test_languages.py`):**
   - 4 tests verifying regional language count >= 5, translation dictionary accuracy, route session persistence, and UI dropdown rendering.

## Verification
- Pytest: 27/27 tests passing.
