import functools
import uuid

from flask_login import LoginManager, UserMixin
import os
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField, BooleanField
from wtforms.validators import InputRequired
from flask import request, render_template, jsonify

login_manager = LoginManager()


class ApiKey:

    def __init__(self):
        self._api_key = ApiKey._generate_key()

    """
    the purpose of this class is that later stage key can be updated to more sophisticated 
    cryptographic algorithm if needed
    """

    @staticmethod
    def _generate_key() -> str:
        return uuid.uuid4().hex

    def compare_key(self, other: str) -> bool:
        return self._api_key == other

    def update_key(self):
        self._api_key = ApiKey._generate_key()

    @property
    def key(self):
        return self._api_key


# webpage login authentication
class User(UserMixin):
    _instance = None

    def __new__(cls, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._initialize(**kwargs)

        return cls._instance

    def _initialize(self, **kwargs):
        # uid, username, password, active=True
        self.id = kwargs.get('uid', 1)
        self.username = kwargs.get('user', os.getenv('AUTH_USER'))
        self.active = kwargs.get('active', True)
        self.passphrase = kwargs.get('passphrase', os.getenv('AUTH_PASS'))
        self.api_key = ApiKey()
        self.allowed_user_addr = set(
            map(lambda x: x.strip(), kwargs.get('addr', os.getenv('ALLOWED_GUEST')).split(',')))


class LoginForm(FlaskForm):
    username = StringField(
        label='User',
        validators=[InputRequired()],
        render_kw={"placeholder": "user"}
    )
    password = PasswordField(
        label='Pass Phrase',
        validators=[InputRequired()],
        render_kw={"placeholder": "passphrase"}
    )

    remember_login = BooleanField(
        label='Remember Me'
    )
    submit = SubmitField('Login')


@login_manager.user_loader
def load_user(user_id):
    user = User()
    if str(user_id) == str(user.get_id()):
        return user
    else:
        return None


# access control
def allowed_addr_only(func):
    @functools.wraps(func)
    def decorator(*args, **kwargs):
        client_addr = request.remote_addr
        allowed_addr = User().allowed_user_addr
        if client_addr in allowed_addr:
            return func(*args, **kwargs)
        else:
            if request.blueprint == 'server':
                return render_template('unauthorized_403.html', err='Unauthorized Device')
            elif request.blueprint == 'api':
                return jsonify({'err': 'unauthorized device'}), 403

    return decorator


# api authentication
def api_key_required(func):
    @functools.wraps(func)
    def decorator(*args, **kwargs):

        api_key_header = request.headers.get('Authentication', None)
        if api_key_header:
            splited_header = api_key_header.split()
            if len(splited_header) == 2:
                api_key = splited_header[1].strip()
                if api_key:
                    if User().api_key.compare_key(api_key):
                        return func(*args, **kwargs)

                    elif os.getenv('API_KEY', None) == api_key:
                        return func(*args, **kwargs)

        return {"message": "Invalid API Key"}, 403

    return decorator
