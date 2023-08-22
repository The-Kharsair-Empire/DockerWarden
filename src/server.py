import os
import uuid

from dotenv import find_dotenv, set_key as dotenv_set_key
from flask import Blueprint, render_template, request, redirect, url_for, send_from_directory, send_file, jsonify
from .authentication import allowed_addr_only, User, LoginForm
from flask_login import login_required, login_user, logout_user
from .api import endpoints

server = Blueprint(os.getenv('SERVER_BLUEPRINT_NAME', 'server'), __name__,
                   template_folder='../templates',
                   static_folder='../static')


@server.route('/')
@server.route('/index')
@allowed_addr_only
@login_required
def home():
    return render_template('dashboard.html', endpoints=endpoints)


@server.route('/login', methods=['GET', 'POST'])
@allowed_addr_only
def login():
    login_form = LoginForm()
    if request.method == 'POST':
        if login_form.validate_on_submit():
            only_user = User()
            if (str(login_form.username.data) == only_user.username
                    and str(login_form.password.data) == only_user.passphrase):
                remember_user = login_form.remember_login.data
                login_user(only_user, remember=remember_user)
                return redirect(url_for('server.home'))
            else:
                return render_template('bad_request_400.html', err="Authentication Failed")
        else:
            return render_template('bad_request_400.html', err="Invalid Authentication Info")
    else:
        return render_template('login.html', login_form=login_form)


@server.route("/logout")
@allowed_addr_only
@login_required
def logout():
    logout_user()
    """
    Also invalidate previous key just in case
    """
    user = User()
    user.api_key.update_key()
    return redirect(url_for('server.login'))


@server.route("/refresh_api")
@allowed_addr_only
@login_required
def refresh_api():
    os.environ['API_KEY'] = uuid.uuid4().hex
    dotenv_set_key(find_dotenv(), 'API_KEY', os.environ['API_KEY'])
    return jsonify({'new_api': os.getenv('API_KEY'), 'msg': 'your new key'})


@server.route('/static/dashboard.js', methods=['GET'])
def dashboard_js():
    return send_from_directory(os.path.join(server.root_path, '..', 'static'), 'dashboard.js')


@server.route('/static/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(server.root_path, '..', 'static'),
                               'favicon.ico')
