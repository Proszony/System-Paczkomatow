from flask import Blueprint, render_template, session, redirect, url_for, request, flash
import psycopg2
from psycopg2.extras import RealDictCursor
from app.helpers import get_conn
from app.decorators import role_required, login_required

kierownik_bp = Blueprint('kierownik', __name__, url_prefix='/kierownik')


@kierownik_bp.route("/")
@kierownik_bp.route("/dashboard")
@role_required('Kierownik')
def dashboard():
    """Dashboard kierownika – statystyki jego centrum"""
    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    # Pobierz centrum kierownika
    cur.execute("""
        SELECT c.id, c.nazwa, c.adres
        FROM kierownik_centrum kc
        JOIN centrum_logistyczne c ON kc.centrum_id = c.id
        WHERE kc.pracownik_id = %s
    """, (session['user_id'],))
    
    centrum = cur.fetchone()
    
    if not centrum:
        cur.close()
        conn.close()
        return "Centrum nie znalezione", 404

    centrum_id = centrum['id']
    
    # 1) Paczkomaty w centrum
    cur.execute("""
        SELECT COUNT(*) AS cnt
        FROM paczkomat
        WHERE centrum_id = %s
    """, (centrum_id,))
    paczkomaty = cur.fetchone()['cnt']
    
    # 2) Przesyłki NADANE z paczkomatów tego centrum – tylko aktywne
    cur.execute("""
        SELECT COUNT(*) AS cnt
        FROM przesylka p
        JOIN paczkomat pm ON p.paczkomat_nadania_id = pm.id
        JOIN status_przesylki sp ON p.status_id = sp.id
        WHERE pm.centrum_id = %s
          AND sp.status IN ('Nadana', 'Przyjeta w centrum')
    """, (centrum_id,))
    nadane_z_centrum = cur.fetchone()['cnt']
    
    # 3) Przesyłki, których PACZKOMAT DOCELOWY jest w tym centrum – tylko aktywne
    cur.execute("""
        SELECT COUNT(*) AS cnt
        FROM przesylka p
        JOIN paczkomat pm ON p.paczkomat_docelowy_id = pm.id
        JOIN status_przesylki sp ON p.status_id = sp.id
        WHERE pm.centrum_id = %s
          AND sp.status IN ('W transporcie', 'Przyjeta w centrum')
    """, (centrum_id,))
    do_centrum = cur.fetchone()['cnt']
    
    # 4) Przesyłki "W transporcie" powiązane z tym centrum (opcjonalnie możesz zawęzić)
    cur.execute("""
        SELECT COUNT(*) AS cnt
        FROM przesylka p
        JOIN status_przesylki sp ON p.status_id = sp.id
        JOIN paczkomat pm_n ON p.paczkomat_nadania_id = pm_n.id
        JOIN paczkomat pm_d ON p.paczkomat_docelowy_id = pm_d.id
        WHERE sp.status = 'W transporcie'
          AND (pm_n.centrum_id = %s OR pm_d.centrum_id = %s)
    """, (centrum_id, centrum_id))
    w_transporcie = cur.fetchone()['cnt']
    
    cur.close()
    conn.close()
    
    return render_template(
        'kierownik_dashboard.html',
        centrum=centrum,
        paczkomaty=paczkomaty,
        nadane_z_centrum=nadane_z_centrum,
        do_centrum=do_centrum,
        w_transporcie=w_transporcie
    )


@kierownik_bp.route("/paczkomaty")
@role_required('Kierownik')
def paczkomaty():
    """Lista paczkomatów w centrum kierownika wraz z zapełnieniem skrytek S/M/L."""
    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500

    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Pobierz ID centrum kierownika
    cur.execute("""
        SELECT c.id
        FROM kierownik_centrum kc
        JOIN centrum_logistyczne c ON kc.centrum_id = c.id
        WHERE kc.pracownik_id = %s
    """, (session['user_id'],))

    centrum = cur.fetchone()
    if not centrum:
        cur.close()
        conn.close()
        return "Centrum nie znalezione", 404

    # Paczkomaty w centrum z zapełnieniem skrytek
    cur.execute("""
        SELECT
            p.id,
            p.kod,
            p.adres,
            c.nazwa AS centrum,
            -- liczba skrytek S/M/L
            COALESCE(SUM(CASE WHEN s.rozmiar_id = 1 THEN 1 ELSE 0 END), 0) AS liczba_s,
            COALESCE(SUM(CASE WHEN s.rozmiar_id = 2 THEN 1 ELSE 0 END), 0) AS liczba_m,
            COALESCE(SUM(CASE WHEN s.rozmiar_id = 3 THEN 1 ELSE 0 END), 0) AS liczba_l,
            -- zajęte skrytki (Zarezerwowana / Zajeta)
            COALESCE(SUM(CASE WHEN s.rozmiar_id = 1 AND ss.status IN ('Zarezerwowana','Zajeta') THEN 1 ELSE 0 END), 0) AS zajete_s,
            COALESCE(SUM(CASE WHEN s.rozmiar_id = 2 AND ss.status IN ('Zarezerwowana','Zajeta') THEN 1 ELSE 0 END), 0) AS zajete_m,
            COALESCE(SUM(CASE WHEN s.rozmiar_id = 3 AND ss.status IN ('Zarezerwowana','Zajeta') THEN 1 ELSE 0 END), 0) AS zajete_l
        FROM paczkomat p
        JOIN centrum_logistyczne c ON p.centrum_id = c.id
        LEFT JOIN skrytka s ON s.paczkomat_id = p.id
        LEFT JOIN status_skrytki ss ON s.status_id = ss.id
        WHERE p.centrum_id = %s
        GROUP BY p.id, p.kod, p.adres, c.nazwa
        ORDER BY p.kod
    """, (centrum['id'],))

    lista_paczkomatów = cur.fetchall()
    cur.close()
    conn.close()

    return render_template("kierownik_paczkomaty.html", paczkomaty=lista_paczkomatów)

