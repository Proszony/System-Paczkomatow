from flask import Blueprint, render_template, request, redirect, url_for, session, flash
import psycopg2
from psycopg2.extras import RealDictCursor
from app.helpers import get_conn, validate_paczkomat_code, validate_nazwa_miasta
from app.decorators import login_required, role_required

admin_bp = Blueprint('admin', __name__, url_prefix='/admin')


# ========== HELPER - BEZPIECZNE SORTOWANIE ==========
def get_sort_params(sort_default='id', order_default='asc', allowed_sorts=None):
    """
    Bezpiecznie pobiera parametry sortowania z URL'a.
    
    Args:
        sort_default: domyślna kolumna do sortowania
        order_default: domyślny kierunek (asc/desc)
        allowed_sorts: lista dozwolonych kolumn
    
    Returns:
        (sort, order) - sprawdzone parametry
    """
    if allowed_sorts is None:
        allowed_sorts = [sort_default]
    
    sort = request.args.get('sort', sort_default).lower().strip()
    order = request.args.get('order', order_default).lower().strip()
    
    # Bezpieczeństwo - sprawdzenie whitelist
    if sort not in allowed_sorts:
        sort = sort_default
    if order not in ['asc', 'desc']:
        order = order_default
    
    return sort, order


def get_sort_icon(sort_col, current_sort, current_order):
    """Zwraca ikonę sortowania"""
    if sort_col == current_sort:
        return '⬆️' if current_order == 'asc' else '⬇️'
    return '⬌'  # Ikona neutral


# ============================================
# DASHBOARD
# ============================================

@admin_bp.route("/")
@admin_bp.route("/dashboard")
def dashboard():
    """Dashboard administratora – statystyki ogólne"""
    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # Statystyki
        cur.execute("SELECT COUNT(*) as cnt FROM klient")
        klienci = cur.fetchone()['cnt']
        
        cur.execute("SELECT COUNT(*) as cnt FROM przesylka")
        przesylki = cur.fetchone()['cnt']
        
        cur.execute("SELECT COUNT(*) as cnt FROM pracownik")
        pracownicy = cur.fetchone()['cnt']
        
        cur.execute("SELECT COUNT(*) as cnt FROM centrum_logistyczne")
        centra = cur.fetchone()['cnt']
        
        cur.execute("SELECT COUNT(*) as cnt FROM przesylka WHERE status_id = (SELECT id FROM status_przesylki WHERE status='Doreczona')")
        doreczone = cur.fetchone()['cnt']
        
        cur.execute("SELECT COALESCE(SUM(koszt), 0) as suma FROM przesylka")
        suma_przesylek = cur.fetchone()['suma']
        
        return render_template('admin_dashboard.html',
                             klienci=klienci,
                             przesylki=przesylki,
                             pracownicy=pracownicy,
                             centra=centra,
                             doreczone=doreczone,
                             suma_przesylek=suma_przesylek)
    
    finally:
        cur.close()
        conn.close()

# ==========
# Kierownicy
# ==========

@admin_bp.route("/kierownik/nowy", methods=["GET", "POST"])
@login_required
@role_required('Administrator')
def nowy_kierownik():
    """Tworzenie nowego kierownika"""
    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500
    
    cur = conn.cursor(cursor_factory=RealDictCursor)

    # Pobierz dostępne centra logistyczne
    try:
        cur.execute("""
            SELECT c.id, c.nazwa
            FROM centrum_logistyczne c
            LEFT JOIN kierownik_centrum kc ON c.id = kc.centrum_id
            WHERE kc.centrum_id IS NULL
            ORDER BY c.nazwa
        """)
        centra = cur.fetchall()
    finally:
        pass

    if request.method == "POST":
        imie = request.form.get("imie")
        nazwisko = request.form.get("nazwisko")
        email = request.form.get("email")
        telefon = request.form.get("telefon")
        adres = request.form.get("adres")
        haslo = request.form.get("haslo")
        powtorz_haslo = request.form.get("powtorz_haslo")
        centrum_id = request.form.get("centrum_id")

        # Walidacja
        if not (imie and nazwisko and email and haslo and telefon and centrum_id):
            flash("Imię, nazwisko, email, hasło, telefon i centrum są wymagane.", "danger")
            return render_template("admin_nowy_kierownik.html", centra=centra)

        if haslo != powtorz_haslo:
            flash("Hasła nie są identyczne.", "danger")
            return render_template("admin_nowy_kierownik.html", centra=centra)

        if len(haslo) < 6:
            flash("Hasło musi mieć co najmniej 6 znaków.", "danger")
            return render_template("admin_nowy_kierownik.html", centra=centra)

        # Sprawdź email
        cur.execute("SELECT id FROM pracownik WHERE email = %s", (email,))
        if cur.fetchone():
            flash("Email już istnieje w bazie pracowników.", "danger")
            return render_template("admin_nowy_kierownik.html", centra=centra)

        cur.execute("SELECT id FROM klient WHERE email = %s", (email,))
        if cur.fetchone():
            flash("Email już istnieje w bazie klientów.", "danger")
            return render_template("admin_nowy_kierownik.html", centra=centra)

        try:
            # ID roli "Kierownik"
            cur.execute("SELECT id FROM rola_pracownika WHERE rola = 'Kierownik'")
            rola_result = cur.fetchone()
            if not rola_result:
                flash("Rola 'Kierownik' nie istnieje w bazie.", "danger")
                return render_template("admin_nowy_kierownik.html", centra=centra)
            rola_id = rola_result['id']

            # ID statusu "Aktywny"
            cur.execute("SELECT id FROM status_pracownika WHERE status = 'Aktywny'")
            status_result = cur.fetchone()
            if not status_result:
                flash("Status 'Aktywny' nie istnieje w bazie.", "danger")
                return render_template("admin_nowy_kierownik.html", centra=centra)
            status_id = status_result['id']

            # Haszuj hasło
            hash_hasla = generate_password_hash(haslo)

            # Wstaw pracownika (kierownika)
            cur.execute("""
                INSERT INTO pracownik 
                (imie, nazwisko, email, telefon, adres, haslo_hash, 
                 data_zatrudnienia, status_id, rola_id, centrum_id)
                VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s)
                RETURNING id
            """, (imie, nazwisko, email, telefon, adres if adres else None,
                  hash_hasla, datetime.now().date(), status_id, rola_id, centrum_id))
            
            pracownik_id = cur.fetchone()['id']

            # Wstaw do kierownik_centrum
            cur.execute("""
                INSERT INTO kierownik_centrum 
                (pracownik_id, centrum_id, data_przypisania)
                VALUES (%s, %s, %s)
            """, (pracownik_id, centrum_id, datetime.now().date()))

            conn.commit()
            flash(f"✅ Kierownik {imie} {nazwisko} został utworzony pomyślnie!", "success")
            return redirect(url_for("admin.lista_kierownikow"))

        except Exception as e:
            conn.rollback()
            flash(f"Błąd: {str(e)}", "danger")
            return render_template("admin_nowy_kierownik.html", centra=centra)
        finally:
            cur.close()
            conn.close()

    return render_template("admin_nowy_kierownik.html", centra=centra)


