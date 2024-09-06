from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required
from src.models import VendorProxies, ZoomClientConfig, db

zoom_bp = Blueprint('zoom', __name__, template_folder='templates')

@zoom_bp.route('/config', methods=('GET', 'POST'))
@login_required
def zoom_config():
    if VendorProxies.query.get(1).zoom_proxy_enabled == False:
        return redirect(url_for('settings.main_config'))
    
    zoom_config = ZoomClientConfig.query.get(1)
    
    if request.method == 'GET':
        return render_template('zoom-config.html', zoom_config=zoom_config)
        
    elif request.method == 'POST':     
        if request.args.get("f") == "zoom_config":
            zoom_config.zoom_client_id = request.form.get('zoom-client-id')
            zoom_config.zoom_client_secret = request.form.get('zoom-client-secret')
            zoom_config.zoom_account_id = request.form.get('zoom-account-id')
            db.session.add(zoom_config)
            db.session.commit()
            flash('Zoom Client config updated', 'warning')
        
        return redirect(url_for('zoom.zoom_config'))