from flask import Blueprint, render_template, request, flash, jsonify, current_app
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .models import File
from . import db
import json
import os

views = Blueprint('views', __name__)


@views.route('/', methods=['GET', 'POST'])
@login_required
def home():
    if request.method == 'POST':
        uploaded_file = request.files['file']  # Gets the file from the HTML

        if uploaded_file.filename == '':
            flash('File is empty!', category='error')
        else:
            filename = secure_filename(uploaded_file.filename)  # Sanitize filename
            filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], filename)
            uploaded_file.save(filepath)

            new_file = File(filename=filename, filepath=filepath, user_id=current_user.id)
            db.session.add(new_file)  # adding the file to the database
            db.session.commit()
            flash('File uploaded successfully!', category='success')

    return render_template("home.html", user=current_user)

    #  If you need to update the displayed content on the "home" page based on the upload, use render_template. 
    #  If a simple redirection is sufficient, use redirect.
    #return redirect(url_for('home'))

@views.route('/delete-file', methods=['POST'])
def delete_file():
    try:
        file_data = json.loads(request.data)
        file_id = file_data['fileId']
        file = File.query.get(file_id)

        if not file:
            # File not found
            return jsonify({'message': 'File not found'}), 404

        if file.user_id != current_user.id:
            # Unauthorized deletion attempt
            return jsonify({'message': 'Unauthorized deletion'}), 403

        # Delete the actual file
        file_path = os.path.join(current_app.config['UPLOAD_FOLDER'], file.filename)
        if os.path.exists(file_path):
            try:
                os.remove(file_path)
            except OSError as e:
                print(f"Error deleting file: {e}")
                return jsonify({'message': 'Error deleting file'}), 500

        db.session.delete(file)
        db.session.commit()
        return jsonify({'message': 'File deleted successfully'})

    except Exception as e:
        print(f"Error deleting file: {e}")
        return jsonify({'message': 'Error deleting file'}), 500