# ============================================
# ZARZĄDZANIE UŻYTKOWNIKAMI
# ============================================

@admin_bp.route("/uzytkownicy")
def uzytkownicy():
    """Lista wszystkich użytkowników (klienci + pracownicy)"""
    sort = request.args.get('sort', 'id').lower()
    order = request.args.get('order', 'asc').lower()
    
    # Whitelist kolumn
    allowed_sorts_klienci = ['id', 'imie', 'nazwisko', 'email']
    if sort not in allowed_sorts_klienci:
        sort = 'id'
    if order not in ['asc', 'desc']:
        order = 'asc'
    
    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500

    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Klienci
        cur.execute(f"""
            SELECT k.id, k.imie, k.nazwisko, k.email, k.telefon,
                   su.status AS status_uzytkownika, 'Klient' as typ
            FROM klient k
            JOIN status_uzytkownika su ON k.status_id = su.id
            ORDER BY k.{sort} {order.upper()}
        """)
        klienci = cur.fetchall()

        # Pracownicy
        cur.execute(f"""
            SELECT p.id, p.imie, p.nazwisko, p.email, '-' as telefon,
                   rp.rola AS status_uzytkownika, 'Pracownik' as typ,
                   c.nazwa AS centrum
            FROM pracownik p
            JOIN rola_pracownika rp ON p.rola_id = rp.id
            LEFT JOIN kierownik_centrum kc ON kc.pracownik_id = p.id
            LEFT JOIN centrum_logistyczne c ON kc.centrum_id = c.id
            ORDER BY p.{sort} {order.upper()}
        """)
        pracownicy = cur.fetchall()

        return render_template("admin_users.html",
                             klienci=klienci,
                             pracownicy=pracownicy,
                             sort=sort,
                             order=order)
    
    finally:
        cur.close()
        conn.close()

# EDYCJE

@admin_bp.route("/klient/<int:klient_id>/edytuj", methods=["GET", "POST"])
@login_required
@role_required('Administrator')
def edytuj_klienta(klient_id):
    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Pobierz klienta
        cur.execute("""
            SELECT k.id, k.imie, k.nazwisko, k.email, k.telefon,
                   k.adres, k.miasto, k.status_id,
                   su.status AS status_nazwa
            FROM klient k
            JOIN status_uzytkownika su ON k.status_id = su.id
            WHERE k.id = %s
        """, (klient_id,))
        klient = cur.fetchone()
        if not klient:
            flash("Klient nie znaleziony.", "danger")
            return redirect(url_for("admin.uzytkownicy"))

        # ID statusów Aktywny / Nieaktywny (do przełącznika)
        cur.execute("""
            SELECT id, status
            FROM status_uzytkownika
            WHERE status IN ('Aktywny', 'Nieaktywny')
        """)
        statusy = {row["status"]: row["id"] for row in cur.fetchall()}

        if request.method == "POST":
            imie = request.form.get("imie", "").strip()
            nazwisko = request.form.get("nazwisko", "").strip()
            email = request.form.get("email", "").strip()
            telefon = request.form.get("telefon", "").strip()
            adres = request.form.get("adres", "").strip()
            miasto = request.form.get("miasto", "").strip()
            nowe_haslo = request.form.get("nowe_haslo", "").strip()
            aktywny = request.form.get("aktywny") == "on"

            if not (imie and nazwisko and email and telefon):
                flash("Imię, nazwisko, email i telefon są wymagane.", "danger")
                return render_template("admin_edytuj_klienta.html",
                                       klient=klient,
                                       statusy=statusy)

            # Unikalność emaila
            cur.execute("""
                SELECT id FROM klient
                WHERE email = %s AND id != %s
            """, (email, klient_id))
            if cur.fetchone():
                flash("Email już istnieje.", "danger")
                return render_template("admin_edytuj_klienta.html",
                                       klient=klient,
                                       statusy=statusy)

            # Unikalność telefonu
            cur.execute("""
                SELECT id FROM klient
                WHERE telefon = %s AND id != %s
            """, (telefon, klient_id))
            if cur.fetchone():
                flash("Telefon już istnieje.", "danger")
                return render_template("admin_edytuj_klienta.html",
                                       klient=klient,
                                       statusy=statusy)

            # Wylicz nowy status_id
            nowy_status_id = statusy['Aktywny'] if aktywny else statusy['Nieaktywny']

            try:
                # Aktualizacja bez hasła
                cur.execute("""
                    UPDATE klient
                    SET imie = %s,
                        nazwisko = %s,
                        email = %s,
                        telefon = %s,
                        adres = %s,
                        miasto = %s,
                        status_id = %s
                    WHERE id = %s
                """, (imie, nazwisko, email, telefon, adres, miasto,
                      nowy_status_id, klient_id))

                # Opcjonalnie aktualizacja hasła (hash w bazie przez pgcrypto)
                if nowe_haslo:
                    cur.execute("""
                        UPDATE klient
                        SET haslo_hash = crypt(%s, gen_salt('bf'))
                        WHERE id = %s
                    """, (nowe_haslo, klient_id))

                conn.commit()
                flash(f"✅ Klient {imie} {nazwisko} został zaktualizowany.", "success")
                return redirect(url_for("admin.uzytkownicy"))
            except Exception as e:
                conn.rollback()
                flash(f"Błąd: {str(e)}", "danger")
                return render_template("admin_edytuj_klienta.html",
                                       klient=klient,
                                       statusy=statusy)

        return render_template("admin_edytuj_klienta.html",
                               klient=klient,
                               statusy=statusy)

    finally:
        cur.close()
        conn.close()

