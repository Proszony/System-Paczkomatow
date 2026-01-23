-- 1. MIASTA (5)
INSERT INTO MIASTO (Nazwa, Kod, Liczba_mieszkancow, Szerokosc_geograficzna, Dlugosc_geograficzna)
VALUES 
  ('Wrocław',   'WRO', 640000, 51.1079, 17.0385),
  ('Poznań',    'POZ', 530000, 52.4082, 16.9454),
  ('Kraków',    'KRK', 780000, 50.0647, 19.9450),
  ('Warszawa',  'WAR', 1863000, 52.2297, 21.0122),
  ('Gdańsk',    'GDA', 470000, 54.3520, 18.6466);

-- 2. CENTRA LOGISTYCZNE (1 na miasto)
INSERT INTO CENTRUM_LOGISTYCZNE (Miasto_ID, Nazwa, Adres, Szerokosc_geograficzna, Dlugosc_geograficzna, Status_ID, Pojemnosc)
VALUES 
  ((SELECT ID FROM MIASTO WHERE Kod='WRO'), 'Centrum Wrocław',  'ul. Logistyczna 1, Wrocław',  51.1079, 17.0385, (SELECT ID FROM STATUS_CENTRUM WHERE Status='Aktywne'), 5000),
  ((SELECT ID FROM MIASTO WHERE Kod='POZ'), 'Centrum Poznań',   'ul. Magazynowa 2, Poznań',   52.4082, 16.9454, (SELECT ID FROM STATUS_CENTRUM WHERE Status='Aktywne'), 4000),
  ((SELECT ID FROM MIASTO WHERE Kod='KRK'), 'Centrum Kraków',   'ul. Dystrybucji 3, Kraków',  50.0647, 19.9450, (SELECT ID FROM STATUS_CENTRUM WHERE Status='Aktywne'), 4500),
  ((SELECT ID FROM MIASTO WHERE Kod='WAR'), 'Centrum Warszawa', 'ul. Transportowa 4, Warszawa',52.2297,21.0122,(SELECT ID FROM STATUS_CENTRUM WHERE Status='Aktywne'), 6000),
  ((SELECT ID FROM MIASTO WHERE Kod='GDA'), 'Centrum Gdańsk',   'ul. Portowa 5, Gdańsk',      54.3520, 18.6466, (SELECT ID FROM STATUS_CENTRUM WHERE Status='Aktywne'), 3500);

-- 3. PACZKOMATY

-- Wrocław (10)
INSERT INTO PACZKOMAT (Kod, Centrum_ID, Adres, Szerokosc_geograficzna, Dlugosc_geograficzna,
                       Liczba_skrytek_S, Liczba_skrytek_M, Liczba_skrytek_L, Status_ID)
