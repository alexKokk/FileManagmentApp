from flask import Blueprint, render_template, request, flash, jsonify, current_app, session, redirect, url_for,  make_response
from flask_login import login_required, current_user
from werkzeug.utils import secure_filename
from .models import File, User
from . import db
import json
import os
from sqlalchemy import join

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
    
    shared_files = File.query.join(File.shared_with).filter(User.id == current_user.id).all()
    print(shared_files)
    return render_template("home.html", user=current_user, shared_files=shared_files)

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

@views.route('/update-selected-files', methods=['POST'])
@login_required
def update_selected_users():
    try:
        data = request.get_json()
        if data is None:
            return jsonify({'error': 'No data received in request'}), 400

        selected_files = data.get('selected_files', [])  # Handle missing key gracefully
        session['selected_file_ids'] = json.dumps(selected_files)

        return jsonify({'success': True})

    except Exception as e:
        print(f"Error updating selected files: {e}")
        return jsonify({'error': 'Error updating selected files'}), 500

@views.route('/select-users', methods=['POST'])
@login_required
def select_users():
    if request.method == 'POST':
        all_users = User.query.all()
        stored_selected_file_ids = json.loads(session.get('selected_file_ids', '[]'))  # Handle missing key gracefully

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
    selected_user_ids = request.form.getlist('selected_user_ids[]')  # Get a list of selected user IDs
    print(f"Received selected user IDs: {selected_user_ids}")
    stored_selected_file_ids = json.loads(session.get('selected_file_ids', '[]'))
    
    try:    
      # Get the selected files based on the previously stored IDs
      selected_files = File.query.filter(File.id.in_(stored_selected_file_ids)).all()
      for user_id in selected_user_ids:
        # Find the user object based on the ID
        user = User.query.get(user_id)  
        # Check if user already has access to any of the selected files
        already_shared_files = db.session.query(File) \
        .join(User.shared_files) \
        .filter(User.id == user_id) \
        .filter(File.id.in_(stored_selected_file_ids)) \
        .all()

        print(f"SHARING FILES")
        # Share files only if the user doesn't already have access
        for file in selected_files:
          if file not in already_shared_files:
            file.shared_with.append(user)  # Add the user to the file's "shared_with" relationship
            flash('succeed File Share' , 'success')
      db.session.commit()   
      # Clear temporary session data
      session.pop('selected_file_ids', None)    
      #flash('Files shared successfully!', 'success')
      return redirect(url_for('views.home'))  # Redirect to the home page after sharing 
    except Exception as e:
      # Handle errors appropriately
      db.session.rollback()  # Rollback database changes on error
      flash(f'An error occurred while sharing files: {str(e)}', 'error')
      return redirect(url_for('views.home'))  # Redirect back to the user selection page

@views.route('/download-file/<filename>', methods=['GET'])
@login_required
def download_file(filename):
  user_id = current_user.id  # Assuming you have a current_user object available
  # Construct user-specific filepath based on uploaded filename
  filepath = os.path.join(current_app.config['UPLOAD_FOLDER'], str(user_id), filename)

  if os.path.isfile(filepath):  # Check if file exists
    with open(filepath, 'rb') as file:
      file_data = file.read()
      response = make_response(file_data)
      response.headers['Content-Disposition'] = f'attachment; filename={filename}'
      response.headers['Content-Type'] = 'application/octet-stream'
      return response
  else:
    flash('File not found!', 'error')
    return redirect(url_for('views.home'))  # Redirect back to the home page

@views.route('/admin', methods=['GET'])
@login_required
def admin():
  # Check if user is logged in and has admin privileges
  if current_user.is_authenticated and current_user.is_admin:
    # Get all users (excluding the current admin user)
    users = User.query.filter(User.id != current_user.id).all()

    # Pass the list of users to the admin.html template
    return render_template('admin.html', users=users, user=current_user)
  else:
    # Redirect to login page or display an unauthorized message
    return redirect(url_for('auth.login'))


