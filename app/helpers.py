import psycopg2
from psycopg2.extras import RealDictCursor
from flask import current_app
import re


# ============================================
# BAZA DANYCH
# ============================================

def get_conn():
    """Tworzy połączenie z bazą danych PostgreSQL"""
    try:
        conn = psycopg2.connect(
            host=current_app.config['DB_HOST'],
            database=current_app.config['DB_NAME'],
            user=current_app.config['DB_USER'],
            password=current_app.config['DB_PASSWORD'],
            port=current_app.config['DB_PORT']
        )
        return conn
    except psycopg2.Error as e:
        print(f"❌ Błąd połączenia z bazą: {e}")
        return None

# ============================================
# REZERWACJA SKRYTKI
# ============================================

def zarezerwuj_skrytke(przesylka_id, paczkomat_id, rozmiar_id):
    """
    Szuka wolnej skrytki o danym rozmiarze w paczkomacie
    i rezerwuje ją dla danej przesyłki (status_skrytki = 'Zarezerwowana'
    + wpis w rezerwacja_skrytki).
    Zwraca True/False.
    """
    conn = get_conn()
    if not conn:
        return False
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        # 1. znajdź wolną skrytkę pasującego rozmiaru
        cur.execute("""
            SELECT s.id
            FROM skrytka s
            JOIN status_skrytki ss ON s.status_id = ss.id
            WHERE s.paczkomat_id = %s
              AND s.rozmiar_id = %s
              AND ss.status = 'Wolna'
            ORDER BY s.numer_skrytki
            LIMIT 1
        """, (paczkomat_id, rozmiar_id))
        skrytka = cur.fetchone()
        if not skrytka:
            conn.close()
            return False

        skrytka_id = skrytka["id"]

        # 2. ustaw status skrytki na "Zarezerwowana"
        cur.execute("""
            UPDATE skrytka
            SET status_id = (SELECT id FROM status_skrytki WHERE status = 'Zarezerwowana')
            WHERE id = %s
        """, (skrytka_id,))

        # 3. wpis do rezerwacja_skrytki
        cur.execute("""
            INSERT INTO rezerwacja_skrytki (przesylka_id, skrytka_id, status, data_utworzenia)
            VALUES (%s, %s, 'Zarezerwowana', CURRENT_TIMESTAMP)
        """, (przesylka_id, skrytka_id))

        conn.commit()
        return True
    finally:
        cur.close()
        conn.close()


# ============================================
# OBLICZENIA
# ============================================

def oblicz_koszt_przesylki(paczkomat_nadania_id, paczkomat_docelowy_id, rozmiar_id, waga):
    """
    Oblicza koszt przesyłki na podstawie:
    - dystansu między paczkomatami (geolokalizacja)
    - rozmiaru przesyłki
    - wagi przesyłki
    
    Wzór: Koszt = (0.5 * Dystans_km) + Cena_rozmiaru + Cena_wagi
    
    Args:
        paczkomat_nadania_id (int): ID paczkomatu nadania
        paczkomat_docelowy_id (int): ID paczkomatu docelowego
        rozmiar_id (int): ID rozmiaru przesyłki (S/M/L)
        waga (float): Waga przesyłki w kg
    
    Returns:
        dict: {'koszt': float, 'dystans': float, ...} lub None
    """
    conn = get_conn()
    if not conn:
        return None
    
    cur = conn.cursor(cursor_factory=RealDictCursor)
    try:
        cur.execute("""
            SELECT 
              ST_DistanceSphere(
                ST_MakePoint(pn.dlugosc_geograficzna, pn.szerokosc_geograficzna),
                ST_MakePoint(cn.dlugosc_geograficzna, cn.szerokosc_geograficzna)
              ) / 1000.0 AS last_mile_start,
              mdm.dystans_km AS inter_city,
              ST_DistanceSphere(
                ST_MakePoint(cd.dlugosc_geograficzna, cd.szerokosc_geograficzna),
                ST_MakePoint(pd.dlugosc_geograficzna, pd.szerokosc_geograficzna)
              ) / 1000.0 AS last_mile_end,
              r.rozmiar
            FROM paczkomat pn
            JOIN paczkomat pd ON pd.id = %s
            JOIN centrum_logistyczne cn ON pn.centrum_id = cn.id
            JOIN centrum_logistyczne cd ON pd.centrum_id = cd.id
            JOIN macierz_odleglosci_miast mdm 
              ON cn.miasto_id = mdm.miasto_z_id 
              AND cd.miasto_id = mdm.miasto_do_id
            JOIN rozmiar_przesylki r ON r.id = %s
            WHERE pn.id = %s
        """, (paczkomat_docelowy_id, rozmiar_id, paczkomat_nadania_id))
        
        row = cur.fetchone()
        cur.close()
        conn.close()
        
        if not row:
            return None
        
        last_mile_start = float(row['last_mile_start']) if row['last_mile_start'] else 0
        inter_city = float(row['inter_city']) if row['inter_city'] else 0
        last_mile_end = float(row['last_mile_end']) if row['last_mile_end'] else 0
        rozmiar = row['rozmiar']
        
        dystans_calkowity = last_mile_start + inter_city + last_mile_end
        cena_rozmiaru = {'S': 5.0, 'M': 10.0, 'L': 15.0}.get(rozmiar, 0.0)
        cena_wagi = 5.0 if waga > 10 else 0.0
        koszt = (0.05 * dystans_calkowity) + cena_rozmiaru + cena_wagi
        
        return {
            'koszt': round(koszt, 2),
            'dystans': round(dystans_calkowity, 2),
            'cena_rozmiaru': cena_rozmiaru,
            'cena_wagi': cena_wagi
        }
    except psycopg2.Error as e:
        print(f"❌ Błąd zapytania: {e}")
        return None


