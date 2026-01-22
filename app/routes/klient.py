from flask import Blueprint, render_template, session, request
import psycopg2
from psycopg2.extras import RealDictCursor
from app.helpers import get_conn
from app.decorators import login_required

klient_bp = Blueprint('klient', __name__, url_prefix='/klient')


@klient_bp.route("/")
@klient_bp.route("/dashboard")
@login_required
def dashboard():
    """Dashboard klienta – jego przesyłki i statystyki"""
    if session.get('user_type') != 'Klient':
        return "Brak dostępu", 403

    filter_value = request.args.get('filter', 'all')

    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Email
        cur.execute("""
            SELECT email FROM klient
            WHERE id = %s
        """, (session['user_id'],))
        result = cur.fetchone()
        user_email = result['email'] if result else None

        # Statystyki
        cur.execute("""
            SELECT COUNT(*) as cnt FROM przesylka
            WHERE nadawca_id = %s OR odbiorca_id = %s
        """, (session['user_id'], session['user_id']))
        wszystkie_przesylki = cur.fetchone()['cnt']
        
        cur.execute("""
            SELECT COUNT(*) as cnt FROM przesylka
            WHERE (nadawca_id = %s OR odbiorca_id = %s)
              AND status_id = (SELECT id FROM status_przesylki WHERE status='Doreczona')
        """, (session['user_id'], session['user_id']))
        doreczone = cur.fetchone()['cnt']
        
        cur.execute("""
            SELECT COUNT(*) as cnt FROM przesylka
            WHERE (nadawca_id = %s OR odbiorca_id = %s)
              AND status_id NOT IN (
                  SELECT id FROM status_przesylki WHERE status IN ('Doreczona', 'Anulowana')
              )
        """, (session['user_id'], session['user_id']))
        w_trakcie = cur.fetchone()['cnt']

        # Mapowanie filtra na statusy
        if filter_value == 'delivered':
            statusy = ['Doreczona', 'Odebrana']
        elif filter_value == 'in_transit':
            statusy = ['Utworzona', 'Nadana', 'Przyjeta w centrum', 'W transporcie']
        else:
            statusy = None

        base_sql = """
            SELECT 
                p.id,
                p.numer_przesylki,
                k_nadawca.imie || ' ' || k_nadawca.nazwisko AS nadawca,
                k_nadawca.email AS nadawca_email,
                COALESCE(k_odbiorca.imie || ' ' || k_odbiorca.nazwisko, 'Nieznany') AS odbiorca,
                COALESCE(k_odbiorca.email, '-') AS odbiorca_email,
                rp.rozmiar AS rozmiar,
                p.waga_nadania,
                p.koszt,
                s.status AS status,
                p.data_nadania,
                p.data_planowanej_dostawy,
                p.data_dostarczenia
            FROM przesylka p
            JOIN klient k_nadawca ON p.nadawca_id = k_nadawca.id
            LEFT JOIN klient k_odbiorca ON p.odbiorca_id = k_odbiorca.id
            LEFT JOIN rozmiar_przesylki rp ON p.rozmiar_id = rp.id
            JOIN status_przesylki s ON p.status_id = s.id
            WHERE (p.nadawca_id = %s OR p.odbiorca_id = %s)
        """

        params = [session['user_id'], session['user_id']]

        if statusy is not None:
            base_sql += " AND s.status = ANY(%s)"
            params.append(statusy)

        base_sql += " ORDER BY p.data_nadania DESC"
        cur.execute(base_sql, params)
        lista_przesylek = cur.fetchall()
        
        return render_template(
            'klient_dashboard.html',
            wszystkie=wszystkie_przesylki,
            dostarczone=doreczone,
            w_trasie=w_trakcie,
            przesylki=lista_przesylek,
            user_email=user_email,
            current_filter=filter_value
        )
    
    finally:
        cur.close()
        conn.close()


@klient_bp.route("/przesylka/<int:przesylka_id>")
@login_required
def szczegoly_przesylki(przesylka_id):
    """Szczegóły konkretnej przesyłki"""
    if session.get('user_type') != 'Klient':
        return "Brak dostępu", 403
    
    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute("""
            SELECT 
                p.id,
                p.numer_przesylki,
                p.nadawca_id,
                p.odbiorca_id,
                k_nadawca.imie || ' ' || k_nadawca.nazwisko AS nadawca_nazwa,
                k_nadawca.email AS nadawca_email,
                k_nadawca.telefon AS nadawca_telefon,
                k_nadawca.adres AS nadawca_adres,
                COALESCE(k_odbiorca.imie || ' ' || k_odbiorca.nazwisko, 'Nieznany') AS odbiorca_nazwa,
                COALESCE(k_odbiorca.email, '-') AS odbiorca_email,
                COALESCE(k_odbiorca.telefon, '-') AS odbiorca_telefon,
                COALESCE(k_odbiorca.adres, '-') AS odbiorca_adres,
                rp.rozmiar AS rozmiar,
                p.wymiary_dlugosc,
                p.wymiary_szerokosc,
                p.wymiary_wysokosc,
                p.waga_nadania,
                p.koszt,
                s.status AS status,
                p.data_nadania,
                p.data_planowanej_dostawy,
                p.data_dostarczenia,
                p.uwagi,
                p.flaga_uszkodzona,
                pm_nadania.kod || ' - ' || pm_nadania.adres AS paczkomat_nadania,
                pm_docelowy.kod || ' - ' || pm_docelowy.adres AS paczkomat_docelowy
            FROM przesylka p
            JOIN klient k_nadawca ON p.nadawca_id = k_nadawca.id
            LEFT JOIN klient k_odbiorca ON p.odbiorca_id = k_odbiorca.id
            LEFT JOIN rozmiar_przesylki rp ON p.rozmiar_id = rp.id
            JOIN status_przesylki s ON p.status_id = s.id
            LEFT JOIN paczkomat pm_nadania ON p.paczkomat_nadania_id = pm_nadania.id
            LEFT JOIN paczkomat pm_docelowy ON p.paczkomat_docelowy_id = pm_docelowy.id
            WHERE p.id = %s AND (p.nadawca_id = %s OR p.odbiorca_id = %s)
        """, (przesylka_id, session['user_id'], session['user_id']))
        
        przesylka = cur.fetchone()
        
        if not przesylka:
            return "Przesyłka nie znaleziona", 404
        
        return render_template('klient_szczegoly_przesylki.html', przesylka=przesylka)
    
    finally:
        cur.close()
        conn.close()
