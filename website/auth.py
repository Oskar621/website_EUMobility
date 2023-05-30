from flask import Blueprint, render_template, request, flash, redirect, url_for
from .models import User
from werkzeug.security import generate_password_hash, check_password_hash
from . import db   ##means from __init__.py import db
from flask_login import login_user, login_required, logout_user, current_user
import gspread

auth = Blueprint('auth', __name__)

@auth.route('/', methods=['GET','POST'])
def starter_page():
    return redirect(url_for('views.checkIn'))

@auth.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        login = request.form.get('login')
        password = request.form.get('password')

        user = User.query.filter_by(login=login).first()
        if user:
            if check_password_hash(user.password, password):
                login_user(user, remember=True)
                flash(f'Dear {current_user.name} welcome to EUMobility Sverige', category="success")
                return redirect(url_for('views.checkIn'))
            else:
                flash('Incorrect password, try again.', category='error')
        else:
            flash('Login does not exist.', category='error')

    return render_template("login.html", user=current_user)


@auth.route('/logout')
@login_required
def logout():
    logout_user()
    flash('You have logged out', category="success")
    return redirect(url_for('auth.login'))


@auth.route('/sign-up', methods=['GET', 'POST'])
def sign_up():
    if request.method == 'POST':
        login = request.form.get('login')
        password1 = request.form.get('password1')
        password2 = request.form.get('password2')
        name = request.form.get('name')
        home_address = request.form.get('home_address')
        work_position = request.form.get('work_position')
        work_email= request.form.get('work_email')
        phone_number = request.form.get('phone_number')
        contract_hours = request.form.get('contract_hours')
        user = User.query.filter_by(login=login).first()
        
        #checking user data        
        if user:
            flash('Login already exists.', category='error')
        elif len(login) < 4:
            flash('Login must be greater than 3 characters.', category='error')
        elif password1 != password2:
            flash('Passwords don\'t match.', category='error')
        elif len(password1) < 7:
            flash('Password must be at least 7 characters.', category='error')
        else:
            new_user = User(login=login,
                            password=generate_password_hash(password1, method='sha256'),
                            name = name,
                            home_address = home_address,
                            work_position = work_position,
                            work_email = work_email,                            
                            phone_number = phone_number,
                            contract_hours = contract_hours
                            )
            db.session.add(new_user)
            db.session.commit()

            #inserting data to created google sheets
            scope = [
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive',
                ]
            client = gspread.service_account(filename='eumobility-project.json')
            sheet_name = str(name) + " work hours"
            sheet = client.create(sheet_name)
            sheet.share(work_email, perm_type='user', role='writer')
            sheet = client.open('User data').sheet1
            try: 
                sheet.append_row([name, login, password1, home_address, work_position, work_email, phone_number, contract_hours])
            except Exception as e:
                    print(f"Exception occurred while inserting data: {str(e)}")
                    flash('Failed to insert data', category='error')
            
            #login user
            login_user(new_user, remember=True)
            flash('Account created!', category='success')
            return redirect(url_for('views.checkIn'))
    return render_template("sign_up.html", user=current_user)
