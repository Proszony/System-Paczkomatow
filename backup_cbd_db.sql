--
-- PostgreSQL database dump
--

\restrict 11lFUrg6mY5vct3JyZYePeLSjqAnZVcaKW0GrfA8wQDCoTBOKDAPleMuPFooGte

-- Dumped from database version 18.1
-- Dumped by pg_dump version 18.1

SET statement_timeout = 0;
SET lock_timeout = 0;
SET idle_in_transaction_session_timeout = 0;
SET transaction_timeout = 0;
SET client_encoding = 'UTF8';
SET standard_conforming_strings = on;
SELECT pg_catalog.set_config('search_path', '', false);
SET check_function_bodies = false;
SET xmloption = content;
SET client_min_messages = warning;
SET row_security = off;

--
-- Name: pgcrypto; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS pgcrypto WITH SCHEMA public;


--
-- Name: EXTENSION pgcrypto; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION pgcrypto IS 'cryptographic functions';


--
-- Name: postgis; Type: EXTENSION; Schema: -; Owner: -
--

CREATE EXTENSION IF NOT EXISTS postgis WITH SCHEMA public;


--
-- Name: EXTENSION postgis; Type: COMMENT; Schema: -; Owner: 
--

COMMENT ON EXTENSION postgis IS 'PostGIS geometry and geography spatial types and functions';


SET default_tablespace = '';

SET default_table_access_method = heap;

--
-- Name: administrator; Type: TABLE; Schema: public; Owner: cbd_user
--

CREATE TABLE public.administrator (
    id integer NOT NULL,
    pracownik_id integer NOT NULL,
    data_nadania_uprawnien timestamp without time zone DEFAULT CURRENT_TIMESTAMP
);


ALTER TABLE public.administrator OWNER TO cbd_user;

--
-- Name: administrator_id_seq; Type: SEQUENCE; Schema: public; Owner: cbd_user
--

CREATE SEQUENCE public.administrator_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.administrator_id_seq OWNER TO cbd_user;

--
-- Name: administrator_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cbd_user
--

ALTER SEQUENCE public.administrator_id_seq OWNED BY public.administrator.id;


--
-- Name: centrum_logistyczne; Type: TABLE; Schema: public; Owner: cbd_user
--

CREATE TABLE public.centrum_logistyczne (
    id integer NOT NULL,
    miasto_id integer NOT NULL,
    nazwa character varying(200) NOT NULL,
    adres character varying(255) NOT NULL,
    szerokosc_geograficzna numeric(10,8) NOT NULL,
    dlugosc_geograficzna numeric(11,8) NOT NULL,
    data_utworzenia date,
    status_id integer NOT NULL,
    pojemnosc integer NOT NULL
);


ALTER TABLE public.centrum_logistyczne OWNER TO cbd_user;

--
-- Name: centrum_logistyczne_id_seq; Type: SEQUENCE; Schema: public; Owner: cbd_user
--

CREATE SEQUENCE public.centrum_logistyczne_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.centrum_logistyczne_id_seq OWNER TO cbd_user;

--
-- Name: centrum_logistyczne_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cbd_user
--

ALTER SEQUENCE public.centrum_logistyczne_id_seq OWNED BY public.centrum_logistyczne.id;


--
-- Name: historia_statusu; Type: TABLE; Schema: public; Owner: cbd_user
--

CREATE TABLE public.historia_statusu (
    id integer NOT NULL,
    przesylka_id integer NOT NULL,
    status_z_id integer,
    status_na_id integer NOT NULL,
    data_zmiany timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    zmienil character varying(100),
    uwagi character varying(255)
);


ALTER TABLE public.historia_statusu OWNER TO cbd_user;

--
-- Name: historia_statusu_id_seq; Type: SEQUENCE; Schema: public; Owner: cbd_user
--

CREATE SEQUENCE public.historia_statusu_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.historia_statusu_id_seq OWNER TO cbd_user;

--
-- Name: historia_statusu_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cbd_user
--

ALTER SEQUENCE public.historia_statusu_id_seq OWNED BY public.historia_statusu.id;


--
-- Name: kierownik_centrum; Type: TABLE; Schema: public; Owner: cbd_user
--

CREATE TABLE public.kierownik_centrum (
    id integer NOT NULL,
    pracownik_id integer NOT NULL,
    centrum_id integer NOT NULL,
    data_przypisania date NOT NULL
);


ALTER TABLE public.kierownik_centrum OWNER TO cbd_user;

--
-- Name: kierownik_centrum_id_seq; Type: SEQUENCE; Schema: public; Owner: cbd_user
--

CREATE SEQUENCE public.kierownik_centrum_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.kierownik_centrum_id_seq OWNER TO cbd_user;

--
-- Name: kierownik_centrum_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cbd_user
--

ALTER SEQUENCE public.kierownik_centrum_id_seq OWNED BY public.kierownik_centrum.id;


--
-- Name: klient; Type: TABLE; Schema: public; Owner: cbd_user
--

CREATE TABLE public.klient (
    id integer NOT NULL,
    imie character varying(50) NOT NULL,
    nazwisko character varying(50) NOT NULL,
    email character varying(100) NOT NULL,
    telefon character varying(15) NOT NULL,
    adres character varying(255),
    miasto character varying(100),
    haslo_hash character varying(255) NOT NULL,
    data_rejestracji timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    status_id integer NOT NULL,
    typ_uzytkownika_id integer NOT NULL
);


ALTER TABLE public.klient OWNER TO cbd_user;

--
-- Name: klient_id_seq; Type: SEQUENCE; Schema: public; Owner: cbd_user
--

CREATE SEQUENCE public.klient_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.klient_id_seq OWNER TO cbd_user;

--
-- Name: klient_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cbd_user
--

ALTER SEQUENCE public.klient_id_seq OWNED BY public.klient.id;


--
-- Name: logi_systemowe; Type: TABLE; Schema: public; Owner: cbd_user
--

CREATE TABLE public.logi_systemowe (
    id integer NOT NULL,
    pracownik_id integer,
    klient_id integer,
    typ_akcji character varying(50) NOT NULL,
    opis_akcji text NOT NULL,
    data_akcji timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    ip_adres character varying(45),
    status_id integer NOT NULL
);


ALTER TABLE public.logi_systemowe OWNER TO cbd_user;

--
-- Name: logi_systemowe_id_seq; Type: SEQUENCE; Schema: public; Owner: cbd_user
--

CREATE SEQUENCE public.logi_systemowe_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.logi_systemowe_id_seq OWNER TO cbd_user;

--
-- Name: logi_systemowe_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cbd_user
--

ALTER SEQUENCE public.logi_systemowe_id_seq OWNED BY public.logi_systemowe.id;


--
-- Name: macierz_odleglosci_miast; Type: TABLE; Schema: public; Owner: cbd_user
--

CREATE TABLE public.macierz_odleglosci_miast (
    id integer NOT NULL,
    miasto_z_id integer NOT NULL,
    miasto_do_id integer NOT NULL,
    dystans_km numeric(8,2) NOT NULL,
    flaga_sasiedztwa boolean DEFAULT false,
    data_aktualizacji timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    uwagi character varying(255)
);


ALTER TABLE public.macierz_odleglosci_miast OWNER TO cbd_user;

--
-- Name: macierz_odleglosci_miast_id_seq; Type: SEQUENCE; Schema: public; Owner: cbd_user
--

CREATE SEQUENCE public.macierz_odleglosci_miast_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.macierz_odleglosci_miast_id_seq OWNER TO cbd_user;

--
-- Name: macierz_odleglosci_miast_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cbd_user
--

ALTER SEQUENCE public.macierz_odleglosci_miast_id_seq OWNED BY public.macierz_odleglosci_miast.id;


--
-- Name: miasto; Type: TABLE; Schema: public; Owner: cbd_user
--

CREATE TABLE public.miasto (
    id integer NOT NULL,
    nazwa character varying(100) NOT NULL,
    kod character varying(3) NOT NULL,
    liczba_mieszkancow integer,
    szerokosc_geograficzna numeric(10,8) NOT NULL,
    dlugosc_geograficzna numeric(11,8) NOT NULL
);


ALTER TABLE public.miasto OWNER TO cbd_user;

--
-- Name: miasto_id_seq; Type: SEQUENCE; Schema: public; Owner: cbd_user
--

CREATE SEQUENCE public.miasto_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.miasto_id_seq OWNER TO cbd_user;

--
-- Name: miasto_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cbd_user
--

ALTER SEQUENCE public.miasto_id_seq OWNED BY public.miasto.id;


--
-- Name: paczkomat; Type: TABLE; Schema: public; Owner: cbd_user
--

CREATE TABLE public.paczkomat (
    id integer NOT NULL,
    kod character varying(7) NOT NULL,
    centrum_id integer NOT NULL,
    adres character varying(255) NOT NULL,
    szerokosc_geograficzna numeric(10,8) NOT NULL,
    dlugosc_geograficzna numeric(11,8) NOT NULL,
    liczba_skrytek_s integer,
    liczba_skrytek_m integer,
    liczba_skrytek_l integer,
    status_id integer NOT NULL,
    data_ostatniego_serwisu date
);


ALTER TABLE public.paczkomat OWNER TO cbd_user;

--
-- Name: paczkomat_id_seq; Type: SEQUENCE; Schema: public; Owner: cbd_user
--

CREATE SEQUENCE public.paczkomat_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.paczkomat_id_seq OWNER TO cbd_user;

--
-- Name: paczkomat_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cbd_user
--

ALTER SEQUENCE public.paczkomat_id_seq OWNED BY public.paczkomat.id;


--
-- Name: pracownik; Type: TABLE; Schema: public; Owner: cbd_user
--

CREATE TABLE public.pracownik (
    id integer NOT NULL,
    imie character varying(50) NOT NULL,
    nazwisko character varying(50) NOT NULL,
    email character varying(100) NOT NULL,
    telefon character varying(15) NOT NULL,
    adres character varying(255),
    haslo_hash character varying(255) NOT NULL,
    data_zatrudnienia date NOT NULL,
    data_zwolnienia date,
    status_id integer NOT NULL,
    rola_id integer NOT NULL,
    centrum_id integer
);


ALTER TABLE public.pracownik OWNER TO cbd_user;

--
-- Name: pracownik_id_seq; Type: SEQUENCE; Schema: public; Owner: cbd_user
--

CREATE SEQUENCE public.pracownik_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.pracownik_id_seq OWNER TO cbd_user;

--
-- Name: pracownik_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cbd_user
--