@admin_bp.route("/pracownik/<int:pracownik_id>/edytuj", methods=["GET", "POST"])
@login_required
@role_required('Administrator')
def edytuj_pracownika(pracownik_id):
    """Edycja danych pracownika (w tym roli i opcjonalnie hasła)"""
    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # Pobierz pracownika (z rola_id)
        cur.execute("""
            SELECT
                p.id, p.imie, p.nazwisko, p.email, p.telefon, p.adres,
                p.rola_id,
                rp.rola AS rola_nazwa
            FROM pracownik p
            JOIN rola_pracownika rp ON p.rola_id = rp.id
            WHERE p.id = %s
        """, (pracownik_id,))
        pracownik = cur.fetchone()

        if not pracownik:
            flash("Pracownik nie znaleziony.", "danger")
            return redirect(url_for("admin.uzytkownicy"))

        # Lista ról do selecta
        cur.execute("SELECT id, rola FROM rola_pracownika WHERE id <> 1 ORDER BY id")
        role = cur.fetchall()

        if request.method == "POST":
            imie = request.form.get("imie", "").strip()
            nazwisko = request.form.get("nazwisko", "").strip()
            email = request.form.get("email", "").strip()
            telefon = request.form.get("telefon", "").strip()
            adres = request.form.get("adres", "").strip()
            rola_id = request.form.get("rola_id")
            nowe_haslo = request.form.get("nowe_haslo", "").strip()
            powtorz_haslo = request.form.get("powtorz_haslo", "").strip()

            if not (imie and nazwisko and email and telefon and rola_id):
                flash("Imię, nazwisko, email, telefon i rola są wymagane.", "danger")
                return render_template("admin_edytuj_pracownika.html",
                                       pracownik=pracownik,
                                       role=role)

            # Walidacja hasła (jeśli podano)
            if nowe_haslo:
                if len(nowe_haslo) < 6:
                    flash("Nowe hasło musi mieć co najmniej 6 znaków.", "danger")
                    return render_template("admin_edytuj_pracownika.html",
                                           pracownik=pracownik,
                                           role=role)
                if nowe_haslo != powtorz_haslo:
                    flash("Nowe hasła nie są identyczne.", "danger")
                    return render_template("admin_edytuj_pracownika.html",
                                           pracownik=pracownik,
                                           role=role)

            # Sprawdź czy email nie istnieje u innego pracownika
            cur.execute("""
                SELECT id FROM pracownik
                WHERE email = %s AND id != %s
            """, (email, pracownik_id))
            if cur.fetchone():
                flash("Email już istnieje.", "danger")
                return render_template("admin_edytuj_pracownika.html",
                                       pracownik=pracownik,
                                       role=role)

            # Sprawdź czy telefon nie istnieje u innego pracownika
            cur.execute("""
                SELECT id FROM pracownik
                WHERE telefon = %s AND id != %s
            """, (telefon, pracownik_id))
            if cur.fetchone():
                flash("Telefon już istnieje.", "danger")
                return render_template("admin_edytuj_pracownika.html",
                                       pracownik=pracownik,
                                       role=role)

            try:
                # Aktualizacja danych pracownika
                cur.execute("""
                    UPDATE pracownik
                    SET imie = %s,
                        nazwisko = %s,
                        email = %s,
                        telefon = %s,
                        adres = %s,
                        rola_id = %s
                    WHERE id = %s
                """, (imie, nazwisko, email, telefon, adres,
                      int(rola_id), pracownik_id))

                # Opcjonalnie aktualizacja hasła (hash w bazie przez pgcrypto)
                if nowe_haslo:
                    cur.execute("""
                        UPDATE pracownik
                        SET haslo_hash = crypt(%s, gen_salt('bf'))
                        WHERE id = %s
                    """, (nowe_haslo, pracownik_id))

                conn.commit()
                flash(f"✅ Pracownik {imie} {nazwisko} został zaktualizowany.", "success")
                return redirect(url_for("admin.uzytkownicy"))

            except Exception as e:
                conn.rollback()
                flash(f"Błąd: {str(e)}", "danger")
                return render_template("admin_edytuj_pracownika.html",
                                       pracownik=pracownik,
                                       role=role)

        return render_template("admin_edytuj_pracownika.html",
                               pracownik=pracownik,
                               role=role)

    finally:
        cur.close()
        conn.close()



# ============================================
# MIASTA – CRUD z SORTOWANIEM
# ============================================

@admin_bp.route("/miasta")
def miasta():
    """Lista wszystkich miast"""
    sort, order = get_sort_params('id', 'asc', ['id', 'nazwa', 'kod'])
    
    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        # ✅ Pobierz wszystkie pola miasta
        cur.execute(f"""
            SELECT id, nazwa, kod, szerokosc_geograficzna, dlugosc_geograficzna, liczba_mieszkancow 
            FROM miasto 
            ORDER BY {sort} {order.upper()}
        """)
        lista_miast = cur.fetchall()
        
        return render_template("admin_miasta.html", 
                             miasta=lista_miast,
                             sort=sort,
                             order=order,
                             get_sort_icon=get_sort_icon)
    
    finally:
        cur.close()
        conn.close()



@admin_bp.route("/miasto/new", methods=["GET", "POST"])
def miasto_new():
    """Dodaj nowe miasto"""
    if request.method == "POST":
        nazwa = request.form.get("nazwa", "").strip()
        kod = request.form.get("kod", "").strip().upper()
        szerokosc_geograficzna = request.form.get("szerokosc_geograficzna", "").strip()
        dlugosc_geograficzna = request.form.get("dlugosc_geograficzna", "").strip()
        liczba_mieszkancow = request.form.get("liczba_mieszkancow", "").strip()
        
        # Walidacja
        is_valid, err = validate_nazwa_miasta(nazwa)
        if not is_valid:
            return render_template("admin_edit_miasto.html", 
                                   blad=err, 
                                   miasto=None)
        
        if len(kod) != 3:
            return render_template("admin_edit_miasto.html", 
                                   blad="Kod miasta musi mieć dokładnie 3 znaki",
                                   miasto=None)
        
        try:
            szerokosc = float(szerokosc_geograficzna)
            dlugosc = float(dlugosc_geograficzna)
            if not (-90 <= szerokosc <= 90) or not (-180 <= dlugosc <= 180):
                raise ValueError("Współrzędne poza zakresem")
        except ValueError:
            return render_template("admin_edit_miasto.html", 
                                   blad="Nieprawidłowe współrzędne geograficzne",
                                   miasto=None)
        
        # Konwersja liczby mieszkańców
        liczba_mieszkancow_int = None
        if liczba_mieszkancow:
            try:
                liczba_mieszkancow_int = int(liczba_mieszkancow)
            except ValueError:
                return render_template("admin_edit_miasto.html", 
                                       blad="Liczba mieszkańców musi być liczbą",
                                       miasto=None)
        
        conn = get_conn()
        if not conn:
            return render_template("admin_edit_miasto.html",
                                   blad="Błąd połączenia z bazą"), 500
        cur = conn.cursor()
        
        try:
            # Sprawdzenie unikalności
            cur.execute("SELECT id FROM miasto WHERE nazwa=%s OR kod=%s", (nazwa, kod))
            if cur.fetchone():
                return render_template("admin_edit_miasto.html",
                                       blad="Miasto o takiej nazwie lub kodzie już istnieje",
                                       miasto=None)
            
            cur.execute("""
                INSERT INTO miasto (nazwa, kod, szerokosc_geograficzna, dlugosc_geograficzna, liczba_mieszkancow)
                VALUES (%s, %s, %s, %s, %s)
            """, (nazwa, kod, szerokosc, dlugosc, liczba_mieszkancow_int))
            conn.commit()
            return redirect(url_for("admin.miasta"))
        
        except psycopg2.Error as e:
            conn.rollback()
            return render_template("admin_edit_miasto.html",
                                   blad=f"Błąd bazy: {str(e)[:100]}",
                                   miasto=None)
        
        finally:
            cur.close()
            conn.close()
    
    return render_template("admin_edit_miasto.html", miasto=None)