@kierownik_bp.route("/przesylki/nadane")
@login_required
def przesylki_nadane_z_centrum():
    if session.get("user_type") != "Pracownik" or session.get("user_role") != "Kierownik":
        return "Brak dostępu", 403

    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # centrum kierownika
        cur.execute("""
            SELECT centrum_id
            FROM kierownik_centrum
            WHERE pracownik_id = %s
        """, (session["user_id"],))
        row = cur.fetchone()
        if not row:
            return "Brak przypisanego centrum dla tego kierownika", 403
        centrum_id = row["centrum_id"]

        # przesyłki nadane z paczkomatów tego centrum (status Nadana lub Przyjeta w centrum)
        cur.execute("""
            SELECT 
                p.id,
                p.numer_przesylki,
                sp.status,
                p.data_nadania,
                (k1.imie || ' ' || k1.nazwisko) AS nadawca,
                COALESCE(k2.imie || ' ' || k2.nazwisko, 'Nieznany') AS odbiorca,
                pm_nadania.kod AS paczkomat_nadania,
                pm_docelowy.kod AS paczkomat_docelowy
            FROM przesylka p
            JOIN status_przesylki sp ON p.status_id = sp.id
            JOIN klient k1 ON p.nadawca_id = k1.id
            LEFT JOIN klient k2 ON p.odbiorca_id = k2.id
            JOIN paczkomat pm_nadania ON p.paczkomat_nadania_id = pm_nadania.id
            JOIN paczkomat pm_docelowy ON p.paczkomat_docelowy_id = pm_docelowy.id
            WHERE pm_nadania.centrum_id = %s
              AND sp.status IN ('Nadana', 'Przyjeta w centrum')
            ORDER BY p.data_nadania DESC
        """, (centrum_id,))
        przesylki = cur.fetchall()

        return render_template("kierownik_przesylki_nadane.html", przesylki=przesylki)
    finally:
        cur.close()
        conn.close()

@kierownik_bp.route("/przesylki/docelowe")
@login_required
def przesylki_do_centrum():
    if session.get("user_type") != "Pracownik" or session.get("user_role") != "Kierownik":
        return "Brak dostępu", 403

    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute("""
            SELECT centrum_id
            FROM kierownik_centrum
            WHERE pracownik_id = %s
        """, (session["user_id"],))
        row = cur.fetchone()
        if not row:
            return "Brak przypisanego centrum dla tego kierownika", 403
        centrum_id = row["centrum_id"]

        # przesyłki, których paczkomat docelowy jest w tym centrum
        # i są 'W transporcie' lub 'Przyjeta w centrum'
        cur.execute("""
            SELECT 
                p.id,
                p.numer_przesylki,
                sp.status,
                p.data_nadania,
                (k1.imie || ' ' || k1.nazwisko) AS nadawca,
                COALESCE(k2.imie || ' ' || k2.nazwisko, 'Nieznany') AS odbiorca,
                pm_nadania.kod AS paczkomat_nadania,
                pm_docelowy.kod AS paczkomat_docelowy
            FROM przesylka p
            JOIN status_przesylki sp ON p.status_id = sp.id
            JOIN klient k1 ON p.nadawca_id = k1.id
            LEFT JOIN klient k2 ON p.odbiorca_id = k2.id
            JOIN paczkomat pm_nadania ON p.paczkomat_nadania_id = pm_nadania.id
            JOIN paczkomat pm_docelowy ON p.paczkomat_docelowy_id = pm_docelowy.id
            WHERE pm_docelowy.centrum_id = %s
              AND sp.status IN ('W transporcie', 'Przyjeta w centrum')
            ORDER BY p.data_nadania DESC
        """, (centrum_id,))
        przesylki = cur.fetchall()

        return render_template("kierownik_przesylki_docelowe.html", przesylki=przesylki)
    finally:
        cur.close()
        conn.close()
        
