import os
from datetime import timedelta

class Config:
    """Konfiguracja aplikacji"""
    
    # Database
    DB_HOST = os.getenv('DB_HOST', 'localhost')
    DB_NAME = os.getenv('DB_NAME', 'cbd_db')
    DB_USER = os.getenv('DB_USER', 'postgres')
    DB_PASSWORD = os.getenv('DB_PASSWORD', 'password')
    DB_PORT = int(os.getenv('DB_PORT', 5432))
    
    # Flask
    SECRET_KEY = os.getenv('SECRET_KEY', 'super-secret-key-change-in-production')
    FLASK_DEBUG = os.getenv('FLASK_DEBUG', True)
    
    # Session
    SESSION_PERMANENT = False
    PERMANENT_SESSION_LIFETIME = timedelta(hours=2)
    SESSION_COOKIE_SECURE = False  # zmień na True w produkcji (HTTPS)
    SESSION_COOKIE_HTTPONLY = True
    SESSION_COOKIE_SAMESITE = 'Lax'