@admin_bp.route("/miasto/<int:miasto_id>/edit", methods=["GET", "POST"])
def miasto_edit(miasto_id):
    """Edytuj miasto"""
    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        if request.method == "POST":
            nazwa = request.form.get("nazwa", "").strip()
            kod = request.form.get("kod", "").strip().upper()
            szerokosc_geograficzna = request.form.get("szerokosc_geograficzna", "").strip()
            dlugosc_geograficzna = request.form.get("dlugosc_geograficzna", "").strip()
            liczba_mieszkancow = request.form.get("liczba_mieszkancow", "").strip()
            
            # Walidacja
            is_valid, err = validate_nazwa_miasta(nazwa)
            if not is_valid:
                cur.execute("SELECT id, nazwa, kod, szerokosc_geograficzna, dlugosc_geograficzna, liczba_mieszkancow FROM miasto WHERE id=%s", (miasto_id,))
                miasto = cur.fetchone()
                return render_template("admin_edit_miasto.html",
                                       blad=err,
                                       miasto=miasto)
            
            if len(kod) != 3:
                cur.execute("SELECT id, nazwa, kod, szerokosc_geograficzna, dlugosc_geograficzna, liczba_mieszkancow FROM miasto WHERE id=%s", (miasto_id,))
                miasto = cur.fetchone()
                return render_template("admin_edit_miasto.html",
                                       blad="Kod miasta musi mieć dokładnie 3 znaki",
                                       miasto=miasto)
            
            try:
                szerokosc = float(szerokosc_geograficzna)
                dlugosc = float(dlugosc_geograficzna)
                if not (-90 <= szerokosc <= 90) or not (-180 <= dlugosc <= 180):
                    raise ValueError("Współrzędne poza zakresem")
            except ValueError:
                cur.execute("SELECT id, nazwa, kod, szerokosc_geograficzna, dlugosc_geograficzna, liczba_mieszkancow FROM miasto WHERE id=%s", (miasto_id,))
                miasto = cur.fetchone()
                return render_template("admin_edit_miasto.html",
                                       blad="Nieprawidłowe współrzędne geograficzne",
                                       miasto=miasto)
            
            # Konwersja liczby mieszkańców
            liczba_mieszkancow_int = None
            if liczba_mieszkancow:
                try:
                    liczba_mieszkancow_int = int(liczba_mieszkancow)
                except ValueError:
                    cur.execute("SELECT id, nazwa, kod, szerokosc_geograficzna, dlugosc_geograficzna, liczba_mieszkancow FROM miasto WHERE id=%s", (miasto_id,))
                    miasto = cur.fetchone()
                    return render_template("admin_edit_miasto.html",
                                           blad="Liczba mieszkańców musi być liczbą",
                                           miasto=miasto)
            
            # Sprawdzenie unikalności (wyłączając to miasto)
            cur.execute("""
                SELECT id FROM miasto WHERE (nazwa=%s OR kod=%s) AND id <> %s
            """, (nazwa, kod, miasto_id))
            if cur.fetchone():
                cur.execute("SELECT id, nazwa, kod, szerokosc_geograficzna, dlugosc_geograficzna, liczba_mieszkancow FROM miasto WHERE id=%s", (miasto_id,))
                miasto = cur.fetchone()
                return render_template("admin_edit_miasto.html",
                                       blad="Miasto o takiej nazwie lub kodzie już istnieje",
                                       miasto=miasto)
            
            cur.execute("""
                UPDATE miasto 
                SET nazwa=%s, kod=%s, szerokosc_geograficzna=%s, dlugosc_geograficzna=%s, liczba_mieszkancow=%s
                WHERE id=%s
            """, (nazwa, kod, szerokosc, dlugosc, liczba_mieszkancow_int, miasto_id))
            conn.commit()
            return redirect(url_for("admin.miasta"))
        
        # GET – wczytaj dane
        cur.execute("""
            SELECT id, nazwa, kod, szerokosc_geograficzna, dlugosc_geograficzna, liczba_mieszkancow 
            FROM miasto WHERE id=%s
        """, (miasto_id,))
        miasto = cur.fetchone()
        
        return render_template("admin_edit_miasto.html", miasto=miasto)
    
    finally:
        cur.close()
        conn.close()


@admin_bp.route("/miasto/<int:miasto_id>/delete", methods=["POST"])
def miasto_delete(miasto_id):
    """Usuń miasto"""
    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500
    
    cur = conn.cursor()
    
    try:
        # Sprawdzenie czy miasto jest używane w centrach
        cur.execute("""
            SELECT COUNT(*) as cnt FROM centrum_logistyczne WHERE miasto_id=%s
        """, (miasto_id,))
        result = cur.fetchone()
        
        if result[0] > 0:
            return render_template("admin_miasta.html",
                                   blad="Nie można usunąć miasta - jest używane w centrach logistycznych"), 400
        
        # Usunięcie miasta
        cur.execute("DELETE FROM miasto WHERE id=%s", (miasto_id,))
        conn.commit()
        
        return redirect(url_for("admin.miasta"))
    
    except psycopg2.Error as e:
        conn.rollback()
        return "Błąd bazy: " + str(e)[:100], 500
    
    finally:
        cur.close()
        conn.close()


# ============================================
# CENTRA LOGISTYCZNE – CRUD z SORTOWANIEM
# ============================================

@admin_bp.route("/centra")
def centra():
    """Lista wszystkich centrów logistycznych"""
    sort, order = get_sort_params('id', 'asc', ['id', 'nazwa', 'adres'])
    
    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        cur.execute(f"""
            SELECT c.id, c.nazwa, c.adres, m.nazwa as miasto, c.status_id
            FROM centrum_logistyczne c
            JOIN miasto m ON c.miasto_id = m.id
            ORDER BY c.{sort} {order.upper()}
        """)
        lista_centrów = cur.fetchall()
        
        return render_template("admin_centra.html", 
                             centra=lista_centrów,
                             sort=sort,
                             order=order,
                             get_sort_icon=get_sort_icon)
    
    finally:
        cur.close()
        conn.close()


