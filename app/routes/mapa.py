from flask import Blueprint, render_template, jsonify
from psycopg2.extras import RealDictCursor

from app.helpers import get_conn
from app.decorators import login_required

mapa_bp = Blueprint("mapa", __name__, url_prefix="/mapa")


@mapa_bp.route("/")
@login_required
def mapa_view():
    # Widok z HTML i JS (Leaflet)
    return render_template("mapa_punktow.html")


@mapa_bp.route("/api/punkty")
@login_required
def api_punkty():
    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        # Centra logistyczne
        cur.execute("""
            SELECT c.id,
                   m.nazwa AS nazwa,
                   c.szerokosc_geograficzna AS lat,
                   c.dlugosc_geograficzna AS lon,
                   'centrum' AS typ
            FROM centrum_logistyczne c
            JOIN miasto m ON c.miasto_id = m.id
        """)
        centra = cur.fetchall()

        # Paczkomaty
        cur.execute("""
            SELECT p.id,
                   p.kod AS nazwa,
                   p.szerokosc_geograficzna AS lat,
                   p.dlugosc_geograficzna AS lon,
                   p.centrum_id,
                   'paczkomat' AS typ
            FROM paczkomat p
        """)
        paczkomaty = cur.fetchall()

        return jsonify({"centra": centra, "paczkomaty": paczkomaty})
    finally:
        cur.close()
        conn.close()