# ============================================
# WALIDACJA DANYCH
# ============================================

def validate_email(email):
    """
    Waliduje format email.
    
    Returns:
        tuple: (True, "") lub (False, "błąd")
    """
    pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
    if not re.match(pattern, email):
        return False, "Nieprawidłowy format email"
    return True, ""


def validate_phone(phone):
    """
    Waliduje numer telefonu.
    Dozwolone formaty:
      - +48XXXXXXXXX (np. +48500111222)
      - 0XXXXXXXXX   (np. 0500111222)
      - XXXXXXXXX    (9 cyfr, np. 500111222)

    Returns:
        tuple: (True, "") lub (False, "błąd")
    """
    pattern = r'^(\+48\d{9}|0\d{9}|\d{9})$'
    if not re.match(pattern, phone):
        return False, "Nieprawidłowy numer telefonu (użyj +48XXXXXXXXX, 0XXXXXXXXX lub 9 cyfr)"
    return True, ""


def validate_paczkomat_code(code):
    """
    Waliduje kod paczkomatu (XXXdddd - 3 litery + 4 cyfry).
    
    Returns:
        tuple: (True, "") lub (False, "błąd")
    """
    pattern = r'^[A-Z]{3}\d{4}$'
    if not re.match(pattern, code):
        return False, "Kod paczkomatu: 3 wielkie litery + 4 cyfry (np. ABC1234)"
    return True, ""


def validate_wymiary(dlugosc, szerokosc, wysokosc):
    """
    Waliduje wymiary (wszystkie > 0).
    
    Returns:
        tuple: (True, "") lub (False, "błąd")
    """
    try:
        dl, sz, wy = float(dlugosc), float(szerokosc), float(wysokosc)
        if not all(x > 0 for x in [dl, sz, wy]):
            return False, "Wymiary muszą być większe od 0"
        return True, ""
    except ValueError:
        return False, "Wymiary muszą być liczbami"


def validate_nazwa_miasta(nazwa):
    """Waliduje nazwę miasta (nie pusta, min 2 znaki)"""
    if not nazwa or len(nazwa.strip()) < 2:
        return False, "Nazwa miasta musi mieć co najmniej 2 znaki"
    return True, ""


# ============================================
# LOGI (TODO: w przyszłości)
# ============================================

def log_akcja(typ_akcji, opis, status_kod='SUKCES'):
    """
    TODO: Zaloguj akcję użytkownika do tabeli audit_log.
    
    Args:
        typ_akcji (str): Typ akcji (np. REJESTRACJA, LOGIN, EDYCJA_UŻYTKOWNIKA)
        opis (str): Opis akcji
        status_kod (str): Kod statusu (SUKCES, BŁĄD)
    """
    pass