@kierownik_bp.route("/przesylka/<int:przesylka_id>/przyjmij-w-centrum", methods=["POST"])
@login_required
def przyjmij_w_centrum(przesylka_id):
    # tylko kierownik
    if session.get("user_type") != "Pracownik" or session.get("user_role") != "Kierownik":
        return "Brak dostępu", 403

    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # centrum kierownika
        cur.execute("""
            SELECT centrum_id
            FROM kierownik_centrum
            WHERE pracownik_id = %s
        """, (session["user_id"],))
        row = cur.fetchone()
        if not row:
            return "Brak przypisanego centrum dla tego kierownika", 403
        centrum_id = row["centrum_id"]

        # pobierz przesyłkę + centrum nadania + status
        cur.execute("""
            SELECT 
                p.id,
                p.status_id,
                pm.centrum_id AS centrum_nadania,
                sp.status AS status_tekst
            FROM przesylka p
            JOIN paczkomat pm ON p.paczkomat_nadania_id = pm.id
            JOIN status_przesylki sp ON p.status_id = sp.id
            WHERE p.id = %s
        """, (przesylka_id,))
        przes = cur.fetchone()
        if not przes:
            return "Przesyłka nie istnieje", 404

        # czy ta paczka należy do centrum kierownika
        if przes["centrum_nadania"] != centrum_id:
            return "Przesyłka nie należy do Twojego centrum", 403

        # czy ma właściwy status
        if przes["status_tekst"] != "Nadana":
            return "Tę przesyłkę nie można przyjąć w centrum (nie jest w statusie 'Nadana')", 400

        # id statusu "Przyjeta w centrum"
        cur.execute("""
            SELECT id
            FROM status_przesylki
            WHERE status = 'Przyjeta w centrum'
        """)
        row = cur.fetchone()
        if not row:
            return "Brak statusu 'Przyjeta w centrum' w bazie", 500
        status_przyjeta_id = row["id"]

        # aktualizacja przesyłki – zmiana statusu
        cur.execute("""
            UPDATE przesylka
            SET status_id = %s
            WHERE id = %s
        """, (status_przyjeta_id, przesylka_id))

        # wpis do historii statusu
        cur.execute("""
            INSERT INTO historia_statusu (przesylka_id, status_z_id, status_na_id, zmienil, data_zmiany, uwagi)
            VALUES (%s, %s, %s, %s, NOW(), %s)
        """, (
            przesylka_id,
            przes["status_id"],
            status_przyjeta_id,
            session["user_id"],
            "Przyjęcie przesyłki w centrum"
        ))

        conn.commit()

        # PO ZMIANIE STATUSU – od razu pobierz i wyrenderuj aktualną listę
        cur.execute("""
            SELECT 
                p.id,
                p.numer_przesylki,
                sp.status,
                p.data_nadania,
                (k1.imie || ' ' || k1.nazwisko) AS nadawca,
                COALESCE(k2.imie || ' ' || k2.nazwisko, 'Nieznany') AS odbiorca,
                pm_nadania.kod AS paczkomat_nadania,
                pm_docelowy.kod AS paczkomat_docelowy
            FROM przesylka p
            JOIN status_przesylki sp ON p.status_id = sp.id
            JOIN klient k1 ON p.nadawca_id = k1.id
            LEFT JOIN klient k2 ON p.odbiorca_id = k2.id
            JOIN paczkomat pm_nadania ON p.paczkomat_nadania_id = pm_nadania.id
            JOIN paczkomat pm_docelowy ON p.paczkomat_docelowy_id = pm_docelowy.id
            WHERE pm_nadania.centrum_id = %s
              AND sp.status IN ('Nadana', 'Przyjeta w centrum')
            ORDER BY p.data_nadania DESC
        """, (centrum_id,))
        przesylki = cur.fetchall()

        return render_template("kierownik_przesylki_nadane.html", przesylki=przesylki)

    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

@kierownik_bp.route("/przesylka/<int:przesylka_id>/wyslij-z-centrum", methods=["POST"])
@login_required
def wyslij_z_centrum(przesylka_id):
    """
    Kierownik wysyła przesyłkę z centrum:
    - jeśli paczkomat docelowy jest w tym samym centrum -> od razu doręcza do paczkomatu docelowego (rezerwuje skrytkę, status 'Doreczona')
    - jeśli paczkomat docelowy jest w innym centrum -> ustawia status 'W transporcie'
    """
    # tylko pracownik-kierownik
    if session.get("user_type") != "Pracownik" or session.get("user_role") != "Kierownik":
        return "Brak dostępu", 403

    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # 1. centrum kierownika
        cur.execute("""
            SELECT centrum_id
            FROM kierownik_centrum
            WHERE pracownik_id = %s
        """, (session["user_id"],))
        row = cur.fetchone()
        if not row:
            return "Brak przypisanego centrum dla tego kierownika", 403
        centrum_kierownika_id = row["centrum_id"]

        # 2. przesyłka z paczkomatami i rozmiarem
        cur.execute("""
            SELECT 
                p.id,
                p.status_id,
                sp.status AS status_tekst,
                p.rozmiar_id,
                pn.id AS paczkomat_nadania_id,
                pn.centrum_id AS centrum_nadania_id,
                pd.id AS paczkomat_docelowy_id,
                pd.centrum_id AS centrum_docelowe_id
            FROM przesylka p
            JOIN status_przesylki sp ON p.status_id = sp.id
            JOIN paczkomat pn ON p.paczkomat_nadania_id = pn.id
            JOIN paczkomat pd ON p.paczkomat_docelowy_id = pd.id
            WHERE p.id = %s
        """, (przesylka_id,))
        prs = cur.fetchone()
        if not prs:
            return "Przesyłka nie istnieje", 404

        # 3. czy ta przesyłka jest z centrum kierownika
        if prs["centrum_nadania_id"] != centrum_kierownika_id:
            return "Przesyłka nie należy do Twojego centrum", 403

        # 4. tylko 'Przyjeta w centrum' może być wysłana z centrum
        # UPEWNIJ SIĘ, że dokładnie tak nazywa się status w tabeli status_przesylki
        if prs["status_tekst"] != "Przyjeta w centrum":
            flash("Przesyłkę można wysłać z centrum tylko w statusie 'Przyjeta w centrum'.", "warning")
            return redirect(url_for("kierownik.przesylki_nadane_z_centrum"))

        ten_sam_centr = (prs["centrum_nadania_id"] == prs["centrum_docelowe_id"])

        if ten_sam_centr:
            # ====== DOSTAWA LOKALNA: od razu do paczkomatu docelowego ======

            # 5. znajdź wolną skrytkę w paczkomacie docelowym o rozmiarze przesyłki
            cur.execute("""
                SELECT s.id
                FROM skrytka s
                JOIN status_skrytki ss ON s.status_id = ss.id
                WHERE s.paczkomat_id = %s
                  AND s.rozmiar_id = %s
                  AND ss.status = 'Wolna'
                ORDER BY s.numer_skrytki
                LIMIT 1
                FOR UPDATE
            """, (prs["paczkomat_docelowy_id"], prs["rozmiar_id"]))
            skrytka = cur.fetchone()

            if not skrytka:
                flash("Brak wolnych skrytek odpowiedniego rozmiaru w paczkomacie docelowym.", "danger")
                return redirect(url_for("kierownik.przesylki_do_centrum"))

            skrytka_id = skrytka["id"]

            # 6. zarezerwuj skrytkę docelową
            cur.execute("""
                UPDATE skrytka
                SET status_id = (SELECT id FROM status_skrytki WHERE status = 'Zarezerwowana')
                WHERE id = %s
            """, (skrytka_id,))

            # 7. utwórz rezerwację skrytki docelowej (status 'Aktywna')
            cur.execute("""
                INSERT INTO rezerwacja_skrytki
                    (przesylka_id, skrytka_id, data_rezerwacji, data_wygasniecia, status_id)
                VALUES (
                    %s,
                    %s,
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP + INTERVAL '3 days',
                    (SELECT id FROM status_rezerwacji WHERE status = 'Aktywna')
                )
            """, (przesylka_id, skrytka_id))

            # 8. zmień status przesyłki na 'Doreczona' (gotowa do odbioru z paczkomatu)
            cur.execute("""
                UPDATE przesylka
                SET status_id = (SELECT id FROM status_przesylki WHERE status = 'Doreczona')
                WHERE id = %s
            """, (przesylka_id,))

            # 9. historia statusu
            cur.execute("""
                INSERT INTO historia_statusu (przesylka_id, status_z_id, status_na_id, zmienil, data_zmiany, uwagi)
                VALUES (
                    %s,
                    (SELECT id FROM status_przesylki WHERE status = 'Przyjeta w centrum'),
                    (SELECT id FROM status_przesylki WHERE status = 'Doreczona'),
                    %s,
                    CURRENT_TIMESTAMP,
                    'Doręczenie do paczkomatu docelowego w tym samym centrum'
                )
            """, (przesylka_id, str(session["user_id"])))

        else:
            # ====== INNE MIASTO / CENTRUM: w trasie między centrami ======

            cur.execute("""
                UPDATE przesylka
                SET status_id = (SELECT id FROM status_przesylki WHERE status = 'W transporcie')
                WHERE id = %s
            """, (przesylka_id,))

            cur.execute("""
                INSERT INTO historia_statusu (przesylka_id, status_z_id, status_na_id, zmienil, data_zmiany, uwagi)
                VALUES (
                    %s,
                    (SELECT id FROM status_przesylki WHERE status = 'Przyjeta w centrum'),
                    (SELECT id FROM status_przesylki WHERE status = 'W transporcie'),
                    %s,
                    CURRENT_TIMESTAMP,
                    'Wysłanie przesyłki z centrum nadania do centrum docelowego'
                )
            """, (przesylka_id, str(session["user_id"])))

        conn.commit()
        flash("Przesyłka została wysłana z centrum.", "success")
        return redirect(url_for("kierownik.przesylki_nadane_z_centrum"))

    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()


