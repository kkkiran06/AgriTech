import os
from flask import Flask

def create_app(test_config=None):
    """Create and configure the KrishiMitra Flask application."""
    app = Flask(__name__, instance_relative_config=True)
    
    # Default configuration
    app.config.from_mapping(
        SECRET_KEY=os.environ.get('SECRET_KEY', 'krishimitra-dev-secret-key-2026'),
        DATABASE=os.path.join(app.root_path, '..', 'krishimitra.db'),
        DATABASE_URL=os.environ.get('DATABASE_URL', None),
    )

    if test_config is not None:
        app.config.update(test_config)

    # Initialize Database helpers
    from app.database import db
    db.init_app(app)

    # Register blueprints (to be linked in subsequent phases)
    from app.routes.main import main_bp
    from app.routes.auth import auth_bp
    from app.routes.crops import crops_bp
    from app.routes.weather import weather_bp
    from app.routes.soil import soil_bp
    from app.routes.diseases import diseases_bp
    from app.routes.market import market_bp
    from app.routes.schemes import schemes_bp
    from app.routes.plantdoctor import plantdoctor_bp

    app.register_blueprint(main_bp)
    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(crops_bp, url_prefix='/crops')
    app.register_blueprint(weather_bp, url_prefix='/weather')
    app.register_blueprint(soil_bp, url_prefix='/soil')
    app.register_blueprint(diseases_bp, url_prefix='/diseases')
    app.register_blueprint(market_bp, url_prefix='/market')
    app.register_blueprint(schemes_bp, url_prefix='/schemes')
    app.register_blueprint(plantdoctor_bp, url_prefix='/plantdoctor')

    # Configure upload folder
    upload_folder = os.path.join(app.root_path, 'static', 'uploads')
    os.makedirs(upload_folder, exist_ok=True)
    app.config['UPLOAD_FOLDER'] = upload_folder
    app.config['MAX_CONTENT_LENGTH'] = 10 * 1024 * 1024  # 10 MB limit

    # Register multi-language localization context processor
    from flask import session
    from app.translations.languages import get_translation, SUPPORTED_LANGUAGES

    @app.context_processor
    def inject_localization():
        lang = session.get('lang', 'en')
        def translate(key):
            return get_translation(key, lang)
        return dict(
            t=translate,
            current_lang=lang,
            supported_languages=SUPPORTED_LANGUAGES
        )

    return app