ALTER SEQUENCE public.pracownik_id_seq OWNED BY public.pracownik.id;


--
-- Name: przesylka; Type: TABLE; Schema: public; Owner: cbd_user
--

CREATE TABLE public.przesylka (
    id integer NOT NULL,
    numer_przesylki character varying(20) NOT NULL,
    nadawca_id integer NOT NULL,
    odbiorca_id integer NOT NULL,
    paczkomat_nadania_id integer NOT NULL,
    paczkomat_docelowy_id integer NOT NULL,
    rozmiar_id integer NOT NULL,
    wymiary_dlugosc integer NOT NULL,
    wymiary_szerokosc integer NOT NULL,
    wymiary_wysokosc integer NOT NULL,
    waga_nadania numeric(5,2) NOT NULL,
    koszt numeric(8,2) NOT NULL,
    status_id integer NOT NULL,
    data_nadania timestamp without time zone,
    data_planowanej_dostawy timestamp without time zone,
    data_dostarczenia timestamp without time zone,
    uwagi character varying(255),
    flaga_uszkodzona boolean DEFAULT false
);


ALTER TABLE public.przesylka OWNER TO cbd_user;

--
-- Name: przesylka_id_seq; Type: SEQUENCE; Schema: public; Owner: cbd_user
--

CREATE SEQUENCE public.przesylka_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.przesylka_id_seq OWNER TO cbd_user;

--
-- Name: przesylka_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cbd_user
--

ALTER SEQUENCE public.przesylka_id_seq OWNED BY public.przesylka.id;


--
-- Name: rezerwacja_skrytki; Type: TABLE; Schema: public; Owner: cbd_user
--

CREATE TABLE public.rezerwacja_skrytki (
    przesylka_id integer NOT NULL,
    skrytka_id integer NOT NULL,
    data_rezerwacji timestamp without time zone DEFAULT CURRENT_TIMESTAMP NOT NULL,
    data_wygasniecia timestamp without time zone NOT NULL,
    status_id integer NOT NULL
);


ALTER TABLE public.rezerwacja_skrytki OWNER TO cbd_user;

--
-- Name: rola_pracownika; Type: TABLE; Schema: public; Owner: cbd_user
--

CREATE TABLE public.rola_pracownika (
    id integer NOT NULL,
    rola character varying(50) NOT NULL
);


ALTER TABLE public.rola_pracownika OWNER TO cbd_user;

--
-- Name: rola_pracownika_id_seq; Type: SEQUENCE; Schema: public; Owner: cbd_user
--

CREATE SEQUENCE public.rola_pracownika_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.rola_pracownika_id_seq OWNER TO cbd_user;

--
-- Name: rola_pracownika_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cbd_user
--

ALTER SEQUENCE public.rola_pracownika_id_seq OWNED BY public.rola_pracownika.id;


--
-- Name: rozmiar_przesylki; Type: TABLE; Schema: public; Owner: cbd_user
--

CREATE TABLE public.rozmiar_przesylki (
    id integer NOT NULL,
    rozmiar character varying(10) NOT NULL
);


ALTER TABLE public.rozmiar_przesylki OWNER TO cbd_user;

--
-- Name: rozmiar_przesylki_id_seq; Type: SEQUENCE; Schema: public; Owner: cbd_user
--

CREATE SEQUENCE public.rozmiar_przesylki_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.rozmiar_przesylki_id_seq OWNER TO cbd_user;

--
-- Name: rozmiar_przesylki_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cbd_user
--

ALTER SEQUENCE public.rozmiar_przesylki_id_seq OWNED BY public.rozmiar_przesylki.id;


--
-- Name: rozmiar_skrytki; Type: TABLE; Schema: public; Owner: cbd_user
--

CREATE TABLE public.rozmiar_skrytki (
    id integer NOT NULL,
    rozmiar character varying(3) NOT NULL
);


ALTER TABLE public.rozmiar_skrytki OWNER TO cbd_user;

--
-- Name: rozmiar_skrytki_id_seq; Type: SEQUENCE; Schema: public; Owner: cbd_user
--

CREATE SEQUENCE public.rozmiar_skrytki_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.rozmiar_skrytki_id_seq OWNER TO cbd_user;

--
-- Name: rozmiar_skrytki_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cbd_user
--

ALTER SEQUENCE public.rozmiar_skrytki_id_seq OWNED BY public.rozmiar_skrytki.id;


--
-- Name: skrytka; Type: TABLE; Schema: public; Owner: cbd_user
--

CREATE TABLE public.skrytka (
    id integer NOT NULL,
    paczkomat_id integer NOT NULL,
    numer_skrytki integer NOT NULL,
    rozmiar_id integer NOT NULL,
    status_id integer NOT NULL,
    data_ostatniej_kontroli timestamp without time zone
);


ALTER TABLE public.skrytka OWNER TO cbd_user;

--
-- Name: skrytka_id_seq; Type: SEQUENCE; Schema: public; Owner: cbd_user
--

CREATE SEQUENCE public.skrytka_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.skrytka_id_seq OWNER TO cbd_user;

--
-- Name: skrytka_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cbd_user
--

ALTER SEQUENCE public.skrytka_id_seq OWNED BY public.skrytka.id;


--
-- Name: status_akcji; Type: TABLE; Schema: public; Owner: cbd_user
--

CREATE TABLE public.status_akcji (
    id integer NOT NULL,
    status character varying(50) NOT NULL
);


ALTER TABLE public.status_akcji OWNER TO cbd_user;

--
-- Name: status_akcji_id_seq; Type: SEQUENCE; Schema: public; Owner: cbd_user
--

CREATE SEQUENCE public.status_akcji_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.status_akcji_id_seq OWNER TO cbd_user;

--
-- Name: status_akcji_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cbd_user
--

ALTER SEQUENCE public.status_akcji_id_seq OWNED BY public.status_akcji.id;


--
-- Name: status_centrum; Type: TABLE; Schema: public; Owner: cbd_user
--

CREATE TABLE public.status_centrum (
    id integer NOT NULL,
    status character varying(50) NOT NULL
);


ALTER TABLE public.status_centrum OWNER TO cbd_user;

--
-- Name: status_centrum_id_seq; Type: SEQUENCE; Schema: public; Owner: cbd_user
--

CREATE SEQUENCE public.status_centrum_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.status_centrum_id_seq OWNER TO cbd_user;

--
-- Name: status_centrum_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cbd_user
--

ALTER SEQUENCE public.status_centrum_id_seq OWNED BY public.status_centrum.id;


--
-- Name: status_paczkomatu; Type: TABLE; Schema: public; Owner: cbd_user
--

CREATE TABLE public.status_paczkomatu (
    id integer NOT NULL,
    status character varying(50) NOT NULL
);


ALTER TABLE public.status_paczkomatu OWNER TO cbd_user;

--
-- Name: status_paczkomatu_id_seq; Type: SEQUENCE; Schema: public; Owner: cbd_user
--

CREATE SEQUENCE public.status_paczkomatu_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.status_paczkomatu_id_seq OWNER TO cbd_user;

--
-- Name: status_paczkomatu_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cbd_user
--

ALTER SEQUENCE public.status_paczkomatu_id_seq OWNED BY public.status_paczkomatu.id;


--
-- Name: status_pracownika; Type: TABLE; Schema: public; Owner: cbd_user
--

CREATE TABLE public.status_pracownika (
    id integer NOT NULL,
    status character varying(50) NOT NULL
);


ALTER TABLE public.status_pracownika OWNER TO cbd_user;

--
-- Name: status_pracownika_id_seq; Type: SEQUENCE; Schema: public; Owner: cbd_user
--

CREATE SEQUENCE public.status_pracownika_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.status_pracownika_id_seq OWNER TO cbd_user;

--
-- Name: status_pracownika_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cbd_user
--

ALTER SEQUENCE public.status_pracownika_id_seq OWNED BY public.status_pracownika.id;


--
-- Name: status_przesylki; Type: TABLE; Schema: public; Owner: cbd_user
--

CREATE TABLE public.status_przesylki (
    id integer NOT NULL,
    status character varying(50) NOT NULL
);


ALTER TABLE public.status_przesylki OWNER TO cbd_user;

--
-- Name: status_przesylki_id_seq; Type: SEQUENCE; Schema: public; Owner: cbd_user
--

CREATE SEQUENCE public.status_przesylki_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.status_przesylki_id_seq OWNER TO cbd_user;

--
-- Name: status_przesylki_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cbd_user
--

ALTER SEQUENCE public.status_przesylki_id_seq OWNED BY public.status_przesylki.id;


--
-- Name: status_rezerwacji; Type: TABLE; Schema: public; Owner: cbd_user
--

CREATE TABLE public.status_rezerwacji (
    id integer NOT NULL,
    status character varying(50) NOT NULL
);


ALTER TABLE public.status_rezerwacji OWNER TO cbd_user;

--
-- Name: status_rezerwacji_id_seq; Type: SEQUENCE; Schema: public; Owner: cbd_user
--

CREATE SEQUENCE public.status_rezerwacji_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.status_rezerwacji_id_seq OWNER TO cbd_user;

--
-- Name: status_rezerwacji_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cbd_user
--

ALTER SEQUENCE public.status_rezerwacji_id_seq OWNED BY public.status_rezerwacji.id;


--
-- Name: status_skrytki; Type: TABLE; Schema: public; Owner: cbd_user
--

CREATE TABLE public.status_skrytki (
    id integer NOT NULL,
    status character varying(50) NOT NULL
);


ALTER TABLE public.status_skrytki OWNER TO cbd_user;

--
-- Name: status_skrytki_id_seq; Type: SEQUENCE; Schema: public; Owner: cbd_user
--

CREATE SEQUENCE public.status_skrytki_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.status_skrytki_id_seq OWNER TO cbd_user;

--
-- Name: status_skrytki_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cbd_user
--

ALTER SEQUENCE public.status_skrytki_id_seq OWNED BY public.status_skrytki.id;


--
-- Name: status_trasy; Type: TABLE; Schema: public; Owner: cbd_user
--

CREATE TABLE public.status_trasy (
    id integer NOT NULL,
    status character varying(50) NOT NULL
);


ALTER TABLE public.status_trasy OWNER TO cbd_user;

--
-- Name: status_trasy_id_seq; Type: SEQUENCE; Schema: public; Owner: cbd_user
--

CREATE SEQUENCE public.status_trasy_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.status_trasy_id_seq OWNER TO cbd_user;

--
-- Name: status_trasy_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cbd_user
--

