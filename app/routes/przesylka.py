from flask import Blueprint, render_template, request, redirect, url_for, session, flash, jsonify
import psycopg2
import time
from psycopg2.extras import RealDictCursor
from app.helpers import get_conn, oblicz_koszt_przesylki
from app.decorators import login_required

przesylka_bp = Blueprint('przesylka', __name__, url_prefix='/przesylka')


@przesylka_bp.route("/nadaj", methods=["GET", "POST"])
@login_required
def nadaj():
    """Nowa przesyłka (dla klientów)"""
    if session.get('user_type') != 'Klient':
        return "Brak dostępu", 403
    
    # --- sekcja wspólna (GET + ponowne wyrenderowanie przy błędzie) ---
    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500
    
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # pobierz tylko zalogowanego klienta jako nadawcę
    cur.execute("""
        SELECT id, imie, nazwisko, email 
        FROM klient
        WHERE id = %s
          AND status_id = (SELECT id FROM status_uzytkownika WHERE status='Aktywny')
    """, (session['user_id'],))
    nadawca = cur.fetchone()

    if not nadawca:
        cur.close()
        conn.close()
        return "Twoje konto jest nieaktywne lub nie istnieje", 403

    # odbiorcy (inni aktywni klienci)
    cur.execute("""
        SELECT id, imie, nazwisko, email 
        FROM klient
        WHERE status_id = (SELECT id FROM status_uzytkownika WHERE status='Aktywny')
          AND id <> %s
        ORDER BY imie, nazwisko
    """, (session['user_id'],))
    odbiorcy = cur.fetchall()
    
    # paczkomaty sprawne
    cur.execute("""
        SELECT id, kod, adres
        FROM paczkomat
        WHERE status_id = (SELECT id FROM status_paczkomatu WHERE status='Sprawny')
        ORDER BY kod
    """)
    paczkomaty = cur.fetchall()
    
    # rozmiary
    cur.execute("SELECT id, rozmiar FROM rozmiar_przesylki ORDER BY id")
    rozmiary = cur.fetchall()
    
    cur.close()
    conn.close()
    
    # --- POST: utworzenie przesyłki + rezerwacja skrytki ---
    if request.method == "POST":
        try:
            nadawca_id = session['user_id']
            odbiorca_id = int(request.form.get("odbiorca_id"))
            paczkomat_nadania_id = int(request.form.get("paczkomat_nadania_id"))
            paczkomat_docelowy_id = int(request.form.get("paczkomat_docelowy_id"))
            rozmiar_id = int(request.form.get("rozmiar_id"))

            waga_raw = (request.form.get("waga") or "").strip()
            waga = float(waga_raw)
            if waga <= 0:
                raise ValueError("waga_ujemna")
        except ValueError:
            # konkretny komunikat dla błędnej wagi
            return render_template(
                "nadaj_przesylke.html",
                blad="Błędna waga. Podaj dodatnią liczbę w kilogramach, np. 2.5.",
                nadawca=nadawca,
                odbiorcy=odbiorcy,
                paczkomaty=paczkomaty,
                rozmiary=rozmiary
            ), 400
        except TypeError:
            return render_template(
                "nadaj_przesylke.html",
                blad="Nieprawidłowe dane formularza. Sprawdź uzupełnione pola.",
                nadawca=nadawca,
                odbiorcy=odbiorcy,
                paczkomaty=paczkomaty,
                rozmiary=rozmiary
            ), 400

        # oblicz koszt
        koszt_info = oblicz_koszt_przesylki(
            paczkomat_nadania_id, paczkomat_docelowy_id, rozmiar_id, waga
        )
        if not koszt_info:
            return render_template(
                "nadaj_przesylke.html",
                blad="Nie można wyliczyć kosztu przesyłki.",
                nadawca=nadawca,
                odbiorcy=odbiorcy,
                paczkomaty=paczkomaty,
                rozmiary=rozmiary
            ), 500
        
        koszt = koszt_info['koszt']

        # jedna transakcja: rezerwacja skrytki + utworzenie przesyłki + wpis rezerwacji
        conn = get_conn()
        if not conn:
            return "Błąd połączenia z bazą", 500
        cur = conn.cursor(cursor_factory=RealDictCursor)

        try:
            # 1. znajdź wolną skrytkę odpowiedniego rozmiaru w paczkomacie nadania
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
            """, (paczkomat_nadania_id, rozmiar_id))
            skrytka = cur.fetchone()

            if not skrytka:
                conn.rollback()
                cur.close()
                conn.close()
                return render_template(
                    "nadaj_przesylke.html",
                    blad="Brak wolnych skrytek danego rozmiaru w wybranym paczkomacie nadania.",
                    nadawca=nadawca,
                    odbiorcy=odbiorcy,
                    paczkomaty=paczkomaty,
                    rozmiary=rozmiary
                ), 400

            skrytka_id = skrytka["id"]

            # 2. zarezerwuj skrytkę (status_skrytki = 'Zarezerwowana')
            cur.execute("""
                UPDATE skrytka
                SET status_id = (SELECT id FROM status_skrytki WHERE status = 'Zarezerwowana')
                WHERE id = %s
            """, (skrytka_id,))

            # 3. utwórz przesyłkę w statusie 'Utworzona'
            cur.execute("""
                INSERT INTO przesylka 
                (numer_przesylki, nadawca_id, odbiorca_id, 
                 paczkomat_nadania_id, paczkomat_docelowy_id,
                 rozmiar_id, wymiary_dlugosc, wymiary_szerokosc, wymiary_wysokosc,
                 waga_nadania, koszt, status_id, data_nadania)
                VALUES (
                    %s, %s, %s, %s, %s, %s,
                    %s, %s, %s, %s, %s,
                    (SELECT id FROM status_przesylki WHERE status='Utworzona'),
                    CURRENT_TIMESTAMP
                )
                RETURNING id
            """, (
                f"PKG-{int(time.time())}",
                nadawca_id, odbiorca_id,
                paczkomat_nadania_id, paczkomat_docelowy_id,
                rozmiar_id, 20, 15, 10,
                waga, koszt
            ))
            przesylka_id_row = cur.fetchone()
            przesylka_id = przesylka_id_row["id"] if isinstance(przesylka_id_row, dict) else przesylka_id_row

            # 4. wpis do rezerwacja_skrytki (Aktywna)
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

            conn.commit()
            cur.close()
            conn.close()

            flash(f"Przesyłka utworzona! ID: {przesylka_id}, koszt: {koszt} zł.", "success")
            return redirect(url_for("klient.dashboard"))

        except Exception:
            conn.rollback()
            cur.close()
            conn.close()
            # tu ewentualnie logujesz szczegóły wyjątku do pliku / loggera
            return render_template(
                "nadaj_przesylke.html",
                blad="Wystąpił nieoczekiwany błąd podczas tworzenia przesyłki. Spróbuj ponownie za chwilę.",
                nadawca=nadawca,
                odbiorcy=odbiorcy,
                paczkomaty=paczkomaty,
                rozmiary=rozmiary
            ), 500

    # --- GET ---
    return render_template(
        "nadaj_przesylke.html",
        nadawca=nadawca,
        odbiorcy=odbiorcy,
        paczkomaty=paczkomaty,
        rozmiary=rozmiary
    )


@przesylka_bp.route("/<int:przesylka_id>/status")
@login_required
def status(przesylka_id):
    """Sprawdzenie statusu przesyłki + trasa skąd–dokąd"""
    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    cur.execute("""
        SELECT 
            p.id, p.numer_przesylki, p.koszt, p.status_id,
            s.status,
            p.data_nadania, p.data_dostarczenia,
            k1.imie  AS nadawca_imie,
            k1.nazwisko AS nadawca_nazwisko,
            k2.imie  AS odbiorca_imie,
            k2.nazwisko AS odbiorca_nazwisko,
            p.nadawca_id, p.odbiorca_id,

            -- Paczkomat nadania + miasto
            pn.kod  AS paczkomat_nadania_kod,
            mn.nazwa AS miasto_nadania_nazwa,

            -- Paczkomat docelowy + miasto
            pd.kod  AS paczkomat_docelowy_kod,
            md.nazwa AS miasto_docelowe_nazwa

        FROM przesylka p
        JOIN status_przesylki s ON p.status_id = s.id
        JOIN klient k1 ON p.nadawca_id = k1.id
        JOIN klient k2 ON p.odbiorca_id = k2.id

        JOIN paczkomat pn ON p.paczkomat_nadania_id = pn.id
        JOIN centrum_logistyczne cl_n ON pn.centrum_id = cl_n.id
        JOIN miasto mn ON cl_n.miasto_id = mn.id

        JOIN paczkomat pd ON p.paczkomat_docelowy_id = pd.id
        JOIN centrum_logistyczne cl_d ON pd.centrum_id = cl_d.id
        JOIN miasto md ON cl_d.miasto_id = md.id

        WHERE p.id = %s
    """, (przesylka_id,))
    
    przesylka = cur.fetchone()
    
    if not przesylka:
        cur.close()
        conn.close()
        return "Przesyłka nie istnieje", 404
    
    # Dostęp klienta tylko do swoich
    if session.get('user_type') == 'Klient':
        if session['user_id'] != przesylka['nadawca_id'] and session['user_id'] != przesylka['odbiorca_id']:
            cur.close()
            conn.close()
            return "Brak dostępu do tej przesyłki", 403
    
    # Historia
    cur.execute("""
        SELECT
            hs.data_zmiany,
            hs.uwagi,
            sp.status AS status_na
        FROM historia_statusu hs
        JOIN status_przesylki sp
            ON hs.status_na_id = sp.id
        WHERE hs.przesylka_id = %s
        ORDER BY hs.data_zmiany DESC
    """, (przesylka_id,))
    
    historia = cur.fetchall()
    cur.close()
    conn.close()
    
    return render_template("status_przesylki.html",
                           przesylka=przesylka,
                           historia=historia)

@przesylka_bp.route("/lista")
@login_required
def lista():
    """Lista przesyłek (dostosowana do roli)"""
    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500
        
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        user_type = session.get('user_type')
        user_role = session.get('user_role')

        if user_type == 'Klient':
            # Klient widzi tylko swoje przesyłki
            cur.execute("""
                SELECT p.id, p.numer_przesylki, p.koszt, s.status,
                       p.data_nadania, p.data_dostarczenia,
                       (k1.imie || ' ' || k1.nazwisko) AS nadawca,
                       (k2.imie || ' ' || k2.nazwisko) AS odbiorca
                FROM przesylka p
                JOIN status_przesylki s ON p.status_id = s.id
                JOIN klient k1 ON p.nadawca_id = k1.id
                JOIN klient k2 ON p.odbiorca_id = k2.id
                WHERE p.nadawca_id = %s OR p.odbiorca_id = %s
                ORDER BY p.data_nadania DESC
                LIMIT 50
            """, (session['user_id'], session['user_id']))

        elif user_type == 'Pracownik':
            if user_role == 'Kierownik':
                # Kierownik – przesyłki 'Nadana' z paczkomatów jego centrum
                cur.execute("""
                    SELECT centrum_id
                    FROM kierownik_centrum
                    WHERE pracownik_id = %s
                """, (session['user_id'],))
                row = cur.fetchone()
                if not row:
                    return "Brak przypisanego centrum dla tego kierownika", 403
                centrum_id = row["centrum_id"]

                cur.execute("""
                    SELECT 
                        p.id,
                        p.numer_przesylki,
                        p.koszt,
                        s.status,
                        p.data_nadania,
                        p.data_dostarczenia,
                        (k1.imie || ' ' || k1.nazwisko) AS nadawca,
                        (k2.imie || ' ' || k2.nazwisko) AS odbiorca,
                        pm_nadania.kod AS paczkomat_nadania,
                        pm_docelowy.kod AS paczkomat_docelowy
                    FROM przesylka p
                    JOIN status_przesylki s ON p.status_id = s.id
                    JOIN klient k1 ON p.nadawca_id = k1.id
                    JOIN klient k2 ON p.odbiorca_id = k2.id
                    JOIN paczkomat pm_nadania ON p.paczkomat_nadania_id = pm_nadania.id
                    JOIN paczkomat pm_docelowy ON p.paczkomat_docelowy_id = pm_docelowy.id
                    WHERE s.status = 'Nadana'
                      AND pm_nadania.centrum_id = %s
                    ORDER BY p.data_nadania DESC
                    LIMIT 50
                """, (centrum_id,))

            elif user_role == 'Administrator':
                # Admin – widzi wszystkie
                cur.execute("""
                    SELECT p.id, p.numer_przesylki, p.koszt, s.status,
                           p.data_nadania, p.data_dostarczenia,
                           (k1.imie || ' ' || k1.nazwisko) AS nadawca,
                           (k2.imie || ' ' || k2.nazwisko) AS odbiorca
                    FROM przesylka p
                    JOIN status_przesylki s ON p.status_id = s.id
                    JOIN klient k1 ON p.nadawca_id = k1.id
                    JOIN klient k2 ON p.odbiorca_id = k2.id
                    ORDER BY p.data_nadania DESC
                    LIMIT 50
                """)
            else:
                # Inny pracownik – na razie brak widoku
                return "Brak uprawnień do podglądu listy przesyłek", 403

        else:
            # Fallback – brak znanego typu użytkownika
            return "Brak uprawnień do podglądu listy przesyłek", 403

        przesylki = cur.fetchall()
    finally:
        cur.close()
        conn.close()
    
    return render_template("lista_przesylek.html", przesylki=przesylki, user_type=user_type, user_role=user_role)


@przesylka_bp.route("/<int:przesylka_id>/nadaj", methods=["POST"])
@login_required
def oznacz_jako_nadana(przesylka_id):
    """
    Klient zmienia status przesyłki z 'Utworzona' na 'Nadana'.
    Używana z przycisku w szczegółach / liście przesyłek.
    """
    if session.get('user_type') != 'Klient':
        return "Brak dostępu", 403

    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # sprawdź, czy to przesyłka tego klienta i czy jest 'Utworzona'
        cur.execute("""
            SELECT p.id, s.status, p.nadawca_id, p.odbiorca_id
            FROM przesylka p
            JOIN status_przesylki s ON p.status_id = s.id
            WHERE p.id = %s
        """, (przesylka_id,))
        p = cur.fetchone()
        if not p:
            return "Przesyłka nie istnieje", 404

        if session['user_id'] not in (p["nadawca_id"], p["odbiorca_id"]):
            return "Brak dostępu", 403

        if p["status"] != "Utworzona":
            flash("Tę przesyłkę można nadać tylko, gdy jest w statusie 'Utworzona'.", "warning")
            return redirect(url_for("klient.szczegoly_przesylki", przesylka_id=przesylka_id))

        # zmiana statusu na 'Nadana'
        cur.execute("""
            UPDATE przesylka
            SET status_id = (SELECT id FROM status_przesylki WHERE status = 'Nadana'),
                data_nadania = CURRENT_TIMESTAMP
            WHERE id = %s
        """, (przesylka_id,))

        # wpis do historii_statusu
        cur.execute("""
            INSERT INTO historia_statusu (przesylka_id, status_z_id, status_na_id, zmienil, data_zmiany, uwagi)
            VALUES (
            %s,
            (SELECT id FROM status_przesylki WHERE status = 'Utworzona'),
            (SELECT id FROM status_przesylki WHERE status = 'Nadana'),
            %s,
            CURRENT_TIMESTAMP,
            'Nadanie przesyłki przez klienta'
            )
        """, (przesylka_id, str(session['user_id'])))

        conn.commit()
        flash("Przesyłka została nadana.", "success")
        return redirect(url_for("klient.szczegoly_przesylki", przesylka_id=przesylka_id))
    finally:
        cur.close()
        conn.close()

@przesylka_bp.route("/<int:przesylka_id>/anuluj", methods=["POST"])
@login_required
def anuluj(przesylka_id):
    """
    Klient anuluje przesyłkę w stanie 'Utworzona':
    - status przesyłki -> 'Anulowana'
    - zwolnienie zarezerwowanej skrytki
    - aktualizacja rezerwacji skrytki
    - wpis w historia_statusu
    """
    if session.get('user_type') != 'Klient':
        return "Brak dostępu", 403

    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # 1. sprawdź, czy przesyłka istnieje i należy do użytkownika
        cur.execute("""
            SELECT p.id, s.status, p.nadawca_id, p.odbiorca_id
            FROM przesylka p
            JOIN status_przesylki s ON p.status_id = s.id
            WHERE p.id = %s
        """, (przesylka_id,))
        p = cur.fetchone()
        if not p:
            return "Przesyłka nie istnieje", 404

        if session['user_id'] not in (p["nadawca_id"], p["odbiorca_id"]):
            return "Brak dostępu", 403

        if p["status"] != "Utworzona":
            flash("Tę przesyłkę można anulować tylko w statusie 'Utworzona'.", "warning")
            return redirect(url_for("klient.szczegoly_przesylki", przesylka_id=przesylka_id))

        # 2. znajdź aktywną rezerwację skrytki
        cur.execute("""
            SELECT rs.skrytka_id, rs.status_id
            FROM rezerwacja_skrytki rs
            JOIN status_rezerwacji sr ON rs.status_id = sr.id
            WHERE rs.przesylka_id = %s
              AND sr.status = 'Aktywna'
            ORDER BY rs.data_rezerwacji DESC
            LIMIT 1
        """, (przesylka_id,))
        rez = cur.fetchone()

        if rez:
            skrytka_id = rez["skrytka_id"]

            # 3. zwolnij skrytkę (status_skrytki -> 'Wolna')
            cur.execute("""
                UPDATE skrytka
                SET status_id = (SELECT id FROM status_skrytki WHERE status = 'Wolna')
                WHERE id = %s
            """, (skrytka_id,))

            # 4. ustaw rezerwację jako zakończoną
            cur.execute("""
                UPDATE rezerwacja_skrytki
                SET status_id = (SELECT id FROM status_rezerwacji WHERE status = 'Zwolniona'),
                    data_wygasniecia = CURRENT_TIMESTAMP
                WHERE przesylka_id = %s
                  AND skrytka_id = %s
            """, (przesylka_id, skrytka_id))

        # 5. zmień status przesyłki na 'Anulowana'
        cur.execute("""
            UPDATE przesylka
            SET status_id = (SELECT id FROM status_przesylki WHERE status = 'Anulowana')
            WHERE id = %s
        """, (przesylka_id,))

        # 6. wpis do historii statusów
        cur.execute("""
            INSERT INTO historia_statusu (przesylka_id, status_z_id, status_na_id, zmienil, data_zmiany, uwagi)
            VALUES (
                %s,
                (SELECT id FROM status_przesylki WHERE status = 'Utworzona'),
                (SELECT id FROM status_przesylki WHERE status = 'Anulowana'),
                %s,
                CURRENT_TIMESTAMP,
                'Anulowanie przesyłki przez klienta'
            )
        """, (przesylka_id, str(session['user_id'])))

        conn.commit()
        flash("Przesyłka została anulowana, a skrytka zwolniona.", "success")
        return redirect(url_for("klient.dashboard"))
    finally:
        cur.close()
        conn.close()


@przesylka_bp.route("/<int:przesylka_id>/odbierz", methods=["POST"])
@login_required
def odbierz(przesylka_id):
    """
    Odbiór przesyłki przez odbiorcę:
    - tylko gdy status = 'Doręczona' i zalogowany = odbiorca
    - zmiana statusu na 'Odebrana'
    - zwolnienie skrytki i zamknięcie rezerwacji
    """
    if session.get('user_type') != 'Klient':
        return "Brak dostępu", 403

    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # 1. pobierz przesyłkę
        cur.execute("""
            SELECT p.id, p.odbiorca_id, p.status_id, sp.status
            FROM przesylka p
            JOIN status_przesylki sp ON p.status_id = sp.id
            WHERE p.id = %s
        """, (przesylka_id,))
        p = cur.fetchone()
        if not p:
            return "Przesyłka nie istnieje", 404

        if p["odbiorca_id"] != session["user_id"]:
            return "Brak dostępu", 403

        if p["status"] != "Doreczona":
            flash("Tę przesyłkę można odebrać tylko, gdy jest w statusie 'Doreczona'.", "warning")
            return redirect(url_for("klient.szczegoly_przesylki", przesylka_id=przesylka_id))

        # 2. znajdź skrytkę i aktywną rezerwację
        cur.execute("""
            SELECT rs.skrytka_id, rs.status_id
            FROM rezerwacja_skrytki rs
            JOIN status_rezerwacji sr ON rs.status_id = sr.id
            WHERE rs.przesylka_id = %s
            ORDER BY rs.data_rezerwacji DESC
            LIMIT 1
        """, (przesylka_id,))
        rez = cur.fetchone()

        if rez:
            skrytka_id = rez["skrytka_id"]

            # zwolnij skrytkę
            cur.execute("""
                UPDATE skrytka
                SET status_id = (SELECT id FROM status_skrytki WHERE status = 'Wolna')
                WHERE id = %s
            """, (skrytka_id,))

            # oznacz rezerwację jako zakończoną
            cur.execute("""
                UPDATE rezerwacja_skrytki
                SET status_id = (SELECT id FROM status_rezerwacji WHERE status = 'Zwolniona'),
                    data_wygasniecia = CURRENT_TIMESTAMP
                WHERE przesylka_id = %s
                  AND skrytka_id = %s
                  AND status_id = %s
            """, (przesylka_id, skrytka_id, rez["status_id"]))

        # 3. zmień status przesyłki na 'Odebrana'
        cur.execute("""
            UPDATE przesylka
            SET status_id = (SELECT id FROM status_przesylki WHERE status = 'Odebrana')
            WHERE id = %s
        """, (przesylka_id,))

        # 4. wpis do historii statusów
        cur.execute("""
            INSERT INTO historia_statusu (
                przesylka_id, status_z_id, status_na_id, zmienil, data_zmiany, uwagi
            )
            VALUES (
                %s,
                (SELECT id FROM status_przesylki WHERE status = 'Doręczona'),
                (SELECT id FROM status_przesylki WHERE status = 'Odebrana'),
                %s,
                CURRENT_TIMESTAMP,
                'Odbiór przesyłki przez odbiorcę'
            )
        """, (przesylka_id, str(session["user_id"])))

        conn.commit()
        flash("Przesyłka odebrana. Skrytka została zwolniona.", "success")
        return redirect(url_for("klient.dashboard"))
    finally:
        cur.close()
        conn.close()

@przesylka_bp.route("/api/koszt", methods=["GET"])
@login_required
def api_koszt_przesylki():
    if session.get('user_type') != 'Klient':
        return jsonify({"error": "Brak dostępu"}), 403

    try:
        paczkomat_nadania_id = int(request.args.get("paczkomat_nadania_id"))
        paczkomat_docelowy_id = int(request.args.get("paczkomat_docelowy_id"))
        rozmiar_id = int(request.args.get("rozmiar_id"))
        waga = float(request.args.get("waga", 0))
    except (TypeError, ValueError):
        return jsonify({"error": "Nieprawidłowe dane"}), 400

    koszt_info = oblicz_koszt_przesylki(
        paczkomat_nadania_id,
        paczkomat_docelowy_id,
        rozmiar_id,
        waga
    )
    if not koszt_info:
        return jsonify({"error": "Nie można wyliczyć kosztu"}), 500

    return jsonify({"koszt": float(koszt_info["koszt"])})


@przesylka_bp.route("/<int:przesylka_id>/zglos_uszkodzenie", methods=["POST"])
@login_required
def zglos_uszkodzenie(przesylka_id):
    # tylko klient
    if session.get("user_type") != "Klient":
        return "Brak dostępu", 403

    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500

    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        # sprawdź, czy przesyłka istnieje i czy to jej odbiorca
        cur.execute(
            """
            SELECT p.id,
                   p.odbiorca_id,
                   p.flaga_uszkodzona,
                   p.status_id,
                   sp.status
            FROM przesylka p
            JOIN status_przesylki sp ON p.status_id = sp.id
            WHERE p.id = %s
            """,
            (przesylka_id,),
        )
        p = cur.fetchone()
        if not p:
            return "Przesyłka nie istnieje", 404

        if p["odbiorca_id"] != session["user_id"]:
            return "Brak dostępu", 403

        if p["status"] != "Odebrana":
            flash(
                "Uszkodzenie można zgłosić tylko dla przesyłki w statusie Odebrana.",
                "warning",
            )
            return redirect(
                url_for("klient.szczegoly_przesylki", przesylka_id=przesylka_id)
            )

        if p["flaga_uszkodzona"]:
            flash(
                "Uszkodzenie tej przesyłki zostało już zgłoszone.",
                "info",
            )
            return redirect(
                url_for("klient.szczegoly_przesylki", przesylka_id=przesylka_id)
            )

        # ustaw flagę na true
        cur.execute(
            "UPDATE przesylka SET flaga_uszkodzona = TRUE WHERE id = %s",
            (przesylka_id,),
        )

        # wpis do historii (status się nie zmienia – z/na ten sam)
        cur.execute(
            """
            INSERT INTO historia_statusu
                (przesylka_id, status_z_id, status_na_id,
                 zmienil, data_zmiany, uwagi)
            VALUES (%s, %s, %s, %s, CURRENT_TIMESTAMP,
                    'Klient zgłosił uszkodzenie przesyłki')
            """,
            (
                przesylka_id,
                p["status_id"],
                p["status_id"],
                str(session["user_id"]),
            ),
        )

        conn.commit()
        flash("Uszkodzenie przesyłki zostało zgłoszone.", "success")
        return redirect(
            url_for("klient.szczegoly_przesylki", przesylka_id=przesylka_id)
        )
    finally:
        cur.close()
        conn.close()

@przesylka_bp.route("/<int:przesylka_id>/uwagi_uszkodzenie", methods=["POST"])
@login_required
def uwagi_uszkodzenie(przesylka_id):
    if session.get("user_type") != "Klient":
        return "Brak dostępu", 403

    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500

    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        # sprawdź, czy przesyłka należy do odbiorcy i jest oznaczona jako uszkodzona
        cur.execute(
            """
            SELECT p.id, p.odbiorca_id, p.flaga_uszkodzona
            FROM przesylka p
            WHERE p.id = %s
            """,
            (przesylka_id,),
        )
        p = cur.fetchone()
        if not p:
            return "Przesyłka nie istnieje", 404

        if p["odbiorca_id"] != session["user_id"]:
            return "Brak dostępu", 403

        if not p["flaga_uszkodzona"]:
            flash("Uwagi można dodać tylko do przesyłki zgłoszonej jako uszkodzona.", "warning")
            return redirect(url_for("klient.szczegoly_przesylki", przesylka_id=przesylka_id))

        uwagi = (request.form.get("uwagi") or "").strip()
        if len(uwagi) > 255:
            uwagi = uwagi[:255]

        cur.execute(
            "UPDATE przesylka SET uwagi = %s WHERE id = %s",
            (uwagi if uwagi else None, przesylka_id),
        )

        conn.commit()
        flash("Uwagi do uszkodzenia zostały zapisane.", "success")
        return redirect(url_for("klient.szczegoly_przesylki", przesylka_id=przesylka_id))
    finally:
        cur.close()
        conn.close()
