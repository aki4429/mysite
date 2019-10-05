#!/usr/bin/env python3
from flask import Flask, request, Response, abort, render_template
from flask_login import LoginManager, login_user, logout_user, login_required, UserMixin
from collections import defaultdict

app = Flask(__name__)
login_manager = LoginManager()
login_manager.init_app(app)
app.config['SECRET_KEY'] = "secret"