ALTER SEQUENCE public.status_trasy_id_seq OWNED BY public.status_trasy.id;


--
-- Name: status_uzytkownika; Type: TABLE; Schema: public; Owner: cbd_user
--

CREATE TABLE public.status_uzytkownika (
    id integer NOT NULL,
    status character varying(50) NOT NULL
);


ALTER TABLE public.status_uzytkownika OWNER TO cbd_user;

--
-- Name: status_uzytkownika_id_seq; Type: SEQUENCE; Schema: public; Owner: cbd_user
--

CREATE SEQUENCE public.status_uzytkownika_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.status_uzytkownika_id_seq OWNER TO cbd_user;

--
-- Name: status_uzytkownika_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cbd_user
--

ALTER SEQUENCE public.status_uzytkownika_id_seq OWNED BY public.status_uzytkownika.id;


--
-- Name: trasa_dostawy; Type: TABLE; Schema: public; Owner: cbd_user
--

CREATE TABLE public.trasa_dostawy (
    id integer NOT NULL,
    centrum_id integer NOT NULL,
    paczkomat_id integer NOT NULL,
    przesylka_id integer NOT NULL,
    data_utworzenia timestamp without time zone DEFAULT CURRENT_TIMESTAMP,
    status_id integer NOT NULL
);


ALTER TABLE public.trasa_dostawy OWNER TO cbd_user;

--
-- Name: trasa_dostawy_id_seq; Type: SEQUENCE; Schema: public; Owner: cbd_user
--

CREATE SEQUENCE public.trasa_dostawy_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.trasa_dostawy_id_seq OWNER TO cbd_user;

--
-- Name: trasa_dostawy_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cbd_user
--

ALTER SEQUENCE public.trasa_dostawy_id_seq OWNED BY public.trasa_dostawy.id;


--
-- Name: typ_uzytkownika; Type: TABLE; Schema: public; Owner: cbd_user
--

CREATE TABLE public.typ_uzytkownika (
    id integer NOT NULL,
    typ character varying(50) NOT NULL
);


ALTER TABLE public.typ_uzytkownika OWNER TO cbd_user;

--
-- Name: typ_uzytkownika_id_seq; Type: SEQUENCE; Schema: public; Owner: cbd_user
--

CREATE SEQUENCE public.typ_uzytkownika_id_seq
    AS integer
    START WITH 1
    INCREMENT BY 1
    NO MINVALUE
    NO MAXVALUE
    CACHE 1;


ALTER SEQUENCE public.typ_uzytkownika_id_seq OWNER TO cbd_user;

--
-- Name: typ_uzytkownika_id_seq; Type: SEQUENCE OWNED BY; Schema: public; Owner: cbd_user
--

ALTER SEQUENCE public.typ_uzytkownika_id_seq OWNED BY public.typ_uzytkownika.id;


--
-- Name: administrator id; Type: DEFAULT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.administrator ALTER COLUMN id SET DEFAULT nextval('public.administrator_id_seq'::regclass);


--
-- Name: centrum_logistyczne id; Type: DEFAULT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.centrum_logistyczne ALTER COLUMN id SET DEFAULT nextval('public.centrum_logistyczne_id_seq'::regclass);


--
-- Name: historia_statusu id; Type: DEFAULT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.historia_statusu ALTER COLUMN id SET DEFAULT nextval('public.historia_statusu_id_seq'::regclass);


--
-- Name: kierownik_centrum id; Type: DEFAULT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.kierownik_centrum ALTER COLUMN id SET DEFAULT nextval('public.kierownik_centrum_id_seq'::regclass);


--
-- Name: klient id; Type: DEFAULT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.klient ALTER COLUMN id SET DEFAULT nextval('public.klient_id_seq'::regclass);


--
-- Name: logi_systemowe id; Type: DEFAULT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.logi_systemowe ALTER COLUMN id SET DEFAULT nextval('public.logi_systemowe_id_seq'::regclass);


--
-- Name: macierz_odleglosci_miast id; Type: DEFAULT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.macierz_odleglosci_miast ALTER COLUMN id SET DEFAULT nextval('public.macierz_odleglosci_miast_id_seq'::regclass);


--
-- Name: miasto id; Type: DEFAULT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.miasto ALTER COLUMN id SET DEFAULT nextval('public.miasto_id_seq'::regclass);


--
-- Name: paczkomat id; Type: DEFAULT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.paczkomat ALTER COLUMN id SET DEFAULT nextval('public.paczkomat_id_seq'::regclass);


--
-- Name: pracownik id; Type: DEFAULT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.pracownik ALTER COLUMN id SET DEFAULT nextval('public.pracownik_id_seq'::regclass);


--
-- Name: przesylka id; Type: DEFAULT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.przesylka ALTER COLUMN id SET DEFAULT nextval('public.przesylka_id_seq'::regclass);


--
-- Name: rola_pracownika id; Type: DEFAULT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.rola_pracownika ALTER COLUMN id SET DEFAULT nextval('public.rola_pracownika_id_seq'::regclass);


--
-- Name: rozmiar_przesylki id; Type: DEFAULT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.rozmiar_przesylki ALTER COLUMN id SET DEFAULT nextval('public.rozmiar_przesylki_id_seq'::regclass);


--
-- Name: rozmiar_skrytki id; Type: DEFAULT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.rozmiar_skrytki ALTER COLUMN id SET DEFAULT nextval('public.rozmiar_skrytki_id_seq'::regclass);


--
-- Name: skrytka id; Type: DEFAULT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.skrytka ALTER COLUMN id SET DEFAULT nextval('public.skrytka_id_seq'::regclass);


--
-- Name: status_akcji id; Type: DEFAULT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.status_akcji ALTER COLUMN id SET DEFAULT nextval('public.status_akcji_id_seq'::regclass);


--
-- Name: status_centrum id; Type: DEFAULT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.status_centrum ALTER COLUMN id SET DEFAULT nextval('public.status_centrum_id_seq'::regclass);


--
-- Name: status_paczkomatu id; Type: DEFAULT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.status_paczkomatu ALTER COLUMN id SET DEFAULT nextval('public.status_paczkomatu_id_seq'::regclass);


--
-- Name: status_pracownika id; Type: DEFAULT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.status_pracownika ALTER COLUMN id SET DEFAULT nextval('public.status_pracownika_id_seq'::regclass);


--
-- Name: status_przesylki id; Type: DEFAULT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.status_przesylki ALTER COLUMN id SET DEFAULT nextval('public.status_przesylki_id_seq'::regclass);


--
-- Name: status_rezerwacji id; Type: DEFAULT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.status_rezerwacji ALTER COLUMN id SET DEFAULT nextval('public.status_rezerwacji_id_seq'::regclass);


--
-- Name: status_skrytki id; Type: DEFAULT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.status_skrytki ALTER COLUMN id SET DEFAULT nextval('public.status_skrytki_id_seq'::regclass);


--
-- Name: status_trasy id; Type: DEFAULT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.status_trasy ALTER COLUMN id SET DEFAULT nextval('public.status_trasy_id_seq'::regclass);


--
-- Name: status_uzytkownika id; Type: DEFAULT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.status_uzytkownika ALTER COLUMN id SET DEFAULT nextval('public.status_uzytkownika_id_seq'::regclass);


--
-- Name: trasa_dostawy id; Type: DEFAULT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.trasa_dostawy ALTER COLUMN id SET DEFAULT nextval('public.trasa_dostawy_id_seq'::regclass);


--
-- Name: typ_uzytkownika id; Type: DEFAULT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.typ_uzytkownika ALTER COLUMN id SET DEFAULT nextval('public.typ_uzytkownika_id_seq'::regclass);


--
-- Data for Name: administrator; Type: TABLE DATA; Schema: public; Owner: cbd_user
--

COPY public.administrator (id, pracownik_id, data_nadania_uprawnien) FROM stdin;
1	1	2026-01-08 21:42:07.287133
\.


--
-- Data for Name: centrum_logistyczne; Type: TABLE DATA; Schema: public; Owner: cbd_user
--

COPY public.centrum_logistyczne (id, miasto_id, nazwa, adres, szerokosc_geograficzna, dlugosc_geograficzna, data_utworzenia, status_id, pojemnosc) FROM stdin;
1	1	Centrum Wrocław	ul. Logistyczna 1, Wrocław	51.10790000	17.03850000	\N	1	5000
2	2	Centrum Poznań	ul. Magazynowa 2, Poznań	52.40820000	16.94540000	\N	1	4000
3	3	Centrum Kraków	ul. Dystrybucji 3, Kraków	50.06470000	19.94500000	\N	1	4500
4	4	Centrum Warszawa	ul. Transportowa 4, Warszawa	52.22970000	21.01220000	\N	1	6000
12	6	Centrum Gdańsk	ul. Sportowa 10, Gdańsk	54.42770400	18.46828600	\N	1	4000
\.


--
-- Data for Name: historia_statusu; Type: TABLE DATA; Schema: public; Owner: cbd_user
--

