from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from . import db
from .models import Check_in, Check_out
from datetime import datetime, date, time

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


def get_check_in_time(user_id):
    check_in_entry = Check_in.query.filter_by(user_id=user_id).order_by(Check_in.check_id.desc()).first()
    if check_in_entry:
        return check_in_entry.check_in
    else:
        return None
    
def format_time_difference(time_difference):
    hours, remainder = divmod(time_difference.total_seconds(), 3600)
    minutes, _ = divmod(remainder, 60)
    return f"{int(hours)} hours, {int(minutes)} minutes"

@views.route('/checkOut', methods=['GET','POST'])
@login_required
def checkOut():
    if request.method == "POST":
        check_out_time_str = request.form.get('checkOutTime')
        if check_out_time_str:
            check_out_time = datetime.strptime(check_out_time_str, '%H:%M').time()
            check_out_date = datetime.now().date()
            check_out_datetime = datetime.combine(check_out_date, check_out_time)
            
            # Retrieve the check-in time for the current user
            check_in_time = get_check_in_time(current_user.id)
            if check_in_time:
                check_in_datetime = datetime.combine(datetime.now().date(), check_in_time)
                time_difference = check_out_datetime - check_in_datetime
                
                # Format the time difference
                time_difference_formatted = format_time_difference(time_difference)
                
                flash(f'You have checked out. Time difference: {time_difference_formatted}', category='success')
            else:
                flash('No check-in time found for the user', category='error')
        else:
            flash('Invalid check-out time', category='error')
        
        return render_template("check_out.html", user=current_user)

    # Add a default return statement in case the request method is not "POST"
    return render_template("check_out.html", user=current_user)