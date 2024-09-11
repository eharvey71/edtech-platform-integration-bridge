from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required
from src.models import VendorProxies, ZoomClientConfig, db
import secrets

zoom_bp = Blueprint('zoom', __name__, template_folder='templates')

@zoom_bp.route('/config', methods=('GET', 'POST'))
@login_required
def zoom_config():
    if not VendorProxies.query.get(1).zoom_proxy_enabled:
        return redirect(url_for('settings.main_config'))
    
    zoom_config = ZoomClientConfig.query.get(1)
    if not zoom_config:
        zoom_config = ZoomClientConfig()
        zoom_config.access_key = secrets.token_urlsafe(32)
        db.session.add(zoom_config)
        db.session.commit()
    
    if request.method == 'POST':
        action = request.form.get('action')
        
        if action == 'update':
            zoom_config.zoom_client_id = request.form.get('zoom-client-id')
            zoom_config.zoom_client_secret = request.form.get('zoom-client-secret')
            zoom_config.zoom_account_id = request.form.get('zoom-account-id')
            zoom_config.require_access_key = 'require-access-key' in request.form
            db.session.commit()
            flash('Zoom Client config updated', 'success')
        
        elif action == 'regenerate':
            zoom_config.access_key = secrets.token_urlsafe(32)
            db.session.commit()
            flash('Access Key regenerated', 'success')
        
        return redirect(url_for('zoom.zoom_config'))
    
    return render_template('zoom-config.html', zoom_config=zoom_config)

@zoom_bp.route('/regenerate-access-key', methods=['POST'])
@login_required
def regenerate_access_key():
    zoom_config = ZoomClientConfig.query.get(1)
    if zoom_config:
        zoom_config.access_key = secrets.token_urlsafe(32)
        db.session.commit()
        flash('Access Key regenerated', 'success')
    else:
        flash('Zoom configuration not found', 'error')
    return redirect(url_for('zoom.zoom_config'))