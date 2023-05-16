from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import Check_in
from . import db

views = Blueprint('views', __name__)


@views.route('/checkIn', methods=['GET', 'POST'])
@login_required
def checkIn():
    return render_template("check_in.html", user=current_user)

@views.route('/checkOut', methods=['GET','POST'])
@login_required
def checkOut():
    return render_template("check_out.html", user=current_user)