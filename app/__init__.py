import os
import threading
import time
from multiprocessing import Manager

from flask import Flask, render_template
from flask_login import LoginManager
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import URL
from flask_migrate import Migrate
from turbo_flask import Turbo
from dispatcher.balancer import DummyBalancer
from dispatcher.dispatcher import DummyDispatcher

# init SQLAlchemy so we can use it later in our models
db = SQLAlchemy()
migrate = Migrate()
login_manager = LoginManager()
turbo = Turbo()

dispatcher = DummyDispatcher(
    host=os.environ.get('WSS_HOST', '0.0.0.0'),
    port=os.environ.get('WSS_PORT', 9990),
    cert=os.path.abspath(
        os.environ.get('WSS_CERT', './ca/ca_cert.pem')),
    key=os.path.abspath(
        os.environ.get('WSS_KEY', './ca/ca.pem')),
    bal=DummyBalancer
)
print(os.getcwd())


def create_app():
    app = Flask(__name__)

    app.config['SECRET_KEY'] = os.environ.get('API_KEY', 'change_me_please')
    app.config['SQLALCHEMY_DATABASE_URI'] = URL.create(
        "postgresql",
        username=os.environ.get('POSTGRES_USER', 'admin'),
        password=os.environ.get('POSTGRES_PASSWORD', 'admin'),
        host=os.environ.get('POSTGRES_HOST', 'localhost'),
        database=os.environ.get('DB_NAME', 'db'),
    )
    app.jinja_env.auto_reload = True
    app.jinja_env.trim_blocks = True
    app.jinja_env.lstrip_blocks = True
    app.config['TEMPLATES_AUTO_RELOAD'] = True
    from app.models import User
    db.init_app(app)
    migrate.init_app(app, db)
    login_manager.init_app(app)
    turbo.init_app(app)

    # blueprint for auth routes in our app
    from app.auth import auth as auth_blueprint
    app.register_blueprint(auth_blueprint)

    # blueprint for non-auth parts of app
    from app.main import main as main_blueprint
    app.register_blueprint(main_blueprint)

    dispatcher.start_server()

    @app.context_processor
    def inject_load():
        logs = list(dispatcher.balancer.responses)[::-1]
        print('logs', logs)
        return {'logs': logs}

    def update_load():
        with app.app_context():
            while True:
                time.sleep(5)
                turbo.push(turbo.replace(render_template('log_textarea.html'), 'log'))
    threading.Thread(target=update_load).start()

    @login_manager.user_loader
    def load_user(user_id):
        # since the user_id is just the primary key of our user table, use it in the query for the user
        return User.query.get(int(user_id))

    return app

