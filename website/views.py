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
        uploaded_file = request.files['file']
        if uploaded_file.filename == '':
            flash('File is too short!', category='error')
        else:
            filename = secure_filename(uploaded_file.filename)

            # Construct user-specific filepath
            user_folder = os.path.join(current_app.config['UPLOAD_FOLDER'], str(current_user.id))
            if not os.path.exists(user_folder):
                os.makedirs(user_folder)  # Create user directory
            filepath = os.path.join(user_folder, filename)
            uploaded_file.save(filepath)

            # Make new db entry
            new_file = File(user_id=current_user.id, filename=filename, filepath=filepath)  # Adjust based on your model
            db.session.add(new_file)
            db.session.commit()

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

        # Access filepath from the database record
        filepath = file.filepath

        # Delete the actual file
        if os.path.exists(filepath):
            try:
                os.remove(filepath)
            except OSError as e:
                print(f"Error deleting file: {e}")
                return jsonify({'message': 'Error deleting file'}), 500

        db.session.delete(file)
        db.session.commit()
        return jsonify({'message': 'File deleted successfully'})

    except Exception as e:
        print(f"Error deleting file: {e}")
        return jsonify({'message': 'Error deleting file'}), 500