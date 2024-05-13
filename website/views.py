from flask import Blueprint, render_template, request, flash, jsonify, current_app, session
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .models import File, User
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
            flash('No File selected for Upload!', category='error')
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
@login_required
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
                flash('Error deleting file: {e}', category='error')
                print(f"Error deleting file: {e}")
                return jsonify({'message': 'Error deleting file'}), 500

        db.session.delete(file)
        db.session.commit()
        flash('File deleted successfully!', category='success')
        return jsonify({'message': 'File deleted successfully'})

    except Exception as e:
        flash('Error deleting file: {e}', category='error')
        return jsonify({'message': 'Error deleting file'}), 500

@views.route('/select-users', methods=['GET', 'POST'])
@login_required
def select_users():
    if request.method == 'GET':
        # Existing logic to retrieve files (optional)
        return render_template("home.html", files=files)  # Pass files data to template for display

    if request.method == 'POST':
        selected_files = request.form.getlist('selected_files')  # Assuming a form with checkboxes for files
        # ... (logic to validate and process selected files) ...

        # Retrieve stored selected file IDs (assuming session)
        stored_selected_file_ids_str = session.get('selected_file_ids')
        if stored_selected_file_ids_str:
            try:
                stored_selected_file_ids = json.loads(stored_selected_file_ids_str)  # Convert back to list
            except Exception:
                stored_selected_file_ids = []  # Handle potential errors during conversion
        else:
            stored_selected_file_ids = []  # Set to an empty list if no value found in session

        # Get all users (excluding the current user)
        all_users = User.query.all()

        # Filter users who don't own any of the selected files
        available_users = [user for user in all_users if user != current_user and not any(file_id == user.id for file_id in stored_selected_file_ids)]

        # Extract user data (ID and email)
        available_user_data = []
        for user in available_users:
            available_user_data.append({'id': user.id, 'email': user.email})

        return render_template("select_users.html", available_users=available_user_data, user=current_user)  # Render select_users.html

@views.route('/share-file', methods=['POST'])
@login_required
def share_file():
    # Retrieve selected user IDs from the form
    selected_user_ids = request.form.getlist('selected_user_ids')

    # Access previously stored selected file IDs (from hidden field)
    stored_selected_file_ids = request.form.get('selected_file_ids')  # Assuming a hidden field

    # ... (logic to validate and process IDs) ...

    # Update database to share files with selected users
    # ... (use selected_file_ids and selected_user_ids to create database entries) ...

    return render_template("home.html", user=current_user) 
