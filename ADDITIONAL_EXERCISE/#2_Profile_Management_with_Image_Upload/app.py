# Step 1: Import necessary libraries and modules
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from werkzeug.security import generate_password_hash, check_password_hash

# Step 2: Import forms and models
from forms import LoginForm, RegistrationForm, ProfileForm
from models import db, User, Student

import os

# Step 3: Initialize Flask app with instance-relative config
app = Flask(__name__, instance_relative_config=True)

# Step 4: Debug logs for development (Optional)
current_working_directory = os.getcwd()
static_folder_path = app.static_folder
print(f"DEBUG: Current working directory (os.getcwd()): {current_working_directory}")
print(f"DEBUG: Flask static folder (app.static_folder): {static_folder_path}")
print(f"DEBUG: Does static folder exist at app.static_folder? {os.path.isdir(static_folder_path)}")
css_file_path = os.path.join(static_folder_path, 'css', 'style.css')
image_file_path = os.path.join(static_folder_path, 'images', 'TUP.png')
print(f"DEBUG: Expected style.css path: {css_file_path}")
print(f"DEBUG: Does style.css exist at expected path? {os.path.exists(css_file_path)}")
print(f"DEBUG: Expected TUP.png path: {image_file_path}")
print(f"DEBUG: Does TUP.png exist at expected path? {os.path.exists(image_file_path)}")

# Step 5: Configuration settings for secret key and database URI
app.config['SECRET_KEY'] = 'my-secret-key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///' + os.path.join(app.instance_path, 'app.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['UPLOAD_FOLDER'] = os.path.join(app.root_path, 'static/uploads')
os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True) # Automatically ensures path arrays exist

# Step 6: Initialize database and login manager
db.init_app(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login' # redirect to login if unauthorized

# Step 7: User loader function required by Flask-Login
@login_manager.user_loader
def load_user(user_id):
 return User.query.get(int(user_id))

# Step 8: Define app routes


@app.route('/dashboard', methods=['GET', 'POST'])
@login_required
def dashboard():
    form = ProfileForm()
    
    if form.validate_on_submit():
        # Isolating updates securely using current_user configuration structures
        if form.profile_picture.data:
            file = form.profile_picture.data
            # Sanitize file string input to counter injection payloads
            clean_name = secure_filename(file.filename)
            # Append owner primary ID index to prevent matching file name overrides
            unique_filename = f"user_{current_user.id}_{clean_name}"
            
            target_destination = os.path.join(app.config['UPLOAD_FOLDER'], unique_filename)
            file.save(target_destination)
            
            # Commit targeted name to current tracking model parameters row
            current_user.image_filename = unique_filename
            
        current_user.display_name = form.display_name.data
        db.session.commit()
        flash('Profile changes successfully updated!')
        return redirect(url_for('dashboard'))
        
    elif request.method == 'GET':
        form.display_name.data = current_user.display_name
        
    return render_template('dashboard.html', form=form)


# Home route
@app.route('/')
def home():
    return render_template('home.html')
# About page
@app.route('/about')
def about():
    return render_template('about.html')
# Contact page
@app.route('/contact')
def contact():
    return render_template('contact.html')


# Register new user
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    if form.validate_on_submit():
        existing_user = User.query.filter_by(email=form.email.data).first()
        if existing_user:
            flash('Email already registered.')
            return redirect(url_for('register'))
        
        hashed_pw = generate_password_hash(form.password.data)
        # Clean copy: no role parameter here!
        new_user = User(email=form.email.data, password=hashed_pw)
        
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful!')
        return redirect(url_for('login'))
    else:
        print("EXERCISE 2 ERRORS:", form.errors)
    return render_template('register.html', form=form)



# Login existing user
@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        user = User.query.filter_by(email=form.email.data).first()
        if user and check_password_hash(user.password, form.password.data):
            login_user(user)
            flash("Logged in successfully.")
            return redirect(url_for('students'))
        else:
            flash("Invalid email or password.")
    return render_template('login.html', form=form)
# Logout user
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash("You have been logged out.")
    return redirect(url_for('home'))
# Display all students
@app.route('/students')
@login_required
def students():
    student_list = Student.query.order_by(Student.full_name).all()
    return render_template('students.html', students=student_list)
# Add new student
@app.route('/add-student', methods=['POST'])
@login_required
def add_student():
    name = request.form['name']
    email = request.form['email']
    student = Student(full_name=name, email=email)
    db.session.add(student)
    db.session.commit()
    return redirect(url_for('students'))
# Delete a student
@app.route('/delete-student/<int:id>')
@login_required

def delete_student(id):
    student = Student.query.get_or_404(id)
    db.session.delete(student)
    db.session.commit()
    return redirect(url_for('students'))

# Add 404 Error Handler to app.py
@app.errorhandler(404)
def page_not_found(e):
    return render_template('404.html'), 404

# Step 9: Run the application and create the database if not yet created
if __name__ == '__main__':
    if not os.path.exists(os.path.join(app.instance_path, 'app.db')):
        os.makedirs(app.instance_path, exist_ok=True)
        with app.app_context():
            db.create_all()
    app.run(debug=True)