@kierownik_bp.route("/przesylki/przyjmij-w-centrum-batch", methods=["POST"])
@login_required
def przyjmij_w_centrum_batch():
    """Kierownik przyjmuje w centrum wiele zaznaczonych przesyłek (Nadana -> Przyjeta w centrum)."""
    if session.get("user_type") != "Pracownik" or session.get("user_role") != "Kierownik":
        return "Brak dostępu", 403

    ids = request.form.getlist("przesylki_ids")
    if not ids:
        flash("Nie zaznaczono żadnej przesyłki.", "warning")
        return redirect(url_for("kierownik.przesylki_nadane_z_centrum"))

    # zamiana na liczby całkowite i filtr śmieci
    try:
        przesylki_ids = [int(x) for x in ids]
    except ValueError:
        flash("Nieprawidłowe identyfikatory przesyłek.", "danger")
        return redirect(url_for("kierownik.przesylki_nadane_z_centrum"))

    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # centrum kierownika
        cur.execute("""
            SELECT centrum_id
            FROM kierownik_centrum
            WHERE pracownik_id = %s
        """, (session["user_id"],))
        row = cur.fetchone()
        if not row:
            return "Brak przypisanego centrum dla tego kierownika", 403
        centrum_kierownika_id = row["centrum_id"]

        # tylko przesyłki z tego centrum i statusem 'Nadana'
        cur.execute("""
            SELECT p.id
            FROM przesylka p
            JOIN status_przesylki sp ON p.status_id = sp.id
            JOIN paczkomat pn ON p.paczkomat_nadania_id = pn.id
            WHERE p.id = ANY(%s)
              AND pn.centrum_id = %s
              AND sp.status = 'Nadana'
        """, (przesylki_ids, centrum_kierownika_id))
        do_przyjecia = [row["id"] for row in cur.fetchall()]

        if not do_przyjecia:
            flash("Brak przesyłek w statusie 'Nadana' do przyjęcia.", "warning")
            return redirect(url_for("kierownik.przesylki_nadane_z_centrum"))

        # zmiana statusu
        cur.execute("""
            UPDATE przesylka
            SET status_id = (SELECT id FROM status_przesylki WHERE status = 'Przyjeta w centrum')
            WHERE id = ANY(%s)
        """, (do_przyjecia,))

        # historia statusu
        for pid in do_przyjecia:
            cur.execute("""
                INSERT INTO historia_statusu (przesylka_id, status_z_id, status_na_id, zmienil, data_zmiany, uwagi)
                VALUES (
                    %s,
                    (SELECT id FROM status_przesylki WHERE status = 'Nadana'),
                    (SELECT id FROM status_przesylki WHERE status = 'Przyjeta w centrum'),
                    %s,
                    CURRENT_TIMESTAMP,
                    'Przyjęcie przesyłki w centrum (operacja zbiorcza)'
                )
            """, (pid, str(session["user_id"])))

        conn.commit()
        flash(f"Przyjęto w centrum {len(do_przyjecia)} przesyłek.", "success")
        return redirect(url_for("kierownik.przesylki_nadane_z_centrum"))

    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

