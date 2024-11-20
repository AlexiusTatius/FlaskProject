from flask import (
    Blueprint,
    render_template,
    redirect,
    url_for,
    request,
    flash,
    send_from_directory,
    abort,
    current_app,
)
from flask_login import login_user, login_required, logout_user, current_user
from werkzeug.utils import secure_filename
from werkzeug.security import generate_password_hash, check_password_hash
from functools import wraps
from app import db
from app.models import User, File
import os

main = Blueprint('main', __name__)

# Allowed file extensions
ALLOWED_EXTENSIONS = {'pdf', 'docx', 'txt', 'jpg'}

# Helper function to check file extension
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# Decorator for admin-required routes
def admin_required(func):
    @wraps(func)
    def decorated_view(*args, **kwargs):
        if not current_user.is_authenticated or current_user.role != 'admin':
            flash('Admin access required', 'danger')
            return redirect(url_for('main.index'))
        return func(*args, **kwargs)
    return decorated_view

# Home route
@main.route('/')
@login_required
def index():
    user_files = File.query.filter_by(user_id=current_user.id).all()
    total_files = len(user_files)
    total_storage = sum(file.file_size for file in user_files)
    most_viewed = max(user_files, key=lambda x: x.view_count, default=None)
    most_downloaded = max(user_files, key=lambda x: x.download_count, default=None)

    return render_template(
        'index.html',
        total_files=total_files,
        total_storage=total_storage,
        most_viewed=most_viewed.filename if most_viewed else "No files viewed yet",
        most_downloaded=most_downloaded.filename if most_downloaded else "No files downloaded yet"
    )

# Registration route
@main.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']

        if User.query.filter_by(username=username).first():
            flash('Username already exists', 'danger')
            return redirect(url_for('main.register'))

        user = User(username=username)
        user.set_password(password)  # Use set_password() method
        
        db.session.add(user)
        db.session.commit()

        flash('Registration successful. Please login.', 'success')
        return redirect(url_for('main.login'))

    return render_template('register.html')
# Analytics route
@main.route('/analytics')
@login_required
@admin_required  # Using the admin_required decorator you already have
def analytics():
    # Get overall statistics
    total_users = User.query.count()
    total_files = File.query.count()
    total_storage = db.session.query(db.func.sum(File.file_size)).scalar() or 0
    
    # Get most active users
    active_users = (
        User.query
        .join(File)
        .group_by(User.id)
        .with_entities(
            User.username,
            db.func.count(File.id).label('file_count'),
            db.func.sum(File.file_size).label('total_size')
        )
        .order_by(db.text('file_count DESC'))
        .limit(5)
        .all()
    )
    
    # Get most viewed/downloaded files
    most_viewed_files = (
        File.query
        .order_by(File.view_count.desc())
        .limit(5)
        .all()
    )
    
    most_downloaded_files = (
        File.query
        .order_by(File.download_count.desc())
        .limit(5)
        .all()
    )
    
    return render_template(
        'analytics.html',
        total_users=total_users,
        total_files=total_files,
        total_storage=total_storage,
        active_users=active_users,
        most_viewed_files=most_viewed_files,
        most_downloaded_files=most_downloaded_files
    )

# File upload route
@main.route('/upload', methods=['GET', 'POST'])
@login_required
def upload_file():
    if request.method == 'POST':
        if 'file' not in request.files:
            flash('No file selected', 'danger')
            return redirect(request.url)

        file = request.files['file']
        if file and allowed_file(file.filename):
            filename = secure_filename(file.filename)
            upload_folder = os.path.join(current_app.root_path, 'uploads')  # Save files to 'app/uploads'
            os.makedirs(upload_folder, exist_ok=True)  # Ensure the folder exists
            filepath = os.path.join(upload_folder, filename)
            file.save(filepath)

            new_file = File(
                user_id=current_user.id,
                filename=filename,
                filepath=filepath,
                file_size=os.path.getsize(filepath)
            )
            db.session.add(new_file)
            db.session.commit()

            flash('File uploaded successfully', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid file type', 'danger')

    return render_template('upload.html')

# Login route
@main.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first()

        # Changed this line to use check_password() method
        if user and user.check_password(password):
            login_user(user)
            flash('Logged in successfully.', 'success')
            return redirect(url_for('main.index'))
        else:
            flash('Invalid username or password.', 'danger')

    return render_template('login.html')

# Logout route
@main.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully', 'success')
    return redirect(url_for('main.login'))

# Test route
@main.route('/test')
def test():
    return "Test route is working!"

# Favicon route
@main.route('/favicon.ico')
def favicon():
    return send_from_directory(
        os.path.join(current_app.root_path, 'static'),
        'favicon.ico',
        mimetype='image/vnd.microsoft.icon'
    )

# Error handler for forbidden access
@main.errorhandler(403)
def forbidden(e):
    return render_template('403.html'), 403

# Error handler for page not found
@main.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404
