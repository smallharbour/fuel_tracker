from flask import Flask, render_template, request, redirect, url_for, flash, jsonify
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf.csrf import CSRFProtect
from werkzeug.security import generate_password_hash, check_password_hash
from datetime import datetime
import os

app = Flask(__name__)
app.config['SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///fuel_tracker.db'
app.config['WTF_CSRF_ENABLED'] = True
app.config['WTF_CSRF_SECRET_KEY'] = os.urandom(24)
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
csrf = CSRFProtect(app)
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = 'login'

@app.template_filter('strftime')
def _jinja2_filter_datetime(date, fmt=None):
    if fmt is None:
        fmt = '%Y-%m-%d'
    return date.strftime(fmt)

@app.template_filter('efficiency')
def _jinja2_filter_efficiency(entry):
    try:
        return (float(entry.liters) / float(entry.kilometers)) * 100
    except (ValueError, ZeroDivisionError):
        return 0

@app.template_filter('float')
def _jinja2_filter_float(value):
    try:
        return float(value)
    except (ValueError, TypeError):
        return 0

@app.template_filter('divide')
def _jinja2_filter_divide(value, divisor):
    try:
        return float(value) / float(divisor)
    except (ValueError, ZeroDivisionError):
        return 0

@app.template_filter('multiply')
def _jinja2_filter_multiply(value, multiplier):
    try:
        return float(value) * float(multiplier)
    except ValueError:
        return 0

class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    password_hash = db.Column(db.String(120), nullable=False)
    cars = db.relationship('Car', backref='owner', lazy=True)
    fuel_entries = db.relationship('FuelEntry', backref='user', lazy=True)

class Car(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(80), nullable=False)
    make = db.Column(db.String(80))
    model = db.Column(db.String(80))
    year = db.Column(db.Integer)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    fuel_entries = db.relationship('FuelEntry', backref='car', lazy=True)

class FuelEntry(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    liters = db.Column(db.Float, nullable=False)
    kilometers = db.Column(db.Float, nullable=False)
    cost = db.Column(db.Float, nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    car_id = db.Column(db.Integer, db.ForeignKey('car.id'), nullable=False)

@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

@app.route('/')
@login_required
def index():
    cars = Car.query.filter_by(user_id=current_user.id).all()
    selected_car_id = request.args.get('car_id', type=int)
    
    if selected_car_id:
        entries = FuelEntry.query.filter_by(user_id=current_user.id, car_id=selected_car_id).order_by(FuelEntry.date.desc()).all()
    else:
        entries = FuelEntry.query.filter_by(user_id=current_user.id).order_by(FuelEntry.date.desc()).all()
    
    # Group entries by car
    grouped_entries = {}
    for entry in entries:
        car_name = entry.car.name
        if car_name not in grouped_entries:
            grouped_entries[car_name] = []
        grouped_entries[car_name].append(entry)
    
    return render_template('index.html', entries=entries, cars=cars, selected_car_id=selected_car_id, grouped_entries=grouped_entries)

@app.route('/add_entry', methods=['POST'])
@login_required
def add_entry():
    date = datetime.strptime(request.form.get('date'), '%Y-%m-%d')
    liters = float(request.form.get('liters'))
    kilometers = float(request.form.get('kilometers'))
    cost = float(request.form.get('cost'))
    car_id = int(request.form.get('car_id'))
    
    entry = FuelEntry(
        date=date,
        liters=liters,
        kilometers=kilometers,
        cost=cost,
        user_id=current_user.id,
        car_id=car_id
    )
    
    db.session.add(entry)
    db.session.commit()
    
    flash('Entry added successfully!')
    return redirect(url_for('index'))

@app.route('/add_car', methods=['POST'])
@login_required
def add_car():
    name = request.form.get('name')
    make = request.form.get('make')
    model = request.form.get('model')
    year = int(request.form.get('year'))
    
    car = Car(
        name=name,
        make=make,
        model=model,
        year=year,
        user_id=current_user.id
    )
    
    db.session.add(car)
    db.session.commit()
    
    flash('Car added successfully!')
    return redirect(url_for('index'))

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        user = User.query.filter_by(username=username).first()
        
        if user and check_password_hash(user.password_hash, password):
            login_user(user)
            return redirect(url_for('index'))
        flash('Invalid username or password', 'error')
    return render_template('login.html')

@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'error')
            return redirect(url_for('register'))
            
        user = User(username=username, password_hash=generate_password_hash(password))
        db.session.add(user)
        db.session.commit()
        flash('Registration successful! Please login.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')

@app.route('/logout')
@login_required
def logout():
    logout_user()
    return redirect(url_for('login'))

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True, port=5001) 