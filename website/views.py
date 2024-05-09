from flask import Blueprint, render_template, request, flash, jsonify
from flask_login import login_required, current_user
from .models import File
from . import db
import json

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST': 
        file = request.form.get('file')#Gets the file from the HTML 

        if len(file) < 1:
            flash('File is too short!', category='error') 
        else:
            new_file = File(data=file, user_id=current_user.id)  #providing the schema for the file 
            db.session.add(new_file) #adding the file to the database 
            db.session.commit()
            flash('File added!', category='success')

    return render_template("home.html", user=current_user)


@views.route('/delete-file', methods=['POST'])
def delete_file():  
    file = json.loads(request.data) # this function expects a JSON from the INDEX.js file 
    fileId = file['fileId']
    file = File.query.get(fileId)
    if file:
        if file.user_id == current_user.id:
            db.session.delete(file)
            db.session.commit()

    return jsonify({})