@admin_bp.route("/centrum/new", methods=["GET", "POST"])
def centrum_new():
    """Dodaj nowe centrum"""
    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500
    
    if request.method == "POST":
        nazwa = request.form.get("nazwa", "").strip()
        adres = request.form.get("adres", "").strip()
        miasto_id = request.form.get("miasto_id", "").strip()
        szerokosc_geograficzna = request.form.get("szerokosc_geograficzna", "").strip()
        dlugosc_geograficzna = request.form.get("dlugosc_geograficzna", "").strip()
        pojemnosc = request.form.get("pojemnosc", "").strip()
        
        # Walidacja - wszystkie pola wymagane
        if not all([nazwa, adres, miasto_id, szerokosc_geograficzna, dlugosc_geograficzna, pojemnosc]):
            cur = conn.cursor(cursor_factory=RealDictCursor)
            try:
                cur.execute("SELECT id, nazwa FROM miasto ORDER BY nazwa")
                miasta = cur.fetchall()
            finally:
                cur.close()
            return render_template("admin_edit_centrum.html",
                                   blad="Wszystkie pola są wymagane",
                                   miasta=miasta,
                                   centrum=None)
        
        # Konwersja typów
        try:
            miasto_id = int(miasto_id)
            pojemnosc_int = int(pojemnosc)
            
            # ✅ ZAMIANA PRZECINKA NA KROPKĘ
            szerokosc_text = szerokosc_geograficzna.replace(',', '.')
            dlugosc_text = dlugosc_geograficzna.replace(',', '.')
            
            szerokosc = float(szerokosc_text)
            dlugosc = float(dlugosc_text)
            
            # Walidacja zakresów
            if not (-90 <= szerokosc <= 90):
                raise ValueError("Szerokość geograficzna musi być między -90 a 90")
            if not (-180 <= dlugosc <= 180):
                raise ValueError("Długość geograficzna musi być między -180 a 180")
            if pojemnosc_int < 1:
                raise ValueError("Pojemność musi być większa od 0")
        
        except ValueError as e:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            try:
                cur.execute("SELECT id, nazwa FROM miasto ORDER BY nazwa")
                miasta = cur.fetchall()
            finally:
                cur.close()
            return render_template("admin_edit_centrum.html",
                                   blad=f"Błędne dane: {str(e)}",
                                   miasta=miasta,
                                   centrum=None)
        
        cur = conn.cursor()
        try:
            cur.execute("""
                INSERT INTO centrum_logistyczne 
                (nazwa, adres, miasto_id, szerokosc_geograficzna, dlugosc_geograficzna, pojemnosc, status_id)
                VALUES (%s, %s, %s, %s, %s, %s, (SELECT id FROM status_centrum WHERE status='Aktywne'))
            """, (nazwa, adres, miasto_id, szerokosc, dlugosc, pojemnosc_int))
            conn.commit()
            return redirect(url_for("admin.centra"))
        
        except psycopg2.Error as e:
            conn.rollback()
            cur = conn.cursor(cursor_factory=RealDictCursor)
            try:
                cur.execute("SELECT id, nazwa FROM miasto ORDER BY nazwa")
                miasta = cur.fetchall()
            finally:
                cur.close()
            return render_template("admin_edit_centrum.html",
                                   blad=f"Błąd bazy: {str(e)[:100]}",
                                   miasta=miasta,
                                   centrum=None)
        
        finally:
            cur.close()
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("SELECT id, nazwa FROM miasto ORDER BY nazwa")
        miasta = cur.fetchall()
    finally:
        cur.close()
    
    conn.close()
    return render_template("admin_edit_centrum.html", 
                          miasta=miasta,
                          centrum=None)


@admin_bp.route("/centrum/<int:centrum_id>/edit", methods=["GET", "POST"])
def centrum_edit(centrum_id):
    """Edytuj centrum"""
    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        if request.method == "POST":
            nazwa = request.form.get("nazwa", "").strip()
            adres = request.form.get("adres", "").strip()
            miasto_id = request.form.get("miasto_id", "").strip()
            szerokosc_geograficzna = request.form.get("szerokosc_geograficzna", "").strip()
            dlugosc_geograficzna = request.form.get("dlugosc_geograficzna", "").strip()
            pojemnosc = request.form.get("pojemnosc", "").strip()
            
            # Walidacja - wszystkie pola wymagane
            if not all([nazwa, adres, miasto_id, szerokosc_geograficzna, dlugosc_geograficzna, pojemnosc]):
                cur.execute("SELECT id, nazwa FROM miasto ORDER BY nazwa")
                miasta = cur.fetchall()
                cur.execute("""
                    SELECT id, nazwa, adres, miasto_id, szerokosc_geograficzna, dlugosc_geograficzna, pojemnosc 
                    FROM centrum_logistyczne WHERE id=%s
                """, (centrum_id,))
                centrum = cur.fetchone()
                
                return render_template("admin_edit_centrum.html",
                                       blad="Wszystkie pola są wymagane",
                                       miasta=miasta,
                                       centrum=centrum)
            
            # Konwersja typów
            try:
                miasto_id = int(miasto_id)
                pojemnosc_int = int(pojemnosc)
                
                # ✅ ZAMIANA PRZECINKA NA KROPKĘ
                szerokosc_text = szerokosc_geograficzna.replace(',', '.')
                dlugosc_text = dlugosc_geograficzna.replace(',', '.')
                
                szerokosc = float(szerokosc_text)
                dlugosc = float(dlugosc_text)
                
                # Walidacja zakresów
                if not (-90 <= szerokosc <= 90):
                    raise ValueError("Szerokość geograficzna musi być między -90 a 90")
                if not (-180 <= dlugosc <= 180):
                    raise ValueError("Długość geograficzna musi być między -180 a 180")
                if pojemnosc_int < 1:
                    raise ValueError("Pojemność musi być większa od 0")
            
            except ValueError as e:
                cur.execute("SELECT id, nazwa FROM miasto ORDER BY nazwa")
                miasta = cur.fetchall()
                cur.execute("""
                    SELECT id, nazwa, adres, miasto_id, szerokosc_geograficzna, dlugosc_geograficzna, pojemnosc 
                    FROM centrum_logistyczne WHERE id=%s
                """, (centrum_id,))
                centrum = cur.fetchone()
                
                return render_template("admin_edit_centrum.html",
                                       blad=f"Błędne dane: {str(e)}",
                                       miasta=miasta,
                                       centrum=centrum)
            
            # UPDATE
            try:
                cur.execute("""
                    UPDATE centrum_logistyczne
                    SET nazwa=%s, adres=%s, miasto_id=%s, szerokosc_geograficzna=%s, dlugosc_geograficzna=%s, pojemnosc=%s
                    WHERE id=%s
                """, (nazwa, adres, miasto_id, szerokosc, dlugosc, pojemnosc_int, centrum_id))
                conn.commit()
                return redirect(url_for("admin.centra"))
            
            except psycopg2.Error as e:
                conn.rollback()
                cur.execute("SELECT id, nazwa FROM miasto ORDER BY nazwa")
                miasta = cur.fetchall()
                cur.execute("""
                    SELECT id, nazwa, adres, miasto_id, szerokosc_geograficzna, dlugosc_geograficzna, pojemnosc 
                    FROM centrum_logistyczne WHERE id=%s
                """, (centrum_id,))
                centrum = cur.fetchone()
                
                return render_template("admin_edit_centrum.html",
                                       blad=f"Błąd bazy: {str(e)[:100]}",
                                       miasta=miasta,
                                       centrum=centrum)
        
        # GET – wczytaj dane
        cur.execute("""
            SELECT id, nazwa, adres, miasto_id, szerokosc_geograficzna, dlugosc_geograficzna, pojemnosc 
            FROM centrum_logistyczne WHERE id=%s
        """, (centrum_id,))
        centrum = cur.fetchone()
        
        cur.execute("SELECT id, nazwa FROM miasto ORDER BY nazwa")
        miasta = cur.fetchall()
        
        return render_template("admin_edit_centrum.html", centrum=centrum, miasta=miasta)
    
    finally:
        cur.close()
        conn.close()

