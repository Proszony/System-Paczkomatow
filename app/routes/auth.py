from flask import Blueprint, render_template, request, redirect, url_for, session
import psycopg2
from psycopg2.extras import RealDictCursor
from app.helpers import get_conn, validate_email, validate_phone
from functools import wraps

auth_bp = Blueprint('auth', __name__, url_prefix='')


def login_required(f):
    """Dekorator do sprawdzenia czy użytkownik jest zalogowany"""
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


@auth_bp.route("/login", methods=["GET", "POST"])
def login():
    """Logowanie użytkownika (admin / kierownik / klient)"""
    
    
    if 'user_id' in session:
        if session.get('user_type') == 'Pracownik':
            if session.get('user_role') == 'Administrator':
                return redirect(url_for('admin.dashboard'))
            elif session.get('user_role') == 'Kierownik':
                return redirect(url_for('kierownik.dashboard'))
        elif session.get('user_type') == 'Klient':
            return redirect(url_for('klient.dashboard'))
    
    if request.method == "POST":
        email = request.form.get("email", "").strip()
        haslo = request.form.get("haslo", "").strip()
        
        if not email or not haslo:
            return render_template("login.html", blad="Email i hasło są wymagane")
        
        conn = get_conn()
        if not conn:
            return render_template("login.html", blad="Błąd połączenia z bazą"), 500
        
        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)
            
            
            cur.execute("""
                SELECT p.id, p.imie, p.nazwisko, p.email, r.rola
                FROM pracownik p
                JOIN rola_pracownika r ON p.rola_id = r.id
                WHERE p.email = %s AND p.haslo_hash = crypt(%s, p.haslo_hash)
            """, (email, haslo))
            
            pracownik = cur.fetchone()
            
            if pracownik:
                session.clear()
                session['user_id'] = pracownik['id']
                session['user_name'] = f"{pracownik['imie']} {pracownik['nazwisko']}"
                session['user_type'] = 'Pracownik'
                session['user_role'] = pracownik['rola']
                
                if pracownik['rola'] == 'Administrator':
                    return redirect(url_for('admin.dashboard'))
                elif pracownik['rola'] == 'Kierownik':
                    return redirect(url_for('kierownik.dashboard'))
            
            
            cur.execute("""
                SELECT id, imie, nazwisko, email
                FROM klient
                WHERE email = %s AND haslo_hash = crypt(%s, haslo_hash)
            """, (email, haslo))
            
            klient = cur.fetchone()
            
            if klient:
                session.clear()
                session['user_id'] = klient['id']
                session['user_name'] = f"{klient['imie']} {klient['nazwisko']}"
                session['user_type'] = 'Klient'
                return redirect(url_for('klient.dashboard'))
            
            
            return render_template("login.html", blad="❌ Błędny email lub hasło")
        
        except psycopg2.Error as e:
            return render_template("login.html", blad=f"Błąd bazy danych: {str(e)[:100]}"), 500
        
        finally:
            cur.close()
            conn.close()
    
    return render_template("login.html")


@auth_bp.route("/logout")
def logout():
    """Wylogowanie użytkownika"""
    session.clear()
    return redirect(url_for('auth.login'))


@auth_bp.route("/register", methods=["GET", "POST"])
def register():
    """Rejestracja nowego klienta"""

    
    if 'user_id' in session:
        return redirect(url_for('klient.dashboard'))

    if request.method == "POST":
        imie = request.form.get("imie", "").strip()
        nazwisko = request.form.get("nazwisko", "").strip()
        email = request.form.get("email", "").strip()
        telefon = request.form.get("telefon", "").strip()
        haslo = request.form.get("haslo", "").strip()

        
        if not all([imie, nazwisko, email, telefon, haslo]):
            return render_template("register.html", blad="❌ Wszystkie pola są wymagane")

        if len(imie) < 2:
            return render_template("register.html", blad="❌ Imię musi mieć min. 2 znaki")

        if len(nazwisko) < 2:
            return render_template("register.html", blad="❌ Nazwisko musi mieć min. 2 znaki")

        if len(haslo) < 6:
            return render_template("register.html", blad="❌ Hasło musi mieć min. 6 znaków")

        is_valid, err = validate_email(email)
        if not is_valid:
            return render_template("register.html", blad=f"❌ {err}")

        is_valid, err = validate_phone(telefon)
        if not is_valid:
            return render_template("register.html", blad=f"❌ {err}")

        conn = get_conn()
        if not conn:
            return render_template("register.html", blad="❌ Błąd połączenia z bazą"), 500

        try:
            cur = conn.cursor(cursor_factory=RealDictCursor)

            
            cur.execute("""
                SELECT id
                FROM klient
                WHERE email = %s OR telefon = %s
            """, (email, telefon))

            if cur.fetchone():
                return render_template(
                    "register.html",
                    blad="❌ Konto z takim adresem e‑mail lub numerem telefonu już istnieje"
                )

            
            
            cur.execute("""
                INSERT INTO klient (
                    imie, nazwisko, email, telefon, haslo_hash,
                    status_id, typ_uzytkownika_id
                )
                VALUES (
                    %s,
                    %s,
                    %s,
                    %s,
                    crypt(%s, gen_salt('bf')),
                    (SELECT id FROM status_uzytkownika WHERE status = 'Aktywny'),
                    (SELECT id FROM typ_uzytkownika WHERE typ = 'Klient')
                )
                RETURNING id
            """, (imie, nazwisko, email, telefon, haslo))

            klient_id = cur.fetchone()["id"]
            conn.commit()

            return render_template(
                "register.html",
                sukces="✅ Konto zostało utworzone! Zaloguj się poniżej."
            )

        except psycopg2.errors.UniqueViolation:
            conn.rollback()
            
            return render_template(
                "register.html",
                blad="❌ Konto z takim adresem e‑mail lub numerem telefonu już istnieje"
            ), 400

        except psycopg2.Error as e:
            conn.rollback()
            return render_template(
                "register.html",
                blad=f"❌ Błąd bazy danych: {str(e)[:100]}"
            ), 500

        finally:
            cur.close()
            conn.close()

    return render_template("register.html")