@kierownik_bp.route("/przesylki/wyslij-z-centrum-batch", methods=["POST"])
@login_required
def wyslij_z_centrum_batch():
    """Kierownik wysyła z centrum wiele zaznaczonych przesyłek (Przyjeta w centrum -> Doreczona / W transporcie)."""
    if session.get("user_type") != "Pracownik" or session.get("user_role") != "Kierownik":
        return "Brak dostępu", 403

    ids = request.form.getlist("przesylki_ids")
    if not ids:
        flash("Nie zaznaczono żadnej przesyłki.", "warning")
        return redirect(url_for("kierownik.przesylki_nadane_z_centrum"))

    try:
        przesylki_ids = [int(x) for x in ids]
    except ValueError:
        flash("Nieprawidłowe identyfikatory przesyłek.", "danger")
        return redirect(url_for("kierownik.przesylki_nadane_z_centrum"))

    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # centrum kierownika
        cur.execute("""
            SELECT centrum_id
            FROM kierownik_centrum
            WHERE pracownik_id = %s
        """, (session["user_id"],))
        row = cur.fetchone()
        if not row:
            return "Brak przypisanego centrum dla tego kierownika", 403
        centrum_kierownika_id = row["centrum_id"]

        # wybierz przesyłki z tego centrum i statusem 'Przyjeta w centrum'
        cur.execute("""
            SELECT 
                p.id,
                p.rozmiar_id,
                sp.status AS status_tekst,
                pn.centrum_id AS centrum_nadania_id,
                pd.id AS paczkomat_docelowy_id,
                pd.centrum_id AS centrum_docelowe_id
            FROM przesylka p
            JOIN status_przesylki sp ON p.status_id = sp.id
            JOIN paczkomat pn ON p.paczkomat_nadania_id = pn.id
            JOIN paczkomat pd ON p.paczkomat_docelowy_id = pd.id
            WHERE p.id = ANY(%s)
              AND pn.centrum_id = %s
              AND sp.status = 'Przyjeta w centrum'
        """, (przesylki_ids, centrum_kierownika_id))
        przesylki = cur.fetchall()

        if not przesylki:
            flash("Brak przesyłek w statusie 'Przyjeta w centrum' do wysłania.", "warning")
            return redirect(url_for("kierownik.przesylki_nadane_z_centrum"))

        ilosc_doreczonych = 0
        ilosc_w_trasie = 0

        for prs in przesylki:
            ten_sam_centr = (prs["centrum_nadania_id"] == prs["centrum_docelowe_id"])

            if ten_sam_centr:
                # lokalnie: od razu do paczkomatu docelowego
                cur.execute("""
                    SELECT s.id
                    FROM skrytka s
                    JOIN status_skrytki ss ON s.status_id = ss.id
                    WHERE s.paczkomat_id = %s
                      AND s.rozmiar_id = %s
                      AND ss.status = 'Wolna'
                    ORDER BY s.numer_skrytki
                    LIMIT 1
                    FOR UPDATE
                """, (prs["paczkomat_docelowy_id"], prs["rozmiar_id"]))
                skrytka = cur.fetchone()
                if not skrytka:
                    # brak miejsca – pomiń tę przesyłkę
                    continue

                skrytka_id = skrytka["id"]

                cur.execute("""
                    UPDATE skrytka
                    SET status_id = (SELECT id FROM status_skrytki WHERE status = 'Zarezerwowana')
                    WHERE id = %s
                """, (skrytka_id,))

                cur.execute("""
                    INSERT INTO rezerwacja_skrytki
                        (przesylka_id, skrytka_id, data_rezerwacji, data_wygasniecia, status_id)
                    VALUES (
                        %s,
                        %s,
                        CURRENT_TIMESTAMP,
                        CURRENT_TIMESTAMP + INTERVAL '3 days',
                        (SELECT id FROM status_rezerwacji WHERE status = 'Aktywna')
                    )
                """, (prs["id"], skrytka_id))

                cur.execute("""
                    UPDATE przesylka
                    SET status_id = (SELECT id FROM status_przesylki WHERE status = 'Doreczona')
                    WHERE id = %s
                """, (prs["id"],))

                cur.execute("""
                    INSERT INTO historia_statusu (przesylka_id, status_z_id, status_na_id, zmienil, data_zmiany, uwagi)
                    VALUES (
                        %s,
                        (SELECT id FROM status_przesylki WHERE status = 'Przyjeta w centrum'),
                        (SELECT id FROM status_przesylki WHERE status = 'Doreczona'),
                        %s,
                        CURRENT_TIMESTAMP,
                        'Doręczenie do paczkomatu docelowego (batch)'
                    )
                """, (prs["id"], str(session["user_id"])))

                ilosc_doreczonych += 1

            else:
                # inne centrum: w trasie
                cur.execute("""
                    UPDATE przesylka
                    SET status_id = (SELECT id FROM status_przesylki WHERE status = 'W transporcie')
                    WHERE id = %s
                """, (prs["id"],))

                cur.execute("""
                    INSERT INTO historia_statusu (przesylka_id, status_z_id, status_na_id, zmienil, data_zmiany, uwagi)
                    VALUES (
                        %s,
                        (SELECT id FROM status_przesylki WHERE status = 'Przyjeta w centrum'),
                        (SELECT id FROM status_przesylki WHERE status = 'W transporcie'),
                        %s,
                        CURRENT_TIMESTAMP,
                        'Wysłanie przesyłki z centrum nadania do centrum docelowego (batch)'
                    )
                """, (prs["id"], str(session["user_id"])))

                ilosc_w_trasie += 1

        conn.commit()
        msg_parts = []
        if ilosc_doreczonych:
            msg_parts.append(f"doręczono lokalnie {ilosc_doreczonych}")
        if ilosc_w_trasie:
            msg_parts.append(f"wysłano w trasę {ilosc_w_trasie}")
        if not msg_parts:
            flash("Nie wykonano żadnych zmian (brak wolnych skrytek lub nieprawidłowe statusy).", "warning")
        else:
            flash(" , ".join(msg_parts) + " przesyłek.", "success")

        return redirect(url_for("kierownik.przesylki_nadane_z_centrum"))

    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

