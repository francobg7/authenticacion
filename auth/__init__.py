# app/auth/__init__.py
from flask import Blueprint

bp = Blueprint('auth', __name__)

from auth import routes