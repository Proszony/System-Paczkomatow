from app.routes import auth, index, admin, kierownik, klient, przesylka, mapa


def register_blueprints(app):
    """Rejestruje wszystkie blueprinty w aplikacji Flask"""
    app.register_blueprint(auth.auth_bp)
    app.register_blueprint(index.index_bp)
    app.register_blueprint(admin.admin_bp)
    app.register_blueprint(kierownik.kierownik_bp)
    app.register_blueprint(klient.klient_bp)
    app.register_blueprint(przesylka.przesylka_bp)
    app.register_blueprint(mapa.mapa_bp)
