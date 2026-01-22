from flask import Flask, send_from_directory
from config import Config
import os


def create_app(config_class=Config):
    """
    Factory do tworzenia instancji Flask aplikacji.
    
    Args:
        config_class: Klasa konfiguracji (domyślnie Config)
    
    Returns:
        instancje aplikacji Flask
    """
    
    template_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'templates'))
    static_dir = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'static'))

    app = Flask(
        __name__,
        template_folder=template_dir,
        static_folder=static_dir
        )

    @app.route('/favicon.svg')
    def favicon():
        return send_from_directory(
            os.path.join(app.root_path, 'static'),
            'favicon.svg',
            mimetype='image/vnd.microsoft.icon'
    )

    app.config.from_object(config_class)
    
    
    from app.routes import register_blueprints
    register_blueprints(app)
    
    
    register_error_handlers(app)
    
    return app


def register_error_handlers(app):
    """Rejestruje handlery błędów"""
    
    @app.errorhandler(404)
    def nie_znaleziono(error):
        return "Strona nie istnieje", 404

    @app.errorhandler(500)
    def blad_serwera(error):
        return "Błąd serwera", 500
