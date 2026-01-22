from flask import Blueprint, redirect, url_for, session

index_bp = Blueprint('index', __name__, url_prefix='')


@index_bp.route("/")
def index():
    """Redirect na panel zależnie od roli"""
    if 'user_id' not in session:
        return redirect(url_for('auth.login'))
    
    if session.get('user_type') == 'Pracownik':
        if session.get('user_role') == 'Administrator':
            return redirect(url_for('admin.dashboard'))
        elif session.get('user_role') == 'Kierownik':
            return redirect(url_for('kierownik.dashboard'))
    elif session.get('user_type') == 'Klient':
        return redirect(url_for('klient.dashboard'))
    
    return redirect(url_for('auth.login'))