@admin_bp.route("/centrum/<int:centrum_id>/delete", methods=["POST"])
def centrum_delete(centrum_id):
    """Usuń centrum"""
    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500
    cur = conn.cursor()
    
    try:
        # Sprawdzenie czy są powiązane paczkomaty
        cur.execute("SELECT id FROM paczkomat WHERE centrum_id=%s", (centrum_id,))
        if cur.fetchone():
            return "Nie można usunąć centrum z przypisanymi paczkomatami", 400
        
        cur.execute("DELETE FROM centrum_logistyczne WHERE id=%s", (centrum_id,))
        conn.commit()
        return redirect(url_for("admin.centra"))
    
    except psycopg2.Error as e:
        conn.rollback()
        return f"Błąd bazy: {str(e)[:100]}", 500
    
    finally:
        cur.close()
        conn.close()


# ============================================
# PACZKOMATY – CRUD z SORTOWANIEM
# ============================================

@admin_bp.route("/paczkomaty")
def paczkomaty():
    """Lista wszystkich paczkomatów z zapełnieniem skrytek S/M/L."""
    sort, order = get_sort_params('id', 'asc', ['id', 'kod', 'adres'])

    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        cur.execute(f"""
            SELECT
                p.id,
                p.kod,
                p.adres,
                m.nazwa AS miasto,
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
            JOIN miasto m ON c.miasto_id = m.id
            LEFT JOIN skrytka s ON s.paczkomat_id = p.id
            LEFT JOIN status_skrytki ss ON s.status_id = ss.id
            GROUP BY p.id, p.kod, p.adres, m.nazwa, c.nazwa
            ORDER BY p.{sort} {order.upper()}
        """)

        lista_paczkomatów = cur.fetchall()

        return render_template(
            "admin_paczkomaty.html",
            paczkomaty=lista_paczkomatów,
            sort=sort,
            order=order,
            get_sort_icon=get_sort_icon
        )

    finally:
        cur.close()
        conn.close()

@admin_bp.route("/paczkomat/new", methods=["GET", "POST"])
def paczkomat_new():
    """Dodaj nowy paczkomat"""
    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500

    def load_centra(cur):
        cur.execute("SELECT c.id, c.nazwa FROM centrum_logistyczne c ORDER BY c.nazwa")
        return cur.fetchall()

    if request.method == "POST":
        kod = request.form.get("kod", "").strip().upper()
        adres = request.form.get("adres", "").strip()
        centrum_id = int(request.form.get("centrum_id", 0) or 0)

        szer = request.form.get("szerokosc_geograficzna", "").strip()
        dl = request.form.get("dlugosc_geograficzna", "").strip()

        sk_s = int(request.form.get("liczba_skrytek_s", 0) or 0)
        sk_m = int(request.form.get("liczba_skrytek_m", 0) or 0)
        sk_l = int(request.form.get("liczba_skrytek_l", 0) or 0)

        cur = conn.cursor(cursor_factory=RealDictCursor)
        try:
            centra = load_centra(cur)

            # walidacja pól
            if not all([kod, adres, centrum_id, szer, dl]) or (sk_s <= 0 and sk_m <= 0 and sk_l <= 0):
                return render_template(
                    "admin_edit_paczkomat.html",
                    blad="Kod, adres, centrum, współrzędne i liczby skrytek są wymagane.",
                    centra=centra,
                    paczkomat=None
                )

            is_valid, err = validate_paczkomat_code(kod)
            if not is_valid:
                return render_template(
                    "admin_edit_paczkomat.html",
                    blad=err,
                    centra=centra,
                    paczkomat=None
                )

            # sprawdź unikalność kodu
            cur.execute("SELECT id FROM paczkomat WHERE kod=%s", (kod,))
            if cur.fetchone():
                return render_template(
                    "admin_edit_paczkomat.html",
                    blad="Paczkomat o takim kodzie już istnieje",
                    centra=centra,
                    paczkomat=None
                )

            # INSERT nowego paczkomatu + wygenerowanie skrytek
            cur2 = conn.cursor()
            try:
                # 1. paczkomat
                cur2.execute("""
                    INSERT INTO paczkomat (
                        kod, adres, centrum_id,
                        szerokosc_geograficzna, dlugosc_geograficzna,
                        liczba_skrytek_s, liczba_skrytek_m, liczba_skrytek_l,
                        status_id
                    )
                    VALUES (
                        %s, %s, %s,
                        %s, %s,
                        %s, %s, %s,
                        (SELECT id FROM status_paczkomatu WHERE status='Sprawny')
                    )
                    RETURNING id
                """, (kod, adres, centrum_id,
                      szer, dl,
                      sk_s, sk_m, sk_l))
                paczkomat_id = cur2.fetchone()[0]

                # 2. wygeneruj skrytki S/M/L (status 'Wolna')
                numer = 1

                cur2.execute("SELECT id FROM status_skrytki WHERE status = 'Wolna'")
                status_wolna_id = cur2.fetchone()[0]

                # S
                cur2.execute("SELECT id FROM rozmiar_skrytki WHERE rozmiar = 'S'")
                rozmiar_s_id = cur2.fetchone()[0]
                for _ in range(sk_s):
                    cur2.execute("""
                        INSERT INTO skrytka (paczkomat_id, numer_skrytki, rozmiar_id, status_id)
                        VALUES (%s, %s, %s, %s)
                    """, (paczkomat_id, numer, rozmiar_s_id, status_wolna_id))
                    numer += 1

                # M
                cur2.execute("SELECT id FROM rozmiar_skrytki WHERE rozmiar = 'M'")
                rozmiar_m_id = cur2.fetchone()[0]
                for _ in range(sk_m):
                    cur2.execute("""
                        INSERT INTO skrytka (paczkomat_id, numer_skrytki, rozmiar_id, status_id)
                        VALUES (%s, %s, %s, %s)
                    """, (paczkomat_id, numer, rozmiar_m_id, status_wolna_id))
                    numer += 1

                # L
                cur2.execute("SELECT id FROM rozmiar_skrytki WHERE rozmiar = 'L'")
                rozmiar_l_id = cur2.fetchone()[0]
                for _ in range(sk_l):
                    cur2.execute("""
                        INSERT INTO skrytka (paczkomat_id, numer_skrytki, rozmiar_id, status_id)
                        VALUES (%s, %s, %s, %s)
                    """, (paczkomat_id, numer, rozmiar_l_id, status_wolna_id))
                    numer += 1

                conn.commit()
            finally:
                cur2.close()

            return redirect(url_for("admin.paczkomaty"))

        except psycopg2.Error as e:
            conn.rollback()
            return render_template(
                "admin_edit_paczkomat.html",
                blad=f"Błąd bazy: {str(e)[:100]}",
                centra=centra,
                paczkomat=None
            )
        finally:
            cur.close()

    # GET – formularz pusty
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        centra = load_centra(cur)
    finally:
        cur.close()
        conn.close()

    return render_template(
        "admin_edit_paczkomat.html",
        centra=centra,
        paczkomat=None
    )


