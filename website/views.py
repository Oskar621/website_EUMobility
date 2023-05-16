from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from . import db
from .models import Check_in, Check_out
from datetime import datetime, date

views = Blueprint('views', __name__)

@views.route('/checkIn', methods=['GET', 'POST'])
@login_required
def checkIn():
    if request.method == "POST":
        check_in_time_str = request.form.get('checkInTime')
        if check_in_time_str:
            check_in_time = datetime.strptime(check_in_time_str, '%H:%M').time()
            check_in_date = date.today()

            new_check = Check_in(user_id=current_user.id, check_in=check_in_time, date=check_in_date)
            db.session.add(new_check)
            db.session.commit()
            flash('You have checked in', category='success')
        else:
            flash('Invalid check-in time', category='error')

    return render_template("check_in.html", user=current_user)


@views.route('/checkOut', methods=['GET','POST'])
@login_required
def checkOut():
    if request.method == "POST":
        check_out_time_str = request.form.get('checkOutTime')
        if check_out_time_str:
            check_out_time = datetime.strptime(check_out_time_str, '%H:%M').time()
            check_out_date = date.today()
            new_check = Check_out(user_id=current_user.id, check_out=check_out_time, date=check_out_date)
            db.session.add(new_check)
            db.session.commit()
            flash('You have checked out', category='success')
        else:
            flash('Invalid check-out time', category='error')

    return render_template("check_out.html", user=current_user)