COPY public.historia_statusu (id, przesylka_id, status_z_id, status_na_id, data_zmiany, zmienil, uwagi) FROM stdin;
1	6	1	2	2026-01-16 20:05:06.386107	Adam Admin	Zmiana statusu przez admina (ID 1)
2	2	1	7	2026-01-17 17:29:15.476314	Adam Admin	Zmiana statusu przez admina (ID 1)
3	9	1	2	2026-01-17 18:43:35.593386	5	Nadanie przesyłki przez klienta
4	5	1	7	2026-01-17 18:47:30.117214	5	Anulowanie przesyłki przez klienta
5	1	\N	6	2026-01-18 16:31:16.386318	1	Odbiór przesyłki przez odbiorcę
6	11	1	2	2026-01-18 19:02:40.860877	5	Nadanie przesyłki przez klienta
7	4	1	2	2026-01-18 19:08:30.029357	8	Nadanie przesyłki przez klienta
8	4	2	3	2026-01-20 12:52:00.058302	2	Przyjęcie przesyłki w centrum
9	11	2	3	2026-01-20 12:56:10.839687	2	Przyjęcie przesyłki w centrum
10	12	1	2	2026-01-20 13:05:51.028671	5	Nadanie przesyłki przez klienta
11	12	2	3	2026-01-20 13:12:52.87365	2	Przyjęcie przesyłki w centrum
12	13	1	2	2026-01-20 14:37:53.617089	5	Nadanie przesyłki przez klienta
13	14	1	2	2026-01-20 14:38:54.130776	5	Nadanie przesyłki przez klienta
14	14	2	3	2026-01-20 14:39:00.188275	2	Przyjęcie przesyłki w centrum
15	20	1	7	2026-01-20 15:55:42.684339	5	Anulowanie przesyłki przez klienta
16	21	1	2	2026-01-20 16:09:41.541981	5	Nadanie przesyłki przez klienta
17	19	1	2	2026-01-20 17:47:54.09742	5	Nadanie przesyłki przez klienta
18	4	3	4	2026-01-21 00:18:14.586192	2	Wysłanie przesyłki z centrum nadania do centrum docelowego (batch)
19	11	3	5	2026-01-21 00:18:14.586192	2	Doręczenie do paczkomatu docelowego (batch)
20	12	3	4	2026-01-21 00:18:14.586192	2	Wysłanie przesyłki z centrum nadania do centrum docelowego (batch)
21	14	3	4	2026-01-21 00:18:14.586192	2	Wysłanie przesyłki z centrum nadania do centrum docelowego (batch)
22	11	\N	6	2026-01-21 00:29:25.732476	8	Odbiór przesyłki przez odbiorcę
23	21	2	3	2026-01-21 00:31:06.374255	2	Przyjęcie przesyłki w centrum (operacja zbiorcza)
24	19	2	3	2026-01-21 00:31:06.374255	2	Przyjęcie przesyłki w centrum (operacja zbiorcza)
25	12	4	3	2026-01-21 02:17:16.731417	3	Przyjęcie przesyłki z trasy w centrum docelowym (batch)
26	14	4	3	2026-01-21 02:17:16.731417	3	Przyjęcie przesyłki z trasy w centrum docelowym (batch)
27	21	3	5	2026-01-21 02:18:13.096541	3	Doręczenie do paczkomatu docelowego (batch, centrum docelowe)
28	21	\N	6	2026-01-21 02:18:21.131881	8	Odbiór przesyłki przez odbiorcę
29	12	3	5	2026-01-21 02:18:30.0382	3	Doręczenie do paczkomatu docelowego (batch, centrum docelowe)
30	14	3	5	2026-01-21 02:47:37.559134	3	Doręczenie do paczkomatu docelowego (batch, centrum docelowe)
31	14	\N	6	2026-01-21 02:48:03.625314	1	Odbiór przesyłki przez odbiorcę
32	19	3	5	2026-01-21 02:56:46.799544	2	Doręczenie do paczkomatu docelowego (batch, centrum docelowe)
33	23	1	2	2026-01-21 08:29:13.651146	5	Nadanie przesyłki przez klienta
34	23	2	3	2026-01-21 08:29:30.823091	2	Przyjęcie przesyłki w centrum (operacja zbiorcza)
35	23	3	4	2026-01-21 08:29:34.448546	2	Wysłanie przesyłki z centrum nadania do centrum docelowego (batch)
36	23	4	3	2026-01-21 08:30:45.720069	3	Przyjęcie przesyłki z trasy w centrum docelowym (batch)
37	23	3	5	2026-01-21 08:30:49.711581	3	Doręczenie do paczkomatu docelowego (batch, centrum docelowe)
38	23	\N	6	2026-01-21 08:32:52.085048	9	Odbiór przesyłki przez odbiorcę
39	19	\N	6	2026-01-22 15:58:24.223761	8	Odbiór przesyłki przez odbiorcę
40	19	6	6	2026-01-22 16:08:37.258251	8	Klient zgłosił uszkodzenie przesyłki
41	24	1	2	2026-01-23 02:23:29.652139	5	Nadanie przesyłki przez klienta
42	24	2	3	2026-01-23 02:24:16.783937	2	Przyjęcie przesyłki w centrum (operacja zbiorcza)
43	24	3	4	2026-01-23 02:24:19.499458	2	Wysłanie przesyłki z centrum nadania do centrum docelowego (batch)
44	24	4	3	2026-01-23 02:24:47.610108	3	Przyjęcie przesyłki z trasy w centrum docelowym (batch)
45	24	3	5	2026-01-23 02:24:50.405649	3	Doręczenie do paczkomatu docelowego (batch, centrum docelowe)
46	24	\N	6	2026-01-23 02:26:11.573413	9	Odbiór przesyłki przez odbiorcę
47	25	1	2	2026-01-23 03:32:16.014834	5	Nadanie przesyłki przez klienta
48	25	2	3	2026-01-23 03:33:03.236046	2	Przyjęcie przesyłki w centrum (operacja zbiorcza)
49	25	3	4	2026-01-23 03:33:10.599468	2	Wysłanie przesyłki z centrum nadania do centrum docelowego (batch)
50	25	4	3	2026-01-23 03:33:41.625172	3	Przyjęcie przesyłki z trasy w centrum docelowym (batch)
51	25	3	5	2026-01-23 03:33:46.871932	3	Doręczenie do paczkomatu docelowego (batch, centrum docelowe)
52	25	\N	6	2026-01-23 03:34:31.913835	8	Odbiór przesyłki przez odbiorcę
53	25	6	6	2026-01-23 03:34:51.221361	8	Klient zgłosił uszkodzenie przesyłki
\.


--
-- Data for Name: kierownik_centrum; Type: TABLE DATA; Schema: public; Owner: cbd_user
--

COPY public.kierownik_centrum (id, pracownik_id, centrum_id, data_przypisania) FROM stdin;
1	2	1	2026-01-08
2	3	2	2026-01-08
\.


--
-- Data for Name: klient; Type: TABLE DATA; Schema: public; Owner: cbd_user
--

COPY public.klient (id, imie, nazwisko, email, telefon, adres, miasto, haslo_hash, data_rejestracji, status_id, typ_uzytkownika_id) FROM stdin;
5	Ali	Baba	boom@mail.gov	421841692		\N	$2a$06$hE1qlpARyKVW8DhsV02ZHuOjpOtrkYJu1vSGCLjZ7MP4pE89y6ft2	2026-01-08 23:21:16.124933	1	1
8	Donland	Macdonland	Kaczor@bogaty.pl	694202137		\N	$2a$06$MCKKHhMGvD97yl1rloZn4O0jVvyw5nL7zJ2NN7Vygx/XrkOWBGJ9O	2026-01-09 06:23:09.386812	1	1
2	Maria	Nowak	maria.nowak@email.com	234567890	ul. Kopernika 15	Poznań	$2a$06$tqy19ullYMAIX2nIZbgUaOQSEIGOovhA6A2uyAQ5bPomkgNpssiGy	2026-01-08 21:42:07.295741	1	1
1	Jan	Kowalski	jan.kowalski@email.com	123456789	ul. Główna 1		$2a$06$i56.inePZFA/5mlnz6ikB.Bdk.uRE.pb0qramawUSdxb35k6j.GQm	2026-01-08 21:42:07.295741	1	1
9	Bożydar	Ki	aniol@niebo.pl	567890432	\N	\N	$2a$06$OxOTUBh3MO4ryWzhSonPNOvZBdyMucWWWo.DJHACi82bu9S09ANtq	2026-01-21 02:56:02.405245	1	1
\.


--
-- Data for Name: logi_systemowe; Type: TABLE DATA; Schema: public; Owner: cbd_user
--

COPY public.logi_systemowe (id, pracownik_id, klient_id, typ_akcji, opis_akcji, data_akcji, ip_adres, status_id) FROM stdin;
\.


--
-- Data for Name: macierz_odleglosci_miast; Type: TABLE DATA; Schema: public; Owner: cbd_user
--

COPY public.macierz_odleglosci_miast (id, miasto_z_id, miasto_do_id, dystans_km, flaga_sasiedztwa, data_aktualizacji, uwagi) FROM stdin;
1	1	2	210.00	f	2026-01-08 21:42:07.281231	\N
2	2	1	210.00	f	2026-01-08 21:42:07.281231	\N
3	1	3	340.00	f	2026-01-08 21:42:07.281231	\N
4	3	1	340.00	f	2026-01-08 21:42:07.281231	\N
5	2	3	560.00	f	2026-01-08 21:42:07.281231	\N
6	3	2	560.00	f	2026-01-08 21:42:07.281231	\N
7	1	4	340.00	f	2026-01-08 21:42:07.281231	\N
8	4	1	340.00	f	2026-01-08 21:42:07.281231	\N
9	2	4	310.00	f	2026-01-08 21:42:07.281231	\N
10	4	2	310.00	f	2026-01-08 21:42:07.281231	\N
11	3	4	280.00	f	2026-01-08 21:42:07.281231	\N
12	4	3	280.00	f	2026-01-08 21:42:07.281231	\N
13	1	1	0.00	f	2026-01-08 21:42:07.281231	\N
14	2	2	0.00	f	2026-01-08 21:42:07.281231	\N
15	3	3	0.00	f	2026-01-08 21:42:07.281231	\N
16	4	4	0.00	f	2026-01-08 21:42:07.281231	\N
\.


--
-- Data for Name: miasto; Type: TABLE DATA; Schema: public; Owner: cbd_user
--

COPY public.miasto (id, nazwa, kod, liczba_mieszkancow, szerokosc_geograficzna, dlugosc_geograficzna) FROM stdin;
1	Wrocław	WRO	640000	51.10790000	17.03850000
2	Poznań	POZ	530000	52.40820000	16.94540000
3	Kraków	KRK	780000	50.06470000	19.94500000
4	Warszawa	WAR	1863000	52.22970000	21.01220000
6	Gdańsk	GDA	489160	54.35000000	18.66670000
\.


--
-- Data for Name: paczkomat; Type: TABLE DATA; Schema: public; Owner: cbd_user
--

COPY public.paczkomat (id, kod, centrum_id, adres, szerokosc_geograficzna, dlugosc_geograficzna, liczba_skrytek_s, liczba_skrytek_m, liczba_skrytek_l, status_id, data_ostatniego_serwisu) FROM stdin;
2	WRO0002	1	ul. Centralna 25, Wrocław	51.10700000	17.03800000	10	8	5	1	\N
3	POZ0001	2	ul. Armii Krajowej 50, Poznań	52.40900000	16.94600000	10	8	5	1	\N
4	KRK0001	3	ul. Floriańska 1, Kraków	50.06550000	19.94550000	10	8	5	1	\N
5	WAR0001	4	ul. Marszałkowska 100, Warszawa	52.23100000	21.01300000	15	10	8	1	\N
1	WRO0001	1	ul. Główna 10, Wrocław	51.10850000	17.03900000	10	8	5	1	\N
7	POZ0002	2	ul. Armii Krajowej 50, Poznań	52.40900000	16.94600000	10	8	5	1	\N
\.