@admin_bp.route("/paczkomat/<int:paczkomat_id>/edit", methods=["GET", "POST"])
def paczkomat_edit(paczkomat_id):
    """Edytuj paczkomat"""
    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500
    cur = conn.cursor(cursor_factory=RealDictCursor)
    
    try:
        if request.method == "POST":
            kod = request.form.get("kod", "").strip().upper()
            adres = request.form.get("adres", "").strip()
            centrum_id = int(request.form.get("centrum_id", 0) or 0)

            sk_s = int(request.form.get("liczba_skrytek_s", 0) or 0)
            sk_m = int(request.form.get("liczba_skrytek_m", 0) or 0)
            sk_l = int(request.form.get("liczba_skrytek_l", 0) or 0)

            szer = request.form.get("szerokosc_geograficzna", "").strip()
            dl = request.form.get("dlugosc_geograficzna", "").strip()
            
            if not all([kod, adres, centrum_id, szer, dl]) or (sk_s <= 0 and sk_m <= 0 and sk_l <= 0):
                cur.execute("SELECT c.id, c.nazwa FROM centrum_logistyczne c ORDER BY c.nazwa")
                centra = cur.fetchall()
                paczkomat_ctx = {
                    "id": paczkomat_id,
                    "kod": kod,
                    "adres": adres,
                    "centrum_id": centrum_id,
                    "liczba_skrytek_s": sk_s,
                    "liczba_skrytek_m": sk_m,
                    "liczba_skrytek_l": sk_l,
                    "szerokosc_geograficzna": szer,
                    "dlugosc_geograficzna": dl,
                }
                return render_template(
                    "admin_edit_paczkomat.html",
                    blad="Kod, adres, centrum, współrzędne i liczby skrytek są wymagane.",
                    centra=centra,
                    paczkomat=paczkomat_ctx
                )
            
            is_valid, err = validate_paczkomat_code(kod)
            if not is_valid:
                cur.execute("SELECT c.id, c.nazwa FROM centrum_logistyczne c ORDER BY c.nazwa")
                centra = cur.fetchall()
                paczkomat_ctx = {
                    "id": paczkomat_id,
                    "kod": kod,
                    "adres": adres,
                    "centrum_id": centrum_id,
                    "liczba_skrytek_s": sk_s,
                    "liczba_skrytek_m": sk_m,
                    "liczba_skrytek_l": sk_l,
                    "szerokosc_geograficzna": szer,
                    "dlugosc_geograficzna": dl,
                }
                return render_template(
                    "admin_edit_paczkomat.html",
                    blad=err,
                    centra=centra,
                    paczkomat=paczkomat_ctx
                )
            
            try:
                # 1. aktualizacja paczkomatu
                cur.execute("""
                    UPDATE paczkomat
                    SET kod=%s,
                        adres=%s,
                        centrum_id=%s,
                        liczba_skrytek_s=%s,
                        liczba_skrytek_m=%s,
                        liczba_skrytek_l=%s,
                        szerokosc_geograficzna=%s,
                        dlugosc_geograficzna=%s
                    WHERE id=%s
                """, (kod, adres, centrum_id,
                      sk_s, sk_m, sk_l,
                      szer, dl,
                      paczkomat_id))

                # 2. dopisz brakujące skrytki (bez kasowania istniejących)
                cur.execute("""
                    SELECT rs.rozmiar, COUNT(*) AS ile
                    FROM skrytka s
                    JOIN rozmiar_skrytki rs ON s.rozmiar_id = rs.id
                    WHERE s.paczkomat_id = %s
                    GROUP BY rs.rozmiar
                """, (paczkomat_id,))
                istniejące = {row["rozmiar"]: row["ile"] for row in cur.fetchall()}

                cur.execute("SELECT id FROM status_skrytki WHERE status = 'Wolna'")
                row = cur.fetchone()
                if not row:
                    raise Exception("Brak statusu 'Wolna' w tabeli status_skrytki")
                status_wolna_id = row["id"]

                def dopisz(rozmiar_litera, docelowa_liczba):
                    cur.execute("SELECT id FROM rozmiar_skrytki WHERE rozmiar = %s", (rozmiar_litera,))
                    r = cur.fetchone()
                    if not r:
                        raise Exception(f"Brak rozmiaru '{rozmiar_litera}' w tabeli rozmiar_skrytki")
                    rozmiar_id = r["id"]

                    aktualnie = istniejące.get(rozmiar_litera, 0)
                    if docelowa_liczba > aktualnie:
                        cur.execute("""
                            SELECT COALESCE(MAX(numer_skrytki), 0) AS max_nr
                            FROM skrytka
                            WHERE paczkomat_id = %s
                        """, (paczkomat_id,))
                        start = cur.fetchone()["max_nr"] + 1
                        ile_dodac = docelowa_liczba - aktualnie
                        for offset in range(ile_dodac):
                            cur.execute("""
                                INSERT INTO skrytka (paczkomat_id, numer_skrytki, rozmiar_id, status_id)
                                VALUES (%s, %s, %s, %s)
                            """, (paczkomat_id, start + offset, rozmiar_id, status_wolna_id))

                dopisz('S', sk_s)
                dopisz('M', sk_m)
                dopisz('L', sk_l)

                conn.commit()
                return redirect(url_for("admin.paczkomaty"))

            except psycopg2.Error as e:
                conn.rollback()
                cur.execute("SELECT c.id, c.nazwa FROM centrum_logistyczne c ORDER BY c.nazwa")
                centra = cur.fetchall()
                paczkomat_ctx = {
                    "id": paczkomat_id,
                    "kod": kod,
                    "adres": adres,
                    "centrum_id": centrum_id,
                    "liczba_skrytek_s": sk_s,
                    "liczba_skrytek_m": sk_m,
                    "liczba_skrytek_l": sk_l,
                    "szerokosc_geograficzna": szer,
                    "dlugosc_geograficzna": dl,
                }
                return render_template(
                    "admin_edit_paczkomat.html",
                    blad=f"Błąd bazy: {str(e)[:120]}",
                    centra=centra,
                    paczkomat=paczkomat_ctx
                )
        
        # GET
        cur.execute("""
            SELECT id, kod, adres, centrum_id,
                   liczba_skrytek_s, liczba_skrytek_m, liczba_skrytek_l,
                   szerokosc_geograficzna, dlugosc_geograficzna
            FROM paczkomat
            WHERE id=%s
        """, (paczkomat_id,))
        paczkomat = cur.fetchone()
        
        cur.execute("SELECT c.id, c.nazwa FROM centrum_logistyczne c ORDER BY c.nazwa")
        centra = cur.fetchall()
        
        return render_template("admin_edit_paczkomat.html", paczkomat=paczkomat, centra=centra)
    
    finally:
        cur.close()
        conn.close()


