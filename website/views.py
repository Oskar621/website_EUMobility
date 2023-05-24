from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from . import db
from .models import Check_in, Check_out, User
from datetime import datetime, date, time
import gspread

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
            check_out_date = datetime.now().date()
            check_out_datetime = datetime.combine(check_out_date, check_out_time)
            new_check = Check_out(user_id=current_user.id, check_out=check_out_time, date=check_out_date)
            db.session.add(new_check)
            db.session.commit()
            # Retrieve the check-in time for the current user
            check_in_record = Check_in.query.filter_by(user_id=current_user.id).order_by(Check_in.check_id.desc()).first()
            if check_in_record:
                check_in_time = check_in_record.check_in  # Extract check-in time from the Check_in record
                check_in_datetime = datetime.combine(datetime.now().date(), check_in_time)
                time_difference = check_out_datetime - check_in_datetime

                # Calculate comfortable and uncomfortable hours
                hours, remainder = divmod(time_difference.total_seconds(), 3600)
                minutes, _ = divmod(remainder, 60)
                if 0 <= hours <= 8:
                    comfortable_hours = hours
                    uncomfortable_hours = 0
                    time_difference_formatted = f"{int(hours)} comfortable hours, {int(minutes)} minutes"
                elif hours > 9:
                    comfortable_hours = 8
                    uncomfortable_hours = hours - 8
                    time_difference_formatted = f"{int(comfortable_hours)} comfortable hours, {int(uncomfortable_hours)} uncomfortable hours, {int(minutes)} minutes"

                # Insert data into the spreadsheet
                scope = [
                    'https://www.googleapis.com/auth/spreadsheets',
                    'https://www.googleapis.com/auth/drive',
                ]
                client = gspread.service_account(filename='eumobility-project.json')
                sheet = client.open('Work time2').sheet1
                login = current_user.login
                check_out_date_str = check_out_date.strftime('%Y-%m-%d')  # Convert the date to a string in the format "YYYY-MM-DD"
                flash(f'You have checked out. Time difference: {time_difference_formatted}', category='success')
                try:
                    sheet.append_row([login, check_out_date_str, check_in_time.strftime('%H:%M'), check_out_time.strftime('%H:%M'), comfortable_hours, uncomfortable_hours, minutes])
                except Exception as e:
                    print(f"Exception occurred while inserting data: {str(e)}")
                    flash('Failed to insert data', category='error')
            else:
                flash('No check-in time found for the user', category='error')
        else:
            flash('Invalid check-out time', category='error')
    return render_template("check_out.html", user=current_user)