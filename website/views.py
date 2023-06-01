from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from . import db
from .models import Check_in, Check_out
from datetime import datetime, date
import gspread

views = Blueprint('views', __name__)

@views.route('/checkIn', methods=['GET', 'POST'])
@login_required
def checkIn():
    if request.method == "POST":
        check_in_time_str = request.form.get('checkInTime')
        check_in_date_str = request.form.get('checkInDate')
        if check_in_time_str:
            check_in_time = datetime.strptime(check_in_time_str, '%H:%M').time()
            check_in_date = datetime.strptime(check_in_date_str, '%Y-%m-%d').date()
            new_check = Check_in(user_id=current_user.id, check_in=check_in_time, date=check_in_date)
            db.session.add(new_check)
            db.session.commit()
            flash('Bring it on, smile and do your best', category='success')
        else:
            flash('Invalid check-in time', category='error')
    return render_template("check_in.html", user=current_user)


@views.route('/checkOut', methods=['GET','POST'])
@login_required
def checkOut():
    if request.method == "POST":
        # Process the check-out request
        check_out_time_str = request.form.get('checkOutTime')
        check_out_date_str = request.form.get('checkOutDate')
        
        if check_out_time_str:
            # Parse check-out time and date
            check_out_time = datetime.strptime(check_out_time_str, '%H:%M').time()
            check_out_date = datetime.strptime(check_out_date_str, '%Y-%m-%d').date()
            
            # Create datetime object combining check-out date and time
            check_out_datetime = datetime.combine(check_out_date, check_out_time)
            
            # Create a new check-out record in the Check_out table
            new_check = Check_out(user_id=current_user.id, check_out=check_out_time, date=check_out_date)
            db.session.add(new_check)
            db.session.commit()

            # Retrieve the check-in time for the current user
            check_in_record = Check_in.query.filter_by(user_id=current_user.id).order_by(Check_in.check_id.desc()).first()
            
            if check_in_record:
                check_in_time = check_in_record.check_in  # Extract check-in time from the Check_in record
                check_in_date = check_in_record.date
                check_in_datetime = datetime.combine(check_in_date, check_in_time)
                
                # Calculate the time difference between check-in and check-out
                time_difference = check_out_datetime - check_in_datetime
                
                # Calculate comfortable and uncomfortable hours
                hours, remainder = divmod(time_difference.total_seconds(), 3600)
                minutes, _ = divmod(remainder, 60)
                
                if hours >= 0:
                    comfortable_hours = hours
                    uncomfortable_hours = 0
                    
                    if hours > 9:
                        comfortable_hours = 8
                        uncomfortable_hours = hours - 8

                    # Insert data into the user's Google Spreadsheet
                    client = gspread.service_account(filename='eumobility-project.json')
                    sheet_name = str(current_user.name) + " work hours"
                    sheet = client.open(sheet_name).sheet1
                    login = current_user.login
                    contract_hours: int = current_user.contract_hours
                    hours = float(hours)  # Assuming hours is a string representation of a numeric value
                    contract_hours_percentage_str = "-"
                    
                    if contract_hours != 0:
                        contract_hours = float(contract_hours)
                        contract_hours_percentage = hours/contract_hours * 100
                        contract_hours_percentage_str = str(contract_hours_percentage) + "%"
                    
                    check_out_date_str = check_out_date.strftime('%Y-%m-%d')  # Convert the date to a string in the format "YYYY-MM-DD"
                    
                    flash(f'Thank you for your good work, {current_user.name}! Please have a nice time ahead', category='success')
                    
                    try:
                        sheet.append_row([login, check_out_date_str, check_in_time.strftime('%H:%M'), check_out_time.strftime('%H:%M'), comfortable_hours, uncomfortable_hours, minutes, contract_hours, contract_hours_percentage_str])
                    except Exception as e:
                        print(f"Exception occurred while inserting data: {str(e)}")
                        flash('Failed to insert data', category='error')
                else:
                    flash('You can\'t end work before you started', category='error')
            else:
                flash('No check-in time found for the user', category='error')
        else:
            flash('Invalid check-out time', category='error')

    if request.method == "GET":
        # Display a message indicating it's time to finish work
        flash('Is it time to finish the work?', category="success")

    # Render the check-out template
    return render_template("check_out.html", user=current_user)