@admin_bp.route("/paczkomat/<int:paczkomat_id>/delete", methods=["POST"])
def paczkomat_delete(paczkomat_id):
    """Usuń paczkomat"""
    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500
    cur = conn.cursor()
    
    try:
        cur.execute("DELETE FROM paczkomat WHERE id=%s", (paczkomat_id,))
        conn.commit()
        return redirect(url_for("admin.paczkomaty"))
    
    except psycopg2.Error as e:
        conn.rollback()
        return f"Błąd bazy: {str(e)[:100]}", 500
    
    finally:
        cur.close()
        conn.close()


# edycja przesyłek
@admin_bp.route("/przesylka/<int:przesylka_id>/edytuj", methods=["GET", "POST"])
@login_required
@role_required('Administrator')
def admin_edytuj_przesylke(przesylka_id):
    conn = get_conn()
    if not conn:
        return "Błąd połączenia z bazą", 500
    cur = conn.cursor(cursor_factory=RealDictCursor)

    try:
        # 1. Pobierz przesyłkę z aktualnym statusem i paczkomatem docelowym
        cur.execute("""
            SELECT 
                p.id,
                p.numer_przesylki,
                p.status_id,
                sp.status AS status_nazwa,
                p.paczkomat_docelowy_id,
                pd.kod AS paczkomat_docelowy_kod,
                p.uwagi,
                p.flaga_uszkodzona
            FROM przesylka p
            JOIN status_przesylki sp ON p.status_id = sp.id
            JOIN paczkomat pd ON p.paczkomat_docelowy_id = pd.id
            WHERE p.id = %s
        """, (przesylka_id,))
        przesylka = cur.fetchone()
        if not przesylka:
            flash("Przesyłka nie istnieje.", "danger")
            return redirect(url_for("przesylka.lista"))

        # 2. Lista statusów do selecta
        cur.execute("SELECT id, status FROM status_przesylki ORDER BY id")
        statusy = cur.fetchall()

        if request.method == "POST":
            nowy_status_id = int(request.form.get("status_id"))
            nowy_paczkomat_kod = request.form.get("paczkomat_docelowy_kod", "").strip().upper()
            uwagi = request.form.get("uwagi", "").strip()
            flaga_uszkodzona = request.form.get("flaga_uszkodzona") == "on"

            # Zapamiętaj poprzedni status do historii
            stary_status_id = przesylka["status_id"]

            # 3. Walidacja paczkomatu docelowego (po kodzie)
            cur.execute("""
                SELECT id FROM paczkomat
                WHERE kod = %s
            """, (nowy_paczkomat_kod,))
            paczkomat_row = cur.fetchone()
            if not paczkomat_row:
                flash("Nie znaleziono paczkomatu o podanym kodzie.", "danger")
                return render_template(
                    "admin_edytuj_przesylke.html",
                    przesylka=przesylka,
                    statusy=statusy
                )
            nowy_paczkomat_id = paczkomat_row["id"]

            try:
                # 4. Aktualizacja przesyłki
                cur.execute("""
                    UPDATE przesylka
                    SET status_id = %s,
                        paczkomat_docelowy_id = %s,
                        uwagi = %s,
                        flaga_uszkodzona = %s
                    WHERE id = %s
                """, (nowy_status_id,
                      nowy_paczkomat_id,
                      uwagi,
                      flaga_uszkodzona,
                      przesylka_id))

                # 5. Wpis do historii statusu (jeśli status się zmienił)
                if nowy_status_id != stary_status_id:
                    cur.execute("""
                        INSERT INTO historia_statusu (
                            przesylka_id,
                            status_z_id,
                            status_na_id,
                            zmienil,
                            uwagi
                        )
                        VALUES (
                            %s,
                            %s,
                            %s,
                            %s,
                            %s
                        )
                    """, (
                        przesylka_id,
                        stary_status_id,
                        nowy_status_id,
                        session.get("user_name", "Administrator"),
                        uwagi or f"Zmiana statusu przez admina (ID {session.get('user_id')})"
                    ))

                # 6. (Na później) obsługa skrytek / rezerwacji, jeśli trzeba

                conn.commit()
                flash("✅ Dane przesyłki zostały zaktualizowane.", "success")
                return redirect(url_for("przesylka.status", przesylka_id=przesylka_id))

            except Exception as e:
                conn.rollback()
                flash(f"Błąd podczas aktualizacji: {str(e)}", "danger")
                return render_template(
                    "admin_edytuj_przesylke.html",
                    przesylka=przesylka,
                    statusy=statusy
                )

        return render_template(
            "admin_edytuj_przesylke.html",
            przesylka=przesylka,
            statusy=statusy
        )

    finally:
        cur.close()
        conn.close()