VALUES
  ('WRO0001', (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Wrocław'),
   'ul. Główna 10, Wrocław', 51.1150, 17.0500, 40, 15, 5, (SELECT ID FROM STATUS_PACZKOMATU WHERE Status='Sprawny')),
  ('WRO0002', (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Wrocław'),
   'ul. Centralna 25, Wrocław', 51.1200, 17.0300, 35, 15, 5, (SELECT ID FROM STATUS_PACZKOMATU WHERE Status='Sprawny')),
  ('WRO0003', (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Wrocław'),
   'ul. Słoneczna 5, Wrocław', 51.1300, 17.0600, 30, 15, 5, (SELECT ID FROM STATUS_PACZKOMATU WHERE Status='Sprawny')),
  ('WRO0004', (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Wrocław'),
   'ul. Polna 7, Wrocław', 51.0900, 17.0200, 25, 10, 5, (SELECT ID FROM STATUS_PACZKOMATU WHERE Status='Sprawny')),
  ('WRO0005', (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Wrocław'),
   'ul. Leśna 12, Wrocław', 51.0950, 17.0700, 30, 15, 5, (SELECT ID FROM STATUS_PACZKOMATU WHERE Status='Sprawny')),
  ('WRO0006', (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Wrocław'),
   'ul. Kwiatowa 20, Wrocław', 51.1250, 17.0800, 40, 15, 5, (SELECT ID FROM STATUS_PACZKOMATU WHERE Status='Sprawny')),
  ('WRO0007', (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Wrocław'),
   'ul. Parkowa 2, Wrocław', 51.1350, 17.0100, 30, 20, 10, (SELECT ID FROM STATUS_PACZKOMATU WHERE Status='Sprawny')),
  ('WRO0008', (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Wrocław'),
   'ul. Mostowa 3, Wrocław', 51.1400, 17.0400, 35, 15, 10, (SELECT ID FROM STATUS_PACZKOMATU WHERE Status='Sprawny')),
  ('WRO0009', (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Wrocław'),
   'ul. Dworcowa 8, Wrocław', 51.1100, 17.0800, 45, 10, 5, (SELECT ID FROM STATUS_PACZKOMATU WHERE Status='Sprawny')),
  ('WRO0010',(SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Wrocław'),
   'ul. Ogrodowa 15, Wrocław', 51.1000, 17.0900, 50, 8, 2, (SELECT ID FROM STATUS_PACZKOMATU WHERE Status='Sprawny'));

-- Warszawa (10)
INSERT INTO PACZKOMAT (Kod, Centrum_ID, Adres, Szerokosc_geograficzna, Dlugosc_geograficzna,
                       Liczba_skrytek_S, Liczba_skrytek_M, Liczba_skrytek_L, Status_ID)
VALUES
  ('WAR0001', (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Warszawa'),
   'ul. Marszałkowska 100, Warszawa', 52.2350, 21.0200, 40, 15, 5, (SELECT ID FROM STATUS_PACZKOMATU WHERE Status='Sprawny')),
  ('WAR0002', (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Warszawa'),
   'ul. Puławska 150, Warszawa', 52.2100, 21.0200, 35, 15, 5, (SELECT ID FROM STATUS_PACZKOMATU WHERE Status='Sprawny')),
  ('WAR0003', (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Warszawa'),
   'ul. Świętokrzyska 10, Warszawa', 52.2400, 21.0000, 30, 15, 5, (SELECT ID FROM STATUS_PACZKOMATU WHERE Status='Sprawny')),
  ('WAR0004', (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Warszawa'),
   'ul. Jana Pawła II 20, Warszawa', 52.2500, 21.0300, 25, 10, 5, (SELECT ID FROM STATUS_PACZKOMATU WHERE Status='Sprawny')),
  ('WAR0005', (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Warszawa'),
   'ul. Towarowa 5, Warszawa', 52.2300, 21.0400, 30, 15, 5, (SELECT ID FROM STATUS_PACZKOMATU WHERE Status='Sprawny')),
  ('WAR0006', (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Warszawa'),
   'ul. Płocka 7, Warszawa', 52.2200, 21.0000, 40, 15, 5, (SELECT ID FROM STATUS_PACZKOMATU WHERE Status='Sprawny')),
  ('WAR0007', (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Warszawa'),
   'ul. Grochowska 30, Warszawa', 52.2400, 21.0600, 30, 20, 10, (SELECT ID FROM STATUS_PACZKOMATU WHERE Status='Sprawny')),
  ('WAR0008', (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Warszawa'),
   'ul. Modlińska 200, Warszawa', 52.2700, 21.0400, 35, 15, 10, (SELECT ID FROM STATUS_PACZKOMATU WHERE Status='Sprawny')),
  ('WAR0009', (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Warszawa'),
   'ul. Łopuszańska 50, Warszawa', 52.2200, 20.9900, 45, 10, 5, (SELECT ID FROM STATUS_PACZKOMATU WHERE Status='Sprawny')),
  ('WAR0010',(SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Warszawa'),
   'ul. Połczyńska 120, Warszawa', 52.2300, 20.9800, 50, 8, 2, (SELECT ID FROM STATUS_PACZKOMATU WHERE Status='Sprawny'));

-- Poznań (6)
INSERT INTO PACZKOMAT (Kod, Centrum_ID, Adres, Szerokosc_geograficzna, Dlugosc_geograficzna,
                       Liczba_skrytek_S, Liczba_skrytek_M, Liczba_skrytek_L, Status_ID)
VALUES
  ('POZ0001', (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Poznań'),
   'ul. Armii Krajowej 50, Poznań', 52.4150, 16.9600, 30, 15, 5, (SELECT ID FROM STATUS_PACZKOMATU WHERE Status='Sprawny')),
  ('POZ0002', (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Poznań'),
   'ul. Długa 10, Poznań', 52.4200, 16.9300, 25, 15, 5, (SELECT ID FROM STATUS_PACZKOMATU WHERE Status='Sprawny')),
  ('POZ0003', (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Poznań'),
   'ul. Polna 3, Poznań', 52.4000, 16.9500, 20, 10, 5, (SELECT ID FROM STATUS_PACZKOMATU WHERE Status='Sprawny')),
  ('POZ0004', (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Poznań'),
   'ul. Leśna 7, Poznań', 52.3950, 16.9800, 35, 15, 5, (SELECT ID FROM STATUS_PACZKOMATU WHERE Status='Sprawny')),
  ('POZ0005', (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Poznań'),
   'ul. Dworcowa 1, Poznań', 52.4100, 16.9000, 40, 15, 5, (SELECT ID FROM STATUS_PACZKOMATU WHERE Status='Sprawny')),
  ('POZ0006', (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Poznań'),
   'ul. Ogrodowa 8, Poznań', 52.4050, 16.9900, 45, 10, 5, (SELECT ID FROM STATUS_PACZKOMATU WHERE Status='Sprawny'));

-- Kraków (6)
INSERT INTO PACZKOMAT (Kod, Centrum_ID, Adres, Szerokosc_geograficzna, Dlugosc_geograficzna,
                       Liczba_skrytek_S, Liczba_skrytek_M, Liczba_skrytek_L, Status_ID)
VALUES
  ('KRK0001', (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Kraków'),
   'ul. Floriańska 1, Kraków', 50.0700, 19.9500, 30, 15, 5, (SELECT ID FROM STATUS_PACZKOMATU WHERE Status='Sprawny')),
  ('KRK0002', (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Kraków'),
   'ul. Karmelicka 20, Kraków', 50.0800, 19.9300, 25, 15, 5, (SELECT ID FROM STATUS_PACZKOMATU WHERE Status='Sprawny')),
  ('KRK0003', (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Kraków'),
   'ul. Zakopiańska 50, Kraków', 50.0300, 19.9500, 20, 10, 5, (SELECT ID FROM STATUS_PACZKOMATU WHERE Status='Sprawny')),
  ('KRK0004', (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Kraków'),
   'ul. Mogilska 10, Kraków', 50.0700, 19.9800, 35, 15, 5, (SELECT ID FROM STATUS_PACZKOMATU WHERE Status='Sprawny')),
  ('KRK0005', (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Kraków'),
   'ul. Wielicka 25, Kraków', 50.0200, 19.9700, 40, 15, 5, (SELECT ID FROM STATUS_PACZKOMATU WHERE Status='Sprawny')),
  ('KRK0006', (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Kraków'),
   'ul. Balicka 100, Kraków', 50.0800, 19.8800, 45, 10, 5, (SELECT ID FROM STATUS_PACZKOMATU WHERE Status='Sprawny'));

-- Gdańsk (6)
INSERT INTO PACZKOMAT (Kod, Centrum_ID, Adres, Szerokosc_geograficzna, Dlugosc_geograficzna,
                       Liczba_skrytek_S, Liczba_skrytek_M, Liczba_skrytek_L, Status_ID)
VALUES
  ('GDA0001', (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Gdańsk'),
   'ul. Długa 1, Gdańsk', 54.3550, 18.6500, 30, 15, 5, (SELECT ID FROM STATUS_PACZKOMATU WHERE Status='Sprawny')),
  ('GDA0002', (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Gdańsk'),
   'ul. Grunwaldzka 100, Gdańsk', 54.3800, 18.6100, 25, 15, 5, (SELECT ID FROM STATUS_PACZKOMATU WHERE Status='Sprawny')),
  ('GDA0003', (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Gdańsk'),
   'ul. Złota 10, Gdańsk', 54.3400, 18.6800, 20, 10, 5, (SELECT ID FROM STATUS_PACZKOMATU WHERE Status='Sprawny')),
  ('GDA0004', (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Gdańsk'),
   'ul. Portowa 20, Gdańsk', 54.3600, 18.6900, 35, 15, 5, (SELECT ID FROM STATUS_PACZKOMATU WHERE Status='Sprawny')),
  ('GDA0005', (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Gdańsk'),
   'ul. Spacerowa 5, Gdańsk', 54.3450, 18.6300, 40, 15, 5, (SELECT ID FROM STATUS_PACZKOMATU WHERE Status='Sprawny')),
  ('GDA0006', (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Gdańsk'),
   'ul. Kartuska 200, Gdańsk', 54.3500, 18.5900, 45, 10, 5, (SELECT ID FROM STATUS_PACZKOMATU WHERE Status='Sprawny'));


-- 5. PRACOWNICY I ADMINISTRATORZY

-- Admin (globalny, bez centrum)
INSERT INTO PRACOWNIK (Imie, Nazwisko, Email, Telefon, Adres, Haslo_hash,
                       Data_zatrudnienia, Status_ID, Rola_ID, Centrum_ID)
VALUES ('Adam', 'Admin', 'admin@cbd.com', '111222333', 'ul. Admin 1',
        crypt('admin123', gen_salt('bf')),
        CURRENT_DATE,
        (SELECT ID FROM STATUS_PRACOWNIKA WHERE Status='Aktywny'),
        (SELECT ID FROM ROLA_PRACOWNIKA WHERE Rola='Administrator'),
        NULL);

INSERT INTO ADMINISTRATOR (Pracownik_ID)
VALUES ((SELECT ID FROM PRACOWNIK WHERE Email='admin@cbd.com'));

-- Kierownicy – po jednym na każde centrum
INSERT INTO PRACOWNIK (Imie, Nazwisko, Email, Telefon, Adres, Haslo_hash,
                       Data_zatrudnienia, Status_ID, Rola_ID, Centrum_ID)
VALUES
  ('Krzysztof', 'Wrocławski', 'kierownik_wro@cbd.com', '222333444', 'ul. Wrocław 5',
   crypt('kierownik123', gen_salt('bf')), CURRENT_DATE,
   (SELECT ID FROM STATUS_PRACOWNIKA WHERE Status='Aktywny'),
   (SELECT ID FROM ROLA_PRACOWNIKA WHERE Rola='Kierownik'),
   (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Wrocław')),

  ('Marta', 'Poznańska', 'kierownik_poz@cbd.com', '333444555', 'ul. Poznań 6',
   crypt('kierownik123', gen_salt('bf')), CURRENT_DATE,
   (SELECT ID FROM STATUS_PRACOWNIKA WHERE Status='Aktywny'),
   (SELECT ID FROM ROLA_PRACOWNIKA WHERE Rola='Kierownik'),
   (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Poznań'))

  ('Piotr', 'Krakowski', 'kierownik_krk@cbd.com', '444555666', 'ul. Kraków 7',
   crypt('kierownik123', gen_salt('bf')), CURRENT_DATE,
   (SELECT ID FROM STATUS_PRACOWNIKA WHERE Status='Aktywny'),
   (SELECT ID FROM ROLA_PRACOWNIKA WHERE Rola='Kierownik'),
   (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Kraków')),

  ('Anna', 'Warszawska', 'kierownik_war@cbd.com', '555666777', 'ul. Warszawa 8',
   crypt('kierownik123', gen_salt('bf')), CURRENT_DATE,
   (SELECT ID FROM STATUS_PRACOWNIKA WHERE Status='Aktywny'),
   (SELECT ID FROM ROLA_PRACOWNIKA WHERE Rola='Kierownik'),
   (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Warszawa')),

  ('Tomasz', 'Gdański', 'kierownik_gda@cbd.com', '666777888', 'ul. Gdańsk 9',
   crypt('kierownik123', gen_salt('bf')), CURRENT_DATE,
   (SELECT ID FROM STATUS_PRACOWNIKA WHERE Status='Aktywny'),
   (SELECT ID FROM ROLA_PRACOWNIKA WHERE Rola='Kierownik'),
   (SELECT ID FROM CENTRUM_LOGISTYCZNE WHERE Nazwa='Centrum Gdańsk'));

INSERT INTO KIEROWNIK_CENTRUM (Pracownik_ID, Centrum_ID, Data_przypisania)
SELECT p.ID, c.ID, CURRENT_DATE
FROM PRACOWNIK p
JOIN CENTRUM_LOGISTYCZNE c ON
    (p.Email = 'kierownik_wro@cbd.com'  AND c.Nazwa='Centrum Wrocław') OR
    (p.Email = 'kierownik_poz@cbd.com'  AND c.Nazwa='Centrum Poznań') OR
    (p.Email = 'kierownik_krk@cbd.com'  AND c.Nazwa='Centrum Kraków') OR
    (p.Email = 'kierownik_war@cbd.com'  AND c.Nazwa='Centrum Warszawa') OR
    (p.Email = 'kierownik_gda@cbd.com'  AND c.Nazwa='Centrum Gdańsk');
    
-- 6. KLIENCI (10)
INSERT INTO KLIENT (Imie, Nazwisko, Email, Telefon, Adres, Miasto, Haslo_hash,
                    Status_ID, Typ_Uzytkownika_ID)
VALUES 
  ('Jan',    'Kowalski',  'jan.kowalski@example.com',   '600000001', 'ul. Główna 1',       'Wrocław',
   crypt('klient123', gen_salt('bf')),
   (SELECT ID FROM STATUS_UZYTKOWNIKA WHERE Status='Aktywny'),
   (SELECT ID FROM TYP_UZYTKOWNIKA WHERE Typ='Klient')),
  ('Maria',  'Nowak',     'maria.nowak@example.com',    '600000002', 'ul. Kopernika 15',   'Poznań',
   crypt('klient123', gen_salt('bf')),
   (SELECT ID FROM STATUS_UZYTKOWNIKA WHERE Status='Aktywny'),
   (SELECT ID FROM TYP_UZYTKOWNIKA WHERE Typ='Klient')),
  ('Piotr',  'Wiśniewski','piotr.wisniewski@example.com','600000003','ul. Ogrodowa 2',     'Kraków',
   crypt('klient123', gen_salt('bf')),
   (SELECT ID FROM STATUS_UZYTKOWNIKA WHERE Status='Aktywny'),
   (SELECT ID FROM TYP_UZYTKOWNIKA WHERE Typ='Klient')),
  ('Anna',   'Zielińska', 'anna.zielinska@example.com', '600000004', 'ul. Leśna 3',        'Warszawa',
   crypt('klient123', gen_salt('bf')),
   (SELECT ID FROM STATUS_UZYTKOWNIKA WHERE Status='Aktywny'),
   (SELECT ID FROM TYP_UZYTKOWNIKA WHERE Typ='Klient')),
  ('Tomasz', 'Wójcik',    'tomasz.wojcik@example.com',  '600000005', 'ul. Spacerowa 4',    'Gdańsk',
   crypt('klient123', gen_salt('bf')),
   (SELECT ID FROM STATUS_UZYTKOWNIKA WHERE Status='Aktywny'),
   (SELECT ID FROM TYP_UZYTKOWNIKA WHERE Typ='Klient')),
  ('Ewa',    'Kamińska',  'ewa.kaminska@example.com',   '600000006', 'ul. Kwiatowa 6',     'Wrocław',
   crypt('klient123', gen_salt('bf')),
   (SELECT ID FROM STATUS_UZYTKOWNIKA WHERE Status='Aktywny'),
   (SELECT ID FROM TYP_UZYTKOWNIKA WHERE Typ='Klient')),
  ('Paweł',  'Lewandowski','pawel.lewandowski@example.com','600000007','ul. Krótka 7',    'Poznań',
   crypt('klient123', gen_salt('bf')),
   (SELECT ID FROM STATUS_UZYTKOWNIKA WHERE Status='Aktywny'),
   (SELECT ID FROM TYP_UZYTKOWNIKA WHERE Typ='Klient')),
  ('Katarzyna','Dąbrowska','katarzyna.dabrowska@example.com','600000008','ul. Zielona 8', 'Kraków',
   crypt('klient123', gen_salt('bf')),
   (SELECT ID FROM STATUS_UZYTKOWNIKA WHERE Status='Aktywny'),
   (SELECT ID FROM TYP_UZYTKOWNIKA WHERE Typ='Klient')),
  ('Michał', 'Szymański', 'michal.szymanski@example.com','600000009','ul. Słoneczna 9',   'Warszawa',
   crypt('klient123', gen_salt('bf')),
   (SELECT ID FROM STATUS_UZYTKOWNIKA WHERE Status='Aktywny'),
   (SELECT ID FROM TYP_UZYTKOWNIKA WHERE Typ='Klient')),
  ('Joanna', 'Woźniak',   'joanna.wozniak@example.com', '600000010', 'ul. Polna 10',       'Gdańsk',
   crypt('klient123', gen_salt('bf')),
   (SELECT ID FROM STATUS_UZYTKOWNIKA WHERE Status='Aktywny'),
   (SELECT ID FROM TYP_UZYTKOWNIKA WHERE Typ='Klient'));
    
  
-- 7. SKRYTKI DLA KAŻDEGO PACZKOMATU
-- Wymaga: ROZMIAR_SKRYTKI ('S','M','L'), STATUS_SKRYTKI ('Wolna')

WITH
sizes AS (
    SELECT
        id,
        liczba_skrytek_s,
        liczba_skrytek_m,
        liczba_skrytek_l
    FROM paczkomat
),
s_slots AS (
    -- Skrytki S: 1 .. liczba_skrytek_s
    SELECT
        p.id AS paczkomat_id,
        gs AS numer_skrytki,
        (SELECT id FROM rozmiar_skrytki WHERE rozmiar = 'S') AS rozmiar_id
    FROM sizes p
    JOIN LATERAL generate_series(1, COALESCE(p.liczba_skrytek_s, 0)) AS gs ON TRUE
),
m_slots AS (
    -- Skrytki M: kolejne numery po S
    SELECT
        p.id AS paczkomat_id,
        COALESCE(p.liczba_skrytek_s, 0) + gm AS numer_skrytki,
        (SELECT id FROM rozmiar_skrytki WHERE rozmiar = 'M') AS rozmiar_id
    FROM sizes p
    JOIN LATERAL generate_series(1, COALESCE(p.liczba_skrytek_m, 0)) AS gm ON TRUE
),
l_slots AS (
    -- Skrytki L: kolejne numery po S i M
    SELECT
        p.id AS paczkomat_id,
        COALESCE(p.liczba_skrytek_s, 0) +
        COALESCE(p.liczba_skrytek_m, 0) + gl AS numer_skrytki,
        (SELECT id FROM rozmiar_skrytki WHERE rozmiar = 'L') AS rozmiar_id
    FROM sizes p
    JOIN LATERAL generate_series(1, COALESCE(p.liczba_skrytek_l, 0)) AS gl ON TRUE
),
all_slots AS (
    SELECT * FROM s_slots
    UNION ALL
    SELECT * FROM m_slots
    UNION ALL
    SELECT * FROM l_slots
)
INSERT INTO skrytka (paczkomat_id, numer_skrytki, rozmiar_id, status_id)
SELECT
    a.paczkomat_id,
    a.numer_skrytki,
    a.rozmiar_id,
    (SELECT id FROM status_skrytki WHERE status = 'Wolna') AS status_id
FROM all_slots a
ORDER BY a.paczkomat_id, a.numer_skrytki;


-- 8. MACIERZ ODLEGLOSCI MIAST – liczone z WGS84

INSERT INTO MACIERZ_ODLEGLOSCI_MIAST (
    Miasto_z_ID,
    Miasto_do_ID,
    Dystans_km,
    Flaga_sasiedztwa
)
SELECT
    m1.id  AS Miasto_z_ID,
    m2.id  AS Miasto_do_ID,
    ROUND(
        (
            ST_Distance(
                ST_SetSRID(ST_MakePoint(m1.dlugosc_geograficzna, m1.szerokosc_geograficzna), 4326)::geography,
                ST_SetSRID(ST_MakePoint(m2.dlugosc_geograficzna, m2.szerokosc_geograficzna), 4326)::geography
            ) / 1000.0
        )::numeric
        , 1
    ) AS Dystans_km,
    CASE
        WHEN m1.id <> m2.id
             AND ST_Distance(
                   ST_SetSRID(ST_MakePoint(m1.dlugosc_geograficzna, m1.szerokosc_geograficzna), 4326)::geography,
                   ST_SetSRID(ST_MakePoint(m2.dlugosc_geograficzna, m2.szerokosc_geograficzna), 4326)::geography
                 ) / 1000.0 <= 350
        THEN TRUE
        ELSE FALSE
    END AS Flaga_sasiedztwa
FROM MIASTO m1
CROSS JOIN MIASTO m2;

