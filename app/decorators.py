from functools import wraps
from flask import session, redirect, url_for


def login_required(f):
    """
    Decorator sprawdzający czy użytkownik jest zalogowany.
    
    Jeśli nie – redirect na login.
    """
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'user_id' not in session:
            return redirect(url_for('auth.login'))
        return f(*args, **kwargs)
    return decorated_function


def role_required(role):
    """
    Decorator sprawdzający rolę użytkownika.
    
    Args:
        role (str): 'Administrator', 'Kierownik', 'Klient'
    
    Działa dla:
    - Pracowników: sprawdza session['user_role'] (z tabeli rola_pracownika)
    - Klientów: sprawdza session['user_type'] == 'Klient'
    
    Jeśli brak dostępu – zwraca 403.
    """
    def decorator(f):
        @wraps(f)
        def decorated_function(*args, **kwargs):
            if 'user_id' not in session:
                return redirect(url_for('auth.login'))
            
            # Dla pracowników (admin/kierownik) sprawdzamy user_role
            if session.get('user_type') == 'Pracownik':
                if session.get('user_role') == role:
                    return f(*args, **kwargs)
            
            # Dla klientów sprawdzamy user_type
            elif session.get('user_type') == role:
                return f(*args, **kwargs)
            
            return "Brak dostępu do tej strony", 403
        return decorated_function
    return decorator
