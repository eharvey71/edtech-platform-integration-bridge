from flask import Blueprint, request, render_template, redirect, url_for, flash
from flask_login import login_required
from src.models import VendorProxies, KalturaAppToken, AccessRestrictions, AppTokenSessionDefaults, db

kaltura_bp = Blueprint('kaltura', __name__, template_folder='templates')

@kaltura_bp.route('/manage')
@login_required
def kaltura_manage():
    if VendorProxies.query.get(1).kaltura_proxy_enabled == False:
        return redirect(url_for('settings.main_config'))
    tokens = KalturaAppToken.query.all()
    return render_template("kaltura-manage.html", tokens=tokens)

@kaltura_bp.route('/config', methods=('GET', 'POST'))
@login_required
def kaltura_config():
    if VendorProxies.query.get(1).kaltura_proxy_enabled == False:
        return redirect(url_for('settings.main_config'))
    
    access_restrictions = AccessRestrictions.query.get(1)
    apptoken_session_defaults = AppTokenSessionDefaults.query.get(1)
    
    if request.method == 'GET':
        return render_template('kaltura-config.html', access_restrictions=access_restrictions, \
                               apptoken_session_defaults=apptoken_session_defaults)
        
    elif request.method == 'POST':
        
        if request.args.get("f") == "restrictions":
            access_restrictions.allowed_categories = request.form.get('force-cats')
            access_restrictions.force_labels = True if request.form.get('force-labels') else False
            db.session.add(access_restrictions)
            db.session.commit()
            flash('Kaltura Access Restrictions config updated', 'warning')
        elif request.args.get("f") == "sessions":
            apptoken_session_defaults.partner_id = request.form.get('partner-id')
            apptoken_session_defaults.session_expiry = request.form.get('session-expiry')
            apptoken_session_defaults.use_local_storage = True if request.form.get('use-local-storage') else False
            db.session.add(apptoken_session_defaults)
            db.session.commit()
            flash('Session Defaults config updated', 'warning')
        
        return redirect(url_for('kaltura.kaltura_config'))
    
@kaltura_bp.route('/addtokens')
@login_required
def kaltura_addtokens():
    if VendorProxies.query.get(1).kaltura_proxy_enabled == False:
        return redirect(url_for('settings.main_config'))
    return render_template('kaltura-addtokens.html')