@kierownik_bp.route("/przesylka/<int:przesylka_id>/przyjmij-z-trasy", methods=["POST"])
@login_required
def przyjmij_z_trasy(przesylka_id):
    """Kierownik centrum DOCZELOWEGO przyjmuje przesyłkę z trasy (W transporcie -> Przyjeta w centrum)."""
    if session.get("user_type") != "Pracownik" or session.get("user_role") != "Kierownik":
        return "Brak dostępu", 403

    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # centrum kierownika (DOCZELOWE)
        cur.execute("""
            SELECT centrum_id
            FROM kierownik_centrum
            WHERE pracownik_id = %s
        """, (session["user_id"],))
        row = cur.fetchone()
        if not row:
            return "Brak przypisanego centrum dla tego kierownika", 403
        centrum_kierownika_id = row["centrum_id"]

        # przesyłka: status + paczkomat docelowy + centrum docelowe
        cur.execute("""
            SELECT 
                p.id,
                p.status_id,
                sp.status AS status_tekst,
                pm_docelowy.centrum_id AS centrum_docelowe_id
            FROM przesylka p
            JOIN status_przesylki sp ON p.status_id = sp.id
            JOIN paczkomat pm_docelowy ON p.paczkomat_docelowy_id = pm_docelowy.id
            WHERE p.id = %s
        """, (przesylka_id,))
        prs = cur.fetchone()
        if not prs:
            return "Przesyłka nie istnieje", 404

        # czy ta przesyłka jest do centrum tego kierownika
        if prs["centrum_docelowe_id"] != centrum_kierownika_id:
            return "Przesyłka nie jest adresowana do Twojego centrum", 403

        # musi być 'W transporcie'
        if prs["status_tekst"] != "W transporcie":
            flash("Przesyłkę można przyjąć z trasy tylko w statusie 'W transporcie'.", "warning")
            return redirect(url_for("kierownik.przesylki_do_centrum"))

        # id statusu 'Przyjeta w centrum'
        cur.execute("""
            SELECT id
            FROM status_przesylki
            WHERE status = 'Przyjeta w centrum'
        """)
        row = cur.fetchone()
        if not row:
            return "Brak statusu 'Przyjeta w centrum' w bazie", 500
        status_przyjeta_id = row["id"]

        # zmiana statusu
        cur.execute("""
            UPDATE przesylka
            SET status_id = %s
            WHERE id = %s
        """, (status_przyjeta_id, przesylka_id))

        # historia
        cur.execute("""
            INSERT INTO historia_statusu (przesylka_id, status_z_id, status_na_id, zmienil, data_zmiany, uwagi)
            VALUES (
                %s,
                (SELECT id FROM status_przesylki WHERE status = 'W transporcie'),
                %s,
                %s,
                CURRENT_TIMESTAMP,
                'Przyjęcie przesyłki z trasy w centrum docelowym'
            )
        """, (przesylka_id, status_przyjeta_id, str(session["user_id"])))

        conn.commit()
        flash("Przesyłka została przyjęta w centrum docelowym.", "success")
        return redirect(url_for("kierownik.przesylki_do_centrum"))

    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

