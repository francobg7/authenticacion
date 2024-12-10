# auth/routes.py
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField, SubmitField
from wtforms.validators import DataRequired, Email, EqualTo, Length
from flask import render_template, redirect, url_for, flash, request
from flask_login import login_user, logout_user, login_required, current_user
from werkzeug.security import generate_password_hash, check_password_hash
from utils.database import get_db_connection
from auth import bp
from models.user import User
from utils.security import csrf, rate_limit
from utils.validators import validate_and_sanitize_user_data



class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Contraseña', validators=[DataRequired()])
    submit = SubmitField('Iniciar Sesión')


class RegistrationForm(FlaskForm):
    email = StringField('Email', validators=[
        DataRequired(), 
        Email(message='Ingrese un email válido')
    ])
    password = PasswordField('Contraseña', validators=[
        DataRequired(),
        Length(min=6, message='La contraseña debe tener al menos 6 caracteres')
    ])
    confirm_password = PasswordField('Confirmar Contraseña', validators=[
        DataRequired(),
        EqualTo('password', message='Las contraseñas deben coincidir')
    ])
    submit = SubmitField('Registrarse')


@bp.route('/')
def index():
    return render_template('index.html')

@bp.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()  # Crea una instancia del formulario
    
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    
    if form.validate_on_submit():  # Usa validate_on_submit en lugar de request.method
        email = form.email.data
        password = form.password.data
        
        user = User.get_by_email(email)
        
        if user and user.check_password(password):
            login_user(user)
            return redirect(url_for('admin.dashboard'))
        
        flash('Email o contraseña incorrectos', 'error')
    
    return render_template('login.html', form=form)  # Pasa el form al template

@bp.route('/register', methods=['GET', 'POST'])
def register():
    if current_user.is_authenticated:
        return redirect(url_for('admin.dashboard'))
    
    form = RegistrationForm()  # Crea una instancia del formulario
    
    if form.validate_on_submit():  # Usa validate_on_submit en lugar de request.method
        email = form.email.data
        password = form.password.data
        
        if User.get_by_email(email):
            flash('El email ya está registrado', 'error')
            return render_template('register.html', form=form)
        
        user = User(email=email)
        user.set_password(password)
        
        if user.save():
            flash('Registro exitoso. Por favor inicia sesión', 'success')
            return redirect(url_for('auth.login'))
        
        flash('Error al registrar usuario', 'error')
    
    return render_template('register.html', form=form) 

@bp.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('auth.login'))