--
-- Data for Name: pracownik; Type: TABLE DATA; Schema: public; Owner: cbd_user
--

COPY public.pracownik (id, imie, nazwisko, email, telefon, adres, haslo_hash, data_zatrudnienia, data_zwolnienia, status_id, rola_id, centrum_id) FROM stdin;
1	Adam	Admin	admin@cbd.com	111222333	ul. Admin 1	$2a$06$oAEt0i9vpiXysFfklu0Xe.g/dlmFhSTM5tUuqI4I06A.ShFFZJjqK	2026-01-08	\N	1	2	\N
3	Marta	Kierowcowa	kierownik_poz@cbd.com	333444555	ul. Poznań 6	$2a$06$0/yP36RzfM9GixYwKYY7I.FaZPpwBlCLQ3fI0iuP1DP/EunwpWf3S	2026-01-08	\N	1	3	2
2	Krzysztof	Kierowca	kierownik_wro@cbd.com	222333444	ul. Wrocław 5	$2a$06$ak6bcB1qgBbNIAbhnS7A1uJi/o6R91W2dCDFiuaNXOitedu0yDk9C	2026-01-08	\N	1	3	1
\.


--
-- Data for Name: przesylka; Type: TABLE DATA; Schema: public; Owner: cbd_user
--

COPY public.przesylka (id, numer_przesylki, nadawca_id, odbiorca_id, paczkomat_nadania_id, paczkomat_docelowy_id, rozmiar_id, wymiary_dlugosc, wymiary_szerokosc, wymiary_wysokosc, waga_nadania, koszt, status_id, data_nadania, data_planowanej_dostawy, data_dostarczenia, uwagi, flaga_uszkodzona) FROM stdin;
21	PKG-1768921729	5	8	2	3	2	20	15	10	15.90	120.10	6	2026-01-20 16:09:41.541981	\N	\N	\N	f
12	PKG-1768910740	5	8	2	3	3	20	15	10	68.00	125.10	5	2026-01-20 13:05:51.028671	\N	\N	\N	f
14	PKG-1768916305	5	1	1	7	2	20	15	10	7.00	115.09	6	2026-01-20 14:38:54.130776	\N	\N	\N	f
3	PKG-1767935617	2	1	1	2	3	20	15	10	8.00	15.09	1	2026-01-09 06:13:37.474341	\N	\N	\N	f
22	PKG-1768960974	9	5	3	2	1	20	15	10	999.90	20.51	1	2026-01-21 03:02:54.718436	\N	\N	\N	f
6	PKG-1767971354	5	1	3	3	3	20	15	10	800.70	20.10	2	2026-01-09 16:09:14.585089	\N	\N		f
2	PKG-1767935591	5	2	1	5	2	20	15	10	5.00	180.11	7	2026-01-09 06:13:11.77563	\N	\N		f
9	PKG-1768670918	5	8	4	5	1	20	15	10	1.00	145.13	2	2026-01-17 18:43:35.593386	\N	\N	\N	f
5	PKG-1767970755	5	1	3	3	3	20	15	10	800.70	20.10	7	2026-01-09 15:59:15.05482	\N	\N	\N	f
1	PKG-1767927130	5	1	4	3	1	20	15	10	5.00	285.10	6	2026-01-09 03:52:10.830927	\N	\N	\N	f
10	PKG-1768750634	1	5	4	5	3	20	15	10	800.00	160.13	1	2026-01-18 16:37:14.128417	\N	\N	\N	f
23	PKG-1768980544	5	9	1	7	3	20	15	10	0.10	25.51	6	2026-01-21 08:29:13.651146	\N	\N	\N	f
19	PKG-1768917402	5	8	1	2	1	20	15	10	5.00	5.09	6	2026-01-20 17:47:54.09742	\N	\N	Zepsute :(	t
13	PKG-1768916167	5	8	5	7	2	20	15	10	8.00	165.13	2	2026-01-20 14:37:53.617089	\N	\N	\N	f
15	PKG-1768916608	5	8	2	4	1	20	15	10	4.00	175.10	1	2026-01-20 14:43:28.52891	\N	\N	\N	f
16	PKG-1768916999	5	1	2	1	3	20	15	10	55.00	20.09	1	2026-01-20 14:49:59.508729	\N	\N	\N	f
17	PKG-1768917159	5	1	2	5	1	20	15	10	2.00	175.13	1	2026-01-20 14:52:39.965652	\N	\N	\N	f
18	PKG-1768917376	5	8	1	2	1	20	15	10	1.00	5.09	1	2026-01-20 14:56:16.134419	\N	\N	\N	f
20	PKG-1768918282	5	2	2	3	2	20	15	10	0.00	115.10	7	2026-01-20 15:11:22.674412	\N	\N	\N	f
4	PKG-1767936287	8	5	1	4	2	20	15	10	7.00	180.09	4	2026-01-18 19:08:30.029357	\N	\N	\N	f
11	PKG-1768759326	5	8	1	2	2	20	15	10	50.00	15.09	6	2026-01-18 19:02:40.860877	\N	\N	\N	f
24	PKG-1769131394	5	9	1	7	2	20	15	10	700.40	25.51	6	2026-01-23 02:23:29.652139	\N	\N	\N	f
25	PKG-1769135519	5	8	1	7	1	20	15	10	999.90	20.51	6	2026-01-23 03:32:16.014834	\N	\N	\N	t
\.


--
-- Data for Name: rezerwacja_skrytki; Type: TABLE DATA; Schema: public; Owner: cbd_user
--

COPY public.rezerwacja_skrytki (przesylka_id, skrytka_id, data_rezerwacji, data_wygasniecia, status_id) FROM stdin;
9	31	2026-01-17 18:28:38.423484	2026-01-20 18:28:38.423484	1
10	113	2026-01-18 16:37:14.128417	2026-01-21 16:37:14.128417	1
11	56	2026-01-18 19:02:06.476857	2026-01-21 19:02:06.476857	1
12	103	2026-01-20 13:05:40.600454	2026-01-23 13:05:40.600454	1
13	88	2026-01-20 14:36:07.6962	2026-01-23 14:36:07.6962	1
14	57	2026-01-20 14:38:25.642154	2026-01-23 14:38:25.642154	1
15	11	2026-01-20 14:43:28.52891	2026-01-23 14:43:28.52891	1
16	104	2026-01-20 14:49:59.508729	2026-01-23 14:49:59.508729	1
17	12	2026-01-20 14:52:39.965652	2026-01-23 14:52:39.965652	1
18	1	2026-01-20 14:56:16.134419	2026-01-23 14:56:16.134419	1
19	2	2026-01-20 14:56:42.031486	2026-01-23 14:56:42.031486	1
20	64	2026-01-20 15:11:22.674412	2026-01-20 15:55:42.684339	2
21	64	2026-01-20 16:08:49.298667	2026-01-23 16:08:49.298667	1
11	65	2026-01-21 00:18:14.586192	2026-01-21 00:29:25.732476	2
21	72	2026-01-21 02:18:13.096541	2026-01-21 02:18:21.131881	2
12	108	2026-01-21 02:18:30.0382	2026-01-24 02:18:30.0382	1
14	136	2026-01-21 02:47:37.559134	2026-01-21 02:48:03.625314	2
22	21	2026-01-21 03:02:54.718436	2026-01-24 03:02:54.718436	1
23	98	2026-01-21 08:29:04.146699	2026-01-24 08:29:04.146699	1
23	144	2026-01-21 08:30:49.711581	2026-01-21 08:32:52.085048	2
19	13	2026-01-21 02:56:46.799544	2026-01-22 15:58:24.223761	2
24	58	2026-01-23 02:23:14.668605	2026-01-26 02:23:14.668605	1
24	136	2026-01-23 02:24:50.405649	2026-01-23 02:26:11.573413	2
25	3	2026-01-23 03:31:59.298347	2026-01-26 03:31:59.298347	1
25	126	2026-01-23 03:33:46.871932	2026-01-23 03:34:31.913835	2
\.


--
-- Data for Name: rola_pracownika; Type: TABLE DATA; Schema: public; Owner: cbd_user
--

COPY public.rola_pracownika (id, rola) FROM stdin;
1	Pracownik
2	Administrator
3	Kierownik
\.


--
-- Data for Name: rozmiar_przesylki; Type: TABLE DATA; Schema: public; Owner: cbd_user
--

COPY public.rozmiar_przesylki (id, rozmiar) FROM stdin;
1	S
2	M
3	L
\.


--
-- Data for Name: rozmiar_skrytki; Type: TABLE DATA; Schema: public; Owner: cbd_user
--

COPY public.rozmiar_skrytki (id, rozmiar) FROM stdin;
1	S
2	M
3	L
\.


--
-- Data for Name: skrytka; Type: TABLE DATA; Schema: public; Owner: cbd_user
--

COPY public.skrytka (id, paczkomat_id, numer_skrytki, rozmiar_id, status_id, data_ostatniej_kontroli) FROM stdin;
4	1	4	1	1	\N
5	1	5	1	1	\N
6	1	6	1	1	\N
7	1	7	1	1	\N
8	1	8	1	1	\N
9	1	9	1	1	\N
10	1	10	1	1	\N
14	2	4	1	1	\N
15	2	5	1	1	\N
16	2	6	1	1	\N
17	2	7	1	1	\N
18	2	8	1	1	\N
19	2	9	1	1	\N
20	2	10	1	1	\N
22	3	2	1	1	\N
23	3	3	1	1	\N
24	3	4	1	1	\N
25	3	5	1	1	\N
26	3	6	1	1	\N
27	3	7	1	1	\N
28	3	8	1	1	\N
29	3	9	1	1	\N
30	3	10	1	1	\N
32	4	2	1	1	\N
33	4	3	1	1	\N
34	4	4	1	1	\N
35	4	5	1	1	\N
36	4	6	1	1	\N
37	4	7	1	1	\N
38	4	8	1	1	\N
39	4	9	1	1	\N
40	4	10	1	1	\N
41	5	1	1	1	\N
42	5	2	1	1	\N
43	5	3	1	1	\N
44	5	4	1	1	\N
45	5	5	1	1	\N
46	5	6	1	1	\N
47	5	7	1	1	\N
48	5	8	1	1	\N
49	5	9	1	1	\N
50	5	10	1	1	\N
51	5	11	1	1	\N
52	5	12	1	1	\N
53	5	13	1	1	\N
54	5	14	1	1	\N
55	5	15	1	1	\N
59	1	14	2	1	\N
60	1	15	2	1	\N
61	1	16	2	1	\N
62	1	17	2	1	\N
63	1	18	2	1	\N
66	2	13	2	1	\N
67	2	14	2	1	\N
68	2	15	2	1	\N
69	2	16	2	1	\N
70	2	17	2	1	\N
71	2	18	2	1	\N
73	3	12	2	1	\N
74	3	13	2	1	\N
75	3	14	2	1	\N
76	3	15	2	1	\N
77	3	16	2	1	\N
78	3	17	2	1	\N
79	3	18	2	1	\N
80	4	11	2	1	\N
81	4	12	2	1	\N
82	4	13	2	1	\N
83	4	14	2	1	\N
84	4	15	2	1	\N
85	4	16	2	1	\N
86	4	17	2	1	\N
87	4	18	2	1	\N
89	5	17	2	1	\N
90	5	18	2	1	\N
91	5	19	2	1	\N
92	5	20	2	1	\N
93	5	21	2	1	\N
94	5	22	2	1	\N
95	5	23	2	1	\N
96	5	24	2	1	\N
97	5	25	2	1	\N
99	1	20	3	1	\N
100	1	21	3	1	\N
101	1	22	3	1	\N
102	1	23	3	1	\N
105	2	21	3	1	\N
106	2	22	3	1	\N
107	2	23	3	1	\N
109	3	20	3	1	\N
110	3	21	3	1	\N
111	3	22	3	1	\N
112	3	23	3	1	\N
114	4	20	3	1	\N
115	4	21	3	1	\N
116	4	22	3	1	\N
117	4	23	3	1	\N
118	5	26	3	1	\N
119	5	27	3	1	\N
120	5	28	3	1	\N
121	5	29	3	1	\N
122	5	30	3	1	\N
123	5	31	3	1	\N
124	5	32	3	1	\N
125	5	33	3	1	\N
137	7	12	2	1	\N
31	4	1	1	3	\N
113	4	19	3	3	\N
56	1	11	2	3	\N
103	2	19	3	3	\N
88	5	16	2	3	\N
57	1	12	2	3	\N
11	2	1	1	3	\N
138	7	13	2	1	\N
104	2	20	3	3	\N
12	2	2	1	3	\N
1	1	1	1	3	\N
2	1	2	1	3	\N
139	7	14	2	1	\N
140	7	15	2	1	\N
64	2	11	2	3	\N
141	7	16	2	1	\N
142	7	17	2	1	\N
65	2	12	2	1	\N
143	7	18	2	1	\N
72	3	11	2	1	\N
108	3	19	3	3	\N
127	7	2	1	1	\N
128	7	3	1	1	\N
129	7	4	1	1	\N
130	7	5	1	1	\N
131	7	6	1	1	\N
132	7	7	1	1	\N
133	7	8	1	1	\N
134	7	9	1	1	\N
135	7	10	1	1	\N
145	7	20	3	1	\N
146	7	21	3	1	\N
147	7	22	3	1	\N
148	7	23	3	1	\N
58	1	13	2	3	\N
136	7	11	2	1	\N
21	3	1	1	3	\N
98	1	19	3	3	\N
13	2	3	1	1	\N
144	7	19	3	1	\N
3	1	3	1	3	\N
126	7	1	1	1	\N
\.


--
-- Data for Name: spatial_ref_sys; Type: TABLE DATA; Schema: public; Owner: postgres
--

COPY public.spatial_ref_sys (srid, auth_name, auth_srid, srtext, proj4text) FROM stdin;
\.


--
-- Data for Name: status_akcji; Type: TABLE DATA; Schema: public; Owner: cbd_user
--

COPY public.status_akcji (id, status) FROM stdin;
1	Sukces
2	Blad
\.


--
-- Data for Name: status_centrum; Type: TABLE DATA; Schema: public; Owner: cbd_user
--

COPY public.status_centrum (id, status) FROM stdin;
1	Aktywne
2	Nieaktywne
3	Zamkniete
\.


--
-- Data for Name: status_paczkomatu; Type: TABLE DATA; Schema: public; Owner: cbd_user
--

COPY public.status_paczkomatu (id, status) FROM stdin;
1	Sprawny
2	Awaria
3	Wylaczony
\.


--
-- Data for Name: status_pracownika; Type: TABLE DATA; Schema: public; Owner: cbd_user
--

COPY public.status_pracownika (id, status) FROM stdin;
1	Aktywny
2	Nieaktywny
3	Zwolniony
\.


--
-- Data for Name: status_przesylki; Type: TABLE DATA; Schema: public; Owner: cbd_user
--

COPY public.status_przesylki (id, status) FROM stdin;
1	Utworzona
2	Nadana
3	Przyjeta w centrum
4	W transporcie
5	Doreczona
6	Odebrana
7	Anulowana
\.


--
-- Data for Name: status_rezerwacji; Type: TABLE DATA; Schema: public; Owner: cbd_user
--

COPY public.status_rezerwacji (id, status) FROM stdin;
1	Aktywna
2	Zwolniona
3	Wygasla
\.


--
-- Data for Name: status_skrytki; Type: TABLE DATA; Schema: public; Owner: cbd_user
--

COPY public.status_skrytki (id, status) FROM stdin;
1	Wolna
2	Zajeta
3	Zarezerwowana
4	Uszkodzona
\.


--
-- Data for Name: status_trasy; Type: TABLE DATA; Schema: public; Owner: cbd_user
--

COPY public.status_trasy (id, status) FROM stdin;
1	Zaplanowana
2	W trakcie
3	Zakonczona
4	Anulowana
\.


--
-- Data for Name: status_uzytkownika; Type: TABLE DATA; Schema: public; Owner: cbd_user
--

COPY public.status_uzytkownika (id, status) FROM stdin;
1	Aktywny
2	Nieaktywny
\.


--
-- Data for Name: trasa_dostawy; Type: TABLE DATA; Schema: public; Owner: cbd_user
--

COPY public.trasa_dostawy (id, centrum_id, paczkomat_id, przesylka_id, data_utworzenia, status_id) FROM stdin;
\.


--
-- Data for Name: typ_uzytkownika; Type: TABLE DATA; Schema: public; Owner: cbd_user
--

COPY public.typ_uzytkownika (id, typ) FROM stdin;
1	Klient
2	Pracownik
3	Administrator
4	Kierownik
\.


--
-- Name: administrator_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cbd_user
--

SELECT pg_catalog.setval('public.administrator_id_seq', 1, true);


--
-- Name: centrum_logistyczne_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cbd_user
--

SELECT pg_catalog.setval('public.centrum_logistyczne_id_seq', 12, true);


--
-- Name: historia_statusu_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cbd_user
--

SELECT pg_catalog.setval('public.historia_statusu_id_seq', 53, true);


--
-- Name: kierownik_centrum_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cbd_user
--

SELECT pg_catalog.setval('public.kierownik_centrum_id_seq', 2, true);


--
-- Name: klient_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cbd_user
--

SELECT pg_catalog.setval('public.klient_id_seq', 9, true);


--
-- Name: logi_systemowe_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cbd_user
--

SELECT pg_catalog.setval('public.logi_systemowe_id_seq', 1, false);


--
-- Name: macierz_odleglosci_miast_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cbd_user
--

SELECT pg_catalog.setval('public.macierz_odleglosci_miast_id_seq', 16, true);


--
-- Name: miasto_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cbd_user
--

SELECT pg_catalog.setval('public.miasto_id_seq', 6, true);


--
-- Name: paczkomat_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cbd_user
--

SELECT pg_catalog.setval('public.paczkomat_id_seq', 7, true);


--
-- Name: pracownik_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cbd_user
--

SELECT pg_catalog.setval('public.pracownik_id_seq', 3, true);


--
-- Name: przesylka_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cbd_user
--

SELECT pg_catalog.setval('public.przesylka_id_seq', 25, true);


--
-- Name: rola_pracownika_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cbd_user
--

SELECT pg_catalog.setval('public.rola_pracownika_id_seq', 3, true);


--
-- Name: rozmiar_przesylki_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cbd_user
--

SELECT pg_catalog.setval('public.rozmiar_przesylki_id_seq', 3, true);


--
-- Name: rozmiar_skrytki_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cbd_user
--

SELECT pg_catalog.setval('public.rozmiar_skrytki_id_seq', 3, true);


--
-- Name: skrytka_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cbd_user
--

SELECT pg_catalog.setval('public.skrytka_id_seq', 148, true);


--
-- Name: status_akcji_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cbd_user
--

SELECT pg_catalog.setval('public.status_akcji_id_seq', 2, true);


--
-- Name: status_centrum_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cbd_user
--

SELECT pg_catalog.setval('public.status_centrum_id_seq', 3, true);


--
-- Name: status_paczkomatu_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cbd_user
--

SELECT pg_catalog.setval('public.status_paczkomatu_id_seq', 3, true);


--
-- Name: status_pracownika_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cbd_user
--

SELECT pg_catalog.setval('public.status_pracownika_id_seq', 3, true);


--
-- Name: status_przesylki_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cbd_user
--

SELECT pg_catalog.setval('public.status_przesylki_id_seq', 7, true);


--
-- Name: status_rezerwacji_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cbd_user
--

SELECT pg_catalog.setval('public.status_rezerwacji_id_seq', 3, true);


--
-- Name: status_skrytki_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cbd_user
--

SELECT pg_catalog.setval('public.status_skrytki_id_seq', 4, true);


--
-- Name: status_trasy_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cbd_user
--

SELECT pg_catalog.setval('public.status_trasy_id_seq', 4, true);


--
-- Name: status_uzytkownika_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cbd_user
--

SELECT pg_catalog.setval('public.status_uzytkownika_id_seq', 2, true);


--
-- Name: trasa_dostawy_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cbd_user
--

SELECT pg_catalog.setval('public.trasa_dostawy_id_seq', 1, false);


--
-- Name: typ_uzytkownika_id_seq; Type: SEQUENCE SET; Schema: public; Owner: cbd_user
--

SELECT pg_catalog.setval('public.typ_uzytkownika_id_seq', 4, true);


--
-- Name: administrator administrator_pkey; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.administrator
    ADD CONSTRAINT administrator_pkey PRIMARY KEY (id);


--
-- Name: administrator administrator_pracownik_id_key; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.administrator
    ADD CONSTRAINT administrator_pracownik_id_key UNIQUE (pracownik_id);


--
-- Name: centrum_logistyczne centrum_logistyczne_miasto_id_key; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.centrum_logistyczne
    ADD CONSTRAINT centrum_logistyczne_miasto_id_key UNIQUE (miasto_id);


--
-- Name: centrum_logistyczne centrum_logistyczne_pkey; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.centrum_logistyczne
    ADD CONSTRAINT centrum_logistyczne_pkey PRIMARY KEY (id);


--
-- Name: historia_statusu historia_statusu_pkey; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.historia_statusu
    ADD CONSTRAINT historia_statusu_pkey PRIMARY KEY (id);


--
-- Name: kierownik_centrum kierownik_centrum_pkey; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.kierownik_centrum
    ADD CONSTRAINT kierownik_centrum_pkey PRIMARY KEY (id);


--
-- Name: kierownik_centrum kierownik_centrum_pracownik_id_key; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.kierownik_centrum
    ADD CONSTRAINT kierownik_centrum_pracownik_id_key UNIQUE (pracownik_id);


--
-- Name: klient klient_email_key; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.klient
    ADD CONSTRAINT klient_email_key UNIQUE (email);


--
-- Name: klient klient_pkey; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.klient
    ADD CONSTRAINT klient_pkey PRIMARY KEY (id);


--
-- Name: klient klient_telefon_key; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.klient
    ADD CONSTRAINT klient_telefon_key UNIQUE (telefon);


--
-- Name: logi_systemowe logi_systemowe_pkey; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.logi_systemowe
    ADD CONSTRAINT logi_systemowe_pkey PRIMARY KEY (id);


--
-- Name: macierz_odleglosci_miast macierz_odleglosci_miast_miasto_z_id_miasto_do_id_key; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.macierz_odleglosci_miast
    ADD CONSTRAINT macierz_odleglosci_miast_miasto_z_id_miasto_do_id_key UNIQUE (miasto_z_id, miasto_do_id);


--
-- Name: macierz_odleglosci_miast macierz_odleglosci_miast_pkey; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.macierz_odleglosci_miast
    ADD CONSTRAINT macierz_odleglosci_miast_pkey PRIMARY KEY (id);


--
-- Name: miasto miasto_kod_key; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.miasto
    ADD CONSTRAINT miasto_kod_key UNIQUE (kod);


--
-- Name: miasto miasto_nazwa_key; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.miasto
    ADD CONSTRAINT miasto_nazwa_key UNIQUE (nazwa);


--
-- Name: miasto miasto_pkey; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.miasto
    ADD CONSTRAINT miasto_pkey PRIMARY KEY (id);


--
-- Name: paczkomat paczkomat_kod_key; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.paczkomat
    ADD CONSTRAINT paczkomat_kod_key UNIQUE (kod);


--
-- Name: paczkomat paczkomat_pkey; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.paczkomat
    ADD CONSTRAINT paczkomat_pkey PRIMARY KEY (id);


--
-- Name: pracownik pracownik_email_key; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.pracownik
    ADD CONSTRAINT pracownik_email_key UNIQUE (email);


--
-- Name: pracownik pracownik_pkey; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.pracownik
    ADD CONSTRAINT pracownik_pkey PRIMARY KEY (id);


--
-- Name: pracownik pracownik_telefon_key; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.pracownik
    ADD CONSTRAINT pracownik_telefon_key UNIQUE (telefon);


--
-- Name: przesylka przesylka_numer_przesylki_key; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.przesylka
    ADD CONSTRAINT przesylka_numer_przesylki_key UNIQUE (numer_przesylki);


--
-- Name: przesylka przesylka_pkey; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.przesylka
    ADD CONSTRAINT przesylka_pkey PRIMARY KEY (id);


--
-- Name: rezerwacja_skrytki rezerwacja_skrytki_pkey; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.rezerwacja_skrytki
    ADD CONSTRAINT rezerwacja_skrytki_pkey PRIMARY KEY (przesylka_id, skrytka_id);


--
-- Name: rola_pracownika rola_pracownika_pkey; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.rola_pracownika
    ADD CONSTRAINT rola_pracownika_pkey PRIMARY KEY (id);


--
-- Name: rola_pracownika rola_pracownika_rola_key; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.rola_pracownika
    ADD CONSTRAINT rola_pracownika_rola_key UNIQUE (rola);


--
-- Name: rozmiar_przesylki rozmiar_przesylki_pkey; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.rozmiar_przesylki
    ADD CONSTRAINT rozmiar_przesylki_pkey PRIMARY KEY (id);


--
-- Name: rozmiar_przesylki rozmiar_przesylki_rozmiar_key; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.rozmiar_przesylki
    ADD CONSTRAINT rozmiar_przesylki_rozmiar_key UNIQUE (rozmiar);


--
-- Name: rozmiar_skrytki rozmiar_skrytki_pkey; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.rozmiar_skrytki
    ADD CONSTRAINT rozmiar_skrytki_pkey PRIMARY KEY (id);


--
-- Name: rozmiar_skrytki rozmiar_skrytki_rozmiar_key; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.rozmiar_skrytki
    ADD CONSTRAINT rozmiar_skrytki_rozmiar_key UNIQUE (rozmiar);


--
-- Name: skrytka skrytka_paczkomat_id_numer_skrytki_key; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.skrytka
    ADD CONSTRAINT skrytka_paczkomat_id_numer_skrytki_key UNIQUE (paczkomat_id, numer_skrytki);


--
-- Name: skrytka skrytka_pkey; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.skrytka
    ADD CONSTRAINT skrytka_pkey PRIMARY KEY (id);


--
-- Name: status_akcji status_akcji_pkey; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.status_akcji
    ADD CONSTRAINT status_akcji_pkey PRIMARY KEY (id);


--
-- Name: status_akcji status_akcji_status_key; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.status_akcji
    ADD CONSTRAINT status_akcji_status_key UNIQUE (status);


--
-- Name: status_centrum status_centrum_pkey; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.status_centrum
    ADD CONSTRAINT status_centrum_pkey PRIMARY KEY (id);


--
-- Name: status_centrum status_centrum_status_key; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.status_centrum
    ADD CONSTRAINT status_centrum_status_key UNIQUE (status);


--
-- Name: status_paczkomatu status_paczkomatu_pkey; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.status_paczkomatu
    ADD CONSTRAINT status_paczkomatu_pkey PRIMARY KEY (id);


--
-- Name: status_paczkomatu status_paczkomatu_status_key; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.status_paczkomatu
    ADD CONSTRAINT status_paczkomatu_status_key UNIQUE (status);


--
-- Name: status_pracownika status_pracownika_pkey; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.status_pracownika
    ADD CONSTRAINT status_pracownika_pkey PRIMARY KEY (id);


--
-- Name: status_pracownika status_pracownika_status_key; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.status_pracownika
    ADD CONSTRAINT status_pracownika_status_key UNIQUE (status);


--
-- Name: status_przesylki status_przesylki_pkey; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.status_przesylki
    ADD CONSTRAINT status_przesylki_pkey PRIMARY KEY (id);


--
-- Name: status_przesylki status_przesylki_status_key; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.status_przesylki
    ADD CONSTRAINT status_przesylki_status_key UNIQUE (status);


--
-- Name: status_rezerwacji status_rezerwacji_pkey; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.status_rezerwacji
    ADD CONSTRAINT status_rezerwacji_pkey PRIMARY KEY (id);


--
-- Name: status_rezerwacji status_rezerwacji_status_key; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.status_rezerwacji
    ADD CONSTRAINT status_rezerwacji_status_key UNIQUE (status);


--
-- Name: status_skrytki status_skrytki_pkey; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.status_skrytki
    ADD CONSTRAINT status_skrytki_pkey PRIMARY KEY (id);


--
-- Name: status_skrytki status_skrytki_status_key; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.status_skrytki
    ADD CONSTRAINT status_skrytki_status_key UNIQUE (status);


--
-- Name: status_trasy status_trasy_pkey; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.status_trasy
    ADD CONSTRAINT status_trasy_pkey PRIMARY KEY (id);


--
-- Name: status_trasy status_trasy_status_key; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.status_trasy
    ADD CONSTRAINT status_trasy_status_key UNIQUE (status);


--
-- Name: status_uzytkownika status_uzytkownika_pkey; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.status_uzytkownika
    ADD CONSTRAINT status_uzytkownika_pkey PRIMARY KEY (id);


--
-- Name: status_uzytkownika status_uzytkownika_status_key; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.status_uzytkownika
    ADD CONSTRAINT status_uzytkownika_status_key UNIQUE (status);


--
-- Name: trasa_dostawy trasa_dostawy_pkey; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.trasa_dostawy
    ADD CONSTRAINT trasa_dostawy_pkey PRIMARY KEY (id);


--
-- Name: typ_uzytkownika typ_uzytkownika_pkey; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.typ_uzytkownika
    ADD CONSTRAINT typ_uzytkownika_pkey PRIMARY KEY (id);


--
-- Name: typ_uzytkownika typ_uzytkownika_typ_key; Type: CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.typ_uzytkownika
    ADD CONSTRAINT typ_uzytkownika_typ_key UNIQUE (typ);


--
-- Name: idx_historia_przesylka; Type: INDEX; Schema: public; Owner: cbd_user
--

CREATE INDEX idx_historia_przesylka ON public.historia_statusu USING btree (przesylka_id);


--
-- Name: idx_logi_data; Type: INDEX; Schema: public; Owner: cbd_user
--

CREATE INDEX idx_logi_data ON public.logi_systemowe USING btree (data_akcji);


--
-- Name: idx_logi_klient; Type: INDEX; Schema: public; Owner: cbd_user
--

CREATE INDEX idx_logi_klient ON public.logi_systemowe USING btree (klient_id);


--
-- Name: idx_logi_pracownik; Type: INDEX; Schema: public; Owner: cbd_user
--

CREATE INDEX idx_logi_pracownik ON public.logi_systemowe USING btree (pracownik_id);


--
-- Name: idx_macierz_miasta; Type: INDEX; Schema: public; Owner: cbd_user
--

CREATE INDEX idx_macierz_miasta ON public.macierz_odleglosci_miast USING btree (miasto_z_id, miasto_do_id);


--
-- Name: idx_paczkomat_centrum; Type: INDEX; Schema: public; Owner: cbd_user
--

CREATE INDEX idx_paczkomat_centrum ON public.paczkomat USING btree (centrum_id);


--
-- Name: idx_przesylka_nadawca; Type: INDEX; Schema: public; Owner: cbd_user
--

CREATE INDEX idx_przesylka_nadawca ON public.przesylka USING btree (nadawca_id);


--
-- Name: idx_przesylka_odbiorca; Type: INDEX; Schema: public; Owner: cbd_user
--

CREATE INDEX idx_przesylka_odbiorca ON public.przesylka USING btree (odbiorca_id);


--
-- Name: administrator administrator_pracownik_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.administrator
    ADD CONSTRAINT administrator_pracownik_id_fkey FOREIGN KEY (pracownik_id) REFERENCES public.pracownik(id) ON DELETE CASCADE;


--
-- Name: centrum_logistyczne centrum_logistyczne_miasto_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.centrum_logistyczne
    ADD CONSTRAINT centrum_logistyczne_miasto_id_fkey FOREIGN KEY (miasto_id) REFERENCES public.miasto(id) ON DELETE CASCADE;


--
-- Name: centrum_logistyczne centrum_logistyczne_status_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.centrum_logistyczne
    ADD CONSTRAINT centrum_logistyczne_status_id_fkey FOREIGN KEY (status_id) REFERENCES public.status_centrum(id);


--
-- Name: historia_statusu historia_statusu_przesylka_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.historia_statusu
    ADD CONSTRAINT historia_statusu_przesylka_id_fkey FOREIGN KEY (przesylka_id) REFERENCES public.przesylka(id) ON DELETE CASCADE;


--
-- Name: historia_statusu historia_statusu_status_na_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.historia_statusu
    ADD CONSTRAINT historia_statusu_status_na_id_fkey FOREIGN KEY (status_na_id) REFERENCES public.status_przesylki(id);


--
-- Name: historia_statusu historia_statusu_status_z_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.historia_statusu
    ADD CONSTRAINT historia_statusu_status_z_id_fkey FOREIGN KEY (status_z_id) REFERENCES public.status_przesylki(id);


--
-- Name: kierownik_centrum kierownik_centrum_centrum_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.kierownik_centrum
    ADD CONSTRAINT kierownik_centrum_centrum_id_fkey FOREIGN KEY (centrum_id) REFERENCES public.centrum_logistyczne(id) ON DELETE CASCADE;


--
-- Name: kierownik_centrum kierownik_centrum_pracownik_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.kierownik_centrum
    ADD CONSTRAINT kierownik_centrum_pracownik_id_fkey FOREIGN KEY (pracownik_id) REFERENCES public.pracownik(id) ON DELETE CASCADE;


--
-- Name: klient klient_status_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.klient
    ADD CONSTRAINT klient_status_id_fkey FOREIGN KEY (status_id) REFERENCES public.status_uzytkownika(id);


--
-- Name: klient klient_typ_uzytkownika_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.klient
    ADD CONSTRAINT klient_typ_uzytkownika_id_fkey FOREIGN KEY (typ_uzytkownika_id) REFERENCES public.typ_uzytkownika(id);


--
-- Name: logi_systemowe logi_systemowe_klient_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.logi_systemowe
    ADD CONSTRAINT logi_systemowe_klient_id_fkey FOREIGN KEY (klient_id) REFERENCES public.klient(id) ON DELETE SET NULL;


--
-- Name: logi_systemowe logi_systemowe_pracownik_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.logi_systemowe
    ADD CONSTRAINT logi_systemowe_pracownik_id_fkey FOREIGN KEY (pracownik_id) REFERENCES public.pracownik(id) ON DELETE SET NULL;


--
-- Name: logi_systemowe logi_systemowe_status_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.logi_systemowe
    ADD CONSTRAINT logi_systemowe_status_id_fkey FOREIGN KEY (status_id) REFERENCES public.status_akcji(id);


--
-- Name: macierz_odleglosci_miast macierz_odleglosci_miast_miasto_do_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.macierz_odleglosci_miast
    ADD CONSTRAINT macierz_odleglosci_miast_miasto_do_id_fkey FOREIGN KEY (miasto_do_id) REFERENCES public.miasto(id) ON DELETE CASCADE;


--
-- Name: macierz_odleglosci_miast macierz_odleglosci_miast_miasto_z_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.macierz_odleglosci_miast
    ADD CONSTRAINT macierz_odleglosci_miast_miasto_z_id_fkey FOREIGN KEY (miasto_z_id) REFERENCES public.miasto(id) ON DELETE CASCADE;


--
-- Name: paczkomat paczkomat_centrum_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.paczkomat
    ADD CONSTRAINT paczkomat_centrum_id_fkey FOREIGN KEY (centrum_id) REFERENCES public.centrum_logistyczne(id) ON DELETE CASCADE;


--
-- Name: paczkomat paczkomat_status_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.paczkomat
    ADD CONSTRAINT paczkomat_status_id_fkey FOREIGN KEY (status_id) REFERENCES public.status_paczkomatu(id);


--
-- Name: pracownik pracownik_centrum_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.pracownik
    ADD CONSTRAINT pracownik_centrum_id_fkey FOREIGN KEY (centrum_id) REFERENCES public.centrum_logistyczne(id) ON DELETE SET NULL;


--
-- Name: pracownik pracownik_rola_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.pracownik
    ADD CONSTRAINT pracownik_rola_id_fkey FOREIGN KEY (rola_id) REFERENCES public.rola_pracownika(id);


--
-- Name: pracownik pracownik_status_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.pracownik
    ADD CONSTRAINT pracownik_status_id_fkey FOREIGN KEY (status_id) REFERENCES public.status_pracownika(id);


--
-- Name: przesylka przesylka_nadawca_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.przesylka
    ADD CONSTRAINT przesylka_nadawca_id_fkey FOREIGN KEY (nadawca_id) REFERENCES public.klient(id) ON DELETE CASCADE;


--
-- Name: przesylka przesylka_odbiorca_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.przesylka
    ADD CONSTRAINT przesylka_odbiorca_id_fkey FOREIGN KEY (odbiorca_id) REFERENCES public.klient(id) ON DELETE CASCADE;


--
-- Name: przesylka przesylka_paczkomat_docelowy_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.przesylka
    ADD CONSTRAINT przesylka_paczkomat_docelowy_id_fkey FOREIGN KEY (paczkomat_docelowy_id) REFERENCES public.paczkomat(id) ON DELETE CASCADE;


--
-- Name: przesylka przesylka_paczkomat_nadania_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.przesylka
    ADD CONSTRAINT przesylka_paczkomat_nadania_id_fkey FOREIGN KEY (paczkomat_nadania_id) REFERENCES public.paczkomat(id) ON DELETE CASCADE;


--
-- Name: przesylka przesylka_rozmiar_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.przesylka
    ADD CONSTRAINT przesylka_rozmiar_id_fkey FOREIGN KEY (rozmiar_id) REFERENCES public.rozmiar_przesylki(id);


--
-- Name: przesylka przesylka_status_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.przesylka
    ADD CONSTRAINT przesylka_status_id_fkey FOREIGN KEY (status_id) REFERENCES public.status_przesylki(id);


--
-- Name: rezerwacja_skrytki rezerwacja_skrytki_przesylka_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.rezerwacja_skrytki
    ADD CONSTRAINT rezerwacja_skrytki_przesylka_id_fkey FOREIGN KEY (przesylka_id) REFERENCES public.przesylka(id) ON DELETE CASCADE;


--
-- Name: rezerwacja_skrytki rezerwacja_skrytki_skrytka_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.rezerwacja_skrytki
    ADD CONSTRAINT rezerwacja_skrytki_skrytka_id_fkey FOREIGN KEY (skrytka_id) REFERENCES public.skrytka(id) ON DELETE CASCADE;


--
-- Name: rezerwacja_skrytki rezerwacja_skrytki_status_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.rezerwacja_skrytki
    ADD CONSTRAINT rezerwacja_skrytki_status_id_fkey FOREIGN KEY (status_id) REFERENCES public.status_rezerwacji(id);


--
-- Name: skrytka skrytka_paczkomat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.skrytka
    ADD CONSTRAINT skrytka_paczkomat_id_fkey FOREIGN KEY (paczkomat_id) REFERENCES public.paczkomat(id) ON DELETE CASCADE;


--
-- Name: skrytka skrytka_rozmiar_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.skrytka
    ADD CONSTRAINT skrytka_rozmiar_id_fkey FOREIGN KEY (rozmiar_id) REFERENCES public.rozmiar_skrytki(id);


--
-- Name: skrytka skrytka_status_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.skrytka
    ADD CONSTRAINT skrytka_status_id_fkey FOREIGN KEY (status_id) REFERENCES public.status_skrytki(id);


--
-- Name: trasa_dostawy trasa_dostawy_centrum_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.trasa_dostawy
    ADD CONSTRAINT trasa_dostawy_centrum_id_fkey FOREIGN KEY (centrum_id) REFERENCES public.centrum_logistyczne(id) ON DELETE CASCADE;


--
-- Name: trasa_dostawy trasa_dostawy_paczkomat_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.trasa_dostawy
    ADD CONSTRAINT trasa_dostawy_paczkomat_id_fkey FOREIGN KEY (paczkomat_id) REFERENCES public.paczkomat(id) ON DELETE CASCADE;


--
-- Name: trasa_dostawy trasa_dostawy_przesylka_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.trasa_dostawy
    ADD CONSTRAINT trasa_dostawy_przesylka_id_fkey FOREIGN KEY (przesylka_id) REFERENCES public.przesylka(id) ON DELETE CASCADE;


--
-- Name: trasa_dostawy trasa_dostawy_status_id_fkey; Type: FK CONSTRAINT; Schema: public; Owner: cbd_user
--

ALTER TABLE ONLY public.trasa_dostawy
    ADD CONSTRAINT trasa_dostawy_status_id_fkey FOREIGN KEY (status_id) REFERENCES public.status_trasy(id);


--
-- Name: SCHEMA public; Type: ACL; Schema: -; Owner: pg_database_owner
--

GRANT ALL ON SCHEMA public TO cbd_user;


--
-- Name: DEFAULT PRIVILEGES FOR SEQUENCES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON SEQUENCES TO cbd_user;


--
-- Name: DEFAULT PRIVILEGES FOR TABLES; Type: DEFAULT ACL; Schema: public; Owner: postgres
--

ALTER DEFAULT PRIVILEGES FOR ROLE postgres IN SCHEMA public GRANT ALL ON TABLES TO cbd_user;


--
-- PostgreSQL database dump complete
--

\unrestrict 11lFUrg6mY5vct3JyZYePeLSjqAnZVcaKW0GrfA8wQDCoTBOKDAPleMuPFooGte