@kierownik_bp.route("/przesylka/<int:przesylka_id>/dorecz-do-paczkomatu", methods=["POST"])
@login_required
def dorecz_do_paczkomatu(przesylka_id):
    """
    Kierownik centrum DOCZELOWEGO doręcza przesyłkę do paczkomatu docelowego:
    - status 'Przyjeta w centrum' -> 'Doreczona'
    - rezerwacja wolnej skrytki w paczkomacie docelowym.
    """
    if session.get("user_type") != "Pracownik" or session.get("user_role") != "Kierownik":
        return "Brak dostępu", 403

    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # centrum kierownika (DOCZELOWE)
        cur.execute("""
            SELECT centrum_id
            FROM kierownik_centrum
            WHERE pracownik_id = %s
        """, (session["user_id"],))
        row = cur.fetchone()
        if not row:
            return "Brak przypisanego centrum dla tego kierownika", 403
        centrum_kierownika_id = row["centrum_id"]

        # przesyłka + paczkomat docelowy + rozmiar
        cur.execute("""
            SELECT 
                p.id,
                p.status_id,
                sp.status AS status_tekst,
                p.rozmiar_id,
                pm_docelowy.id AS paczkomat_docelowy_id,
                pm_docelowy.centrum_id AS centrum_docelowe_id
            FROM przesylka p
            JOIN status_przesylki sp ON p.status_id = sp.id
            JOIN paczkomat pm_docelowy ON p.paczkomat_docelowy_id = pm_docelowy.id
            WHERE p.id = %s
        """, (przesylka_id,))
        prs = cur.fetchone()
        if not prs:
            return "Przesyłka nie istnieje", 404

        # czy ta przesyłka jest do centrum tego kierownika
        if prs["centrum_docelowe_id"] != centrum_kierownika_id:
            return "Przesyłka nie jest adresowana do Twojego centrum", 403

        # tylko 'Przyjeta w centrum'
        if prs["status_tekst"] != "Przyjeta w centrum":
            flash("Przesyłkę można doręczyć do paczkomatu tylko w statusie 'Przyjeta w centrum'.", "warning")
            return redirect(url_for("kierownik.przesylki_do_centrum"))

        # znajdź wolną skrytkę w paczkomacie docelowym o podanym rozmiarze
        cur.execute("""
            SELECT s.id
            FROM skrytka s
            JOIN status_skrytki ss ON s.status_id = ss.id
            WHERE s.paczkomat_id = %s
              AND s.rozmiar_id = %s
              AND ss.status = 'Wolna'
            ORDER BY s.numer_skrytki
            LIMIT 1
            FOR UPDATE
        """, (prs["paczkomat_docelowy_id"], prs["rozmiar_id"]))
        skrytka = cur.fetchone()

        if not skrytka:
            flash("Brak wolnych skrytek odpowiedniego rozmiaru w paczkomacie docelowym.", "danger")
            return redirect(url_for("kierownik.przesylki_do_centrum"))

        skrytka_id = skrytka["id"]

        # zarezerwuj skrytkę (status 'Zarezerwowana')
        cur.execute("""
            UPDATE skrytka
            SET status_id = (SELECT id FROM status_skrytki WHERE status = 'Zarezerwowana')
            WHERE id = %s
        """, (skrytka_id,))

        # utwórz rezerwację skrytki (Aktywna, 3 dni)
        cur.execute("""
            INSERT INTO rezerwacja_skrytki
                (przesylka_id, skrytka_id, data_rezerwacji, data_wygasniecia, status_id)
            VALUES (
                %s,
                %s,
                CURRENT_TIMESTAMP,
                CURRENT_TIMESTAMP + INTERVAL '3 days',
                (SELECT id FROM status_rezerwacji WHERE status = 'Aktywna')
            )
        """, (przesylka_id, skrytka_id))

        # zmień status przesyłki na 'Doreczona'
        cur.execute("""
            UPDATE przesylka
            SET status_id = (SELECT id FROM status_przesylki WHERE status = 'Doreczona')
            WHERE id = %s
        """, (przesylka_id,))

        # historia statusu
        cur.execute("""
            INSERT INTO historia_statusu (przesylka_id, status_z_id, status_na_id, zmienil, data_zmiany, uwagi)
            VALUES (
                %s,
                (SELECT id FROM status_przesylki WHERE status = 'Przyjeta w centrum'),
                (SELECT id FROM status_przesylki WHERE status = 'Doreczona'),
                %s,
                CURRENT_TIMESTAMP,
                'Doręczenie do paczkomatu docelowego w centrum docelowym'
            )
        """, (przesylka_id, str(session["user_id"])))

        conn.commit()
        flash("Przesyłka została doręczona do paczkomatu docelowego.", "success")
        return redirect(url_for("kierownik.przesylki_do_centrum"))

    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

@kierownik_bp.route("/przesylki/przyjmij-z-trasy-batch", methods=["POST"])
@login_required
def przyjmij_z_trasy_batch():
    """Kierownik centrum DOCZELOWEGO przyjmuje wiele przesyłek z trasy (W transporcie -> Przyjeta w centrum)."""
    if session.get("user_type") != "Pracownik" or session.get("user_role") != "Kierownik":
        return "Brak dostępu", 403

    ids = request.form.getlist("przesylki_ids")
    if not ids:
        flash("Nie zaznaczono żadnej przesyłki.", "warning")
        return redirect(url_for("kierownik.przesylki_do_centrum"))

    try:
        przesylki_ids = [int(x) for x in ids]
    except ValueError:
        flash("Nieprawidłowe identyfikatory przesyłek.", "danger")
        return redirect(url_for("kierownik.przesylki_do_centrum"))

    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # centrum kierownika (docelowe)
        cur.execute("""
            SELECT centrum_id
            FROM kierownik_centrum
            WHERE pracownik_id = %s
        """, (session["user_id"],))
        row = cur.fetchone()
        if not row:
            return "Brak przypisanego centrum dla tego kierownika", 403
        centrum_kierownika_id = row["centrum_id"]

        # wybierz przesyłki: docelowy paczkomat w tym centrum i status 'W transporcie'
        cur.execute("""
            SELECT p.id
            FROM przesylka p
            JOIN status_przesylki sp ON p.status_id = sp.id
            JOIN paczkomat pm_docelowy ON p.paczkomat_docelowy_id = pm_docelowy.id
            WHERE p.id = ANY(%s)
              AND pm_docelowy.centrum_id = %s
              AND sp.status = 'W transporcie'
        """, (przesylki_ids, centrum_kierownika_id))
        do_przyjecia = [row["id"] for row in cur.fetchall()]

        if not do_przyjecia:
            flash("Brak przesyłek w statusie 'W transporcie' do przyjęcia.", "warning")
            return redirect(url_for("kierownik.przesylki_do_centrum"))

        # zmiana statusu na 'Przyjeta w centrum'
        cur.execute("""
            UPDATE przesylka
            SET status_id = (SELECT id FROM status_przesylki WHERE status = 'Przyjeta w centrum')
            WHERE id = ANY(%s)
        """, (do_przyjecia,))

        # historia statusu
        for pid in do_przyjecia:
            cur.execute("""
                INSERT INTO historia_statusu (przesylka_id, status_z_id, status_na_id, zmienil, data_zmiany, uwagi)
                VALUES (
                    %s,
                    (SELECT id FROM status_przesylki WHERE status = 'W transporcie'),
                    (SELECT id FROM status_przesylki WHERE status = 'Przyjeta w centrum'),
                    %s,
                    CURRENT_TIMESTAMP,
                    'Przyjęcie przesyłki z trasy w centrum docelowym (batch)'
                )
            """, (pid, str(session["user_id"])))

        conn.commit()
        flash(f"Przyjęto z trasy {len(do_przyjecia)} przesyłek.", "success")
        return redirect(url_for("kierownik.przesylki_do_centrum"))

    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()

@kierownik_bp.route("/przesylki/dorecz-do-paczkomatu-batch", methods=["POST"])
@login_required
def dorecz_do_paczkomatu_batch():
    """Kierownik centrum DOCZELOWEGO doręcza wiele przesyłek do paczkomatów docelowych (Przyjeta w centrum -> Doreczona)."""
    if session.get("user_type") != "Pracownik" or session.get("user_role") != "Kierownik":
        return "Brak dostępu", 403

    ids = request.form.getlist("przesylki_ids")
    if not ids:
        flash("Nie zaznaczono żadnej przesyłki.", "warning")
        return redirect(url_for("kierownik.przesylki_do_centrum"))

    try:
        przesylki_ids = [int(x) for x in ids]
    except ValueError:
        flash("Nieprawidłowe identyfikatory przesyłek.", "danger")
        return redirect(url_for("kierownik.przesylki_do_centrum"))

    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # centrum kierownika (docelowe)
        cur.execute("""
            SELECT centrum_id
            FROM kierownik_centrum
            WHERE pracownik_id = %s
        """, (session["user_id"],))
        row = cur.fetchone()
        if not row:
            return "Brak przypisanego centrum dla tego kierownika", 403
        centrum_kierownika_id = row["centrum_id"]

        # przesyłki: paczkomat docelowy w tym centrum + status 'Przyjeta w centrum'
        cur.execute("""
            SELECT 
                p.id,
                p.rozmiar_id,
                pm_docelowy.id AS paczkomat_docelowy_id
            FROM przesylka p
            JOIN status_przesylki sp ON p.status_id = sp.id
            JOIN paczkomat pm_docelowy ON p.paczkomat_docelowy_id = pm_docelowy.id
            WHERE p.id = ANY(%s)
              AND pm_docelowy.centrum_id = %s
              AND sp.status = 'Przyjeta w centrum'
        """, (przesylki_ids, centrum_kierownika_id))
        przesylki = cur.fetchall()

        if not przesylki:
            flash("Brak przesyłek w statusie 'Przyjeta w centrum' do doręczenia.", "warning")
            return redirect(url_for("kierownik.przesylki_do_centrum"))

        ilosc_doreczonych = 0

        for prs in przesylki:
            # szukamy wolnej skrytki w paczkomacie docelowym
            cur.execute("""
                SELECT s.id
                FROM skrytka s
                JOIN status_skrytki ss ON s.status_id = ss.id
                WHERE s.paczkomat_id = %s
                  AND s.rozmiar_id = %s
                  AND ss.status = 'Wolna'
                ORDER BY s.numer_skrytki
                LIMIT 1
                FOR UPDATE
            """, (prs["paczkomat_docelowy_id"], prs["rozmiar_id"]))
            skrytka = cur.fetchone()
            if not skrytka:
                # brak miejsca – pomijamy daną przesyłkę
                continue

            skrytka_id = skrytka["id"]

            # rezerwujemy skrytkę
            cur.execute("""
                UPDATE skrytka
                SET status_id = (SELECT id FROM status_skrytki WHERE status = 'Zarezerwowana')
                WHERE id = %s
            """, (skrytka_id,))

            # tworzymy rezerwację (Aktywna)
            cur.execute("""
                INSERT INTO rezerwacja_skrytki
                    (przesylka_id, skrytka_id, data_rezerwacji, data_wygasniecia, status_id)
                VALUES (
                    %s,
                    %s,
                    CURRENT_TIMESTAMP,
                    CURRENT_TIMESTAMP + INTERVAL '3 days',
                    (SELECT id FROM status_rezerwacji WHERE status = 'Aktywna')
                )
            """, (prs["id"], skrytka_id))

            # status 'Doreczona'
            cur.execute("""
                UPDATE przesylka
                SET status_id = (SELECT id FROM status_przesylki WHERE status = 'Doreczona')
                WHERE id = %s
            """, (prs["id"],))

            # historia statusu
            cur.execute("""
                INSERT INTO historia_statusu (przesylka_id, status_z_id, status_na_id, zmienil, data_zmiany, uwagi)
                VALUES (
                    %s,
                    (SELECT id FROM status_przesylki WHERE status = 'Przyjeta w centrum'),
                    (SELECT id FROM status_przesylki WHERE status = 'Doreczona'),
                    %s,
                    CURRENT_TIMESTAMP,
                    'Doręczenie do paczkomatu docelowego (batch, centrum docelowe)'
                )
            """, (prs["id"], str(session["user_id"])))

            ilosc_doreczonych += 1

        conn.commit()
        if not ilosc_doreczonych:
            flash("Nie doręczono żadnej przesyłki (brak wolnych skrytek lub niewłaściwe statusy).", "warning")
        else:
            flash(f"Doręczono {ilosc_doreczonych} przesyłek do paczkomatów docelowych.", "success")

        return redirect(url_for("kierownik.przesylki_do_centrum"))

    except Exception:
        conn.rollback()
        raise
    finally:
        cur.close()
        conn.close()
