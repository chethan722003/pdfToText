import os
from flask import Flask, render_template, redirect, url_for, request, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, UserMixin, login_user, login_required, logout_user, current_user
from flask_wtf import FlaskForm
from wtforms import StringField, PasswordField
from wtforms.validators import DataRequired, Email, Length
from flask_bcrypt import Bcrypt
import fitz  # PyMuPDF for PDF text extraction
from forms import UploadForm  # ✅ Make sure this line is present
from werkzeug.utils import secure_filename



app = Flask(__name__)
app.config['SECRET_KEY'] = 'os.urandom(24)'
app.config['SQLALCHEMY_DATABASE_URI'] = "postgresql://postgres:Jeevan@localhost:5433/flaskapi"
app.config['UPLOAD_FOLDER'] = 'uploads/'
app.config['MAX_CONTENT_LENGTH'] = 50 * 1024 * 1024  # 50MB max file size

db = SQLAlchemy(app)
bcrypt = Bcrypt(app)
login_manager = LoginManager(app)
login_manager.login_view = 'login'

# User Model for Authentication
class User(UserMixin, db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100))
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False)
    files = db.relationship('File', backref='owner', lazy=True)

# File Model for storing uploaded PDF and extracted text
class File(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, db.ForeignKey('user.id'), nullable=False)
    filename = db.Column(db.String(255), nullable=False)
    file_path = db.Column(db.String(255), nullable=False)
    extracted_text = db.Column(db.Text)
    created_at = db.Column(db.DateTime, default=db.func.current_timestamp())

def extract_text_from_pdf(file_path):
    try:
        document = fitz.open(file_path)
        text = ""
        for page_num in range(len(document)):
            page = document.load_page(page_num)
            text += page.get_text("text") + "\n"
        return text
    except Exception as e:
        print(f"❌ Error extracting text: {str(e)}")
        return "⚠️ Error extracting text from PDF."


# Forms for Registration and Login
class RegistrationForm(FlaskForm):
    name = StringField('Name', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired(), Length(min=6)])

class LoginForm(FlaskForm):
    email = StringField('Email', validators=[DataRequired(), Email()])
    password = PasswordField('Password', validators=[DataRequired()])

# User loader for Flask-Login
@login_manager.user_loader
def load_user(user_id):
    return User.query.get(int(user_id))

# Home Route
@app.route('/')
def home():
    return render_template('home.html')

# Register Route
@app.route('/register', methods=['GET', 'POST'])
def register():
    form = RegistrationForm()
    
    if form.validate_on_submit():
        print("✅ Form validation passed!")

        existing_user = User.query.filter_by(email=form.email.data.lower()).first()
        if existing_user:
            flash('⚠️ Email already registered. Please log in.', 'warning')
            print("⚠️ Email already exists:", existing_user.email)
            return redirect(url_for('login'))
        
        hashed_password = bcrypt.generate_password_hash(form.password.data).decode('utf-8')
        new_user = User(name=form.name.data, email=form.email.data.lower(), password=hashed_password)

        try:
            db.session.add(new_user)
            db.session.commit()
            print("✅ User created:", new_user.email)

            flash('✅ Account created successfully! Please log in.', 'success')
            return redirect(url_for('login'))  # Should redirect here
        except Exception as e:
            db.session.rollback()
            print(f'❌ Database Error: {str(e)}')
            flash(f'Error creating account: {str(e)}', 'danger')

    else:
        print("❌ Form validation failed:", form.errors)
    
    return render_template('register.html', form=form)

@app.route('/login', methods=['GET', 'POST'])
def login():
    form = LoginForm()
    if form.validate_on_submit():
        print(f"✅ Login form submitted with: {form.email.data}")  # Debugging
        user = User.query.filter_by(email=form.email.data.lower()).first()

        if user:
            print(f"🔍 User found: {user.email}")  # Debugging

        if user and bcrypt.check_password_hash(user.password, form.password.data):
            login_user(user)
            flash('✅ Login successful!', 'success')
            print(f"✅ User logged in: {user.email}")  # Debugging
            return redirect(url_for('dashboard'))
        else:
            flash('⚠️ Invalid email or password.', 'danger')
            print("❌ Login failed: Invalid credentials")  # Debugging

    else:
        print(f"❌ Form validation failed: {form.errors}")  # Debugging
    
    return render_template('login.html', form=form)



# Dashboard Route (Authenticated)
@app.route('/dashboard')
@login_required
def dashboard():
    files = File.query.filter_by(user_id=current_user.id).all()
    return render_template('dashboard.html', name=current_user.name, files=files)
ALLOWED_EXTENSIONS = {'pdf'}

def allowed_file(filename):
    """Check if the file extension is PDF."""
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

@app.route('/upload', methods=['GET', 'POST'])
@login_required
def upload():
    form = UploadForm()
    
    if form.validate_on_submit():
        file = form.pdf_file.data  
        
        # Check file type
        if not allowed_file(file.filename):
            flash('⚠️ Invalid file type! Only PDF files are allowed.', 'danger')
            return redirect(url_for('upload'))

        # Check file size
        file.seek(0, os.SEEK_END)  # Move to end of file
        file_length = file.tell()  # Get file size
        file.seek(0)  # Reset file pointer

        if file_length > 50 * 1024 * 1024:  # 50MB limit
            flash('⚠️ File is too large! Maximum size allowed is 50MB.', 'danger')
            return redirect(url_for('upload'))
        
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)

        # Extract text
        extracted_text = extract_text_from_pdf(file_path)

        # Save file details in DB
        new_file = File(user_id=current_user.id, filename=filename, file_path=file_path, extracted_text=extracted_text)
        db.session.add(new_file)
        db.session.commit()

        flash('✅ File uploaded and processed successfully!', 'success')
        return redirect(url_for('dashboard'))
    
    return render_template('upload.html', form=form)


@app.route('/extract_text', methods=['GET', 'POST'])
@login_required
def extract_text():
    file_id = request.args.get('file_id') if request.method == 'GET' else request.form.get('file_id')

    if not file_id:
        flash('⚠️ No file ID provided.', 'danger')
        return redirect(url_for('dashboard'))

    file = File.query.get(file_id)

    if not file or file.user_id != current_user.id:
        flash('⚠️ Invalid file.', 'danger')
        return redirect(url_for('dashboard'))

    # Extract text if not already extracted
    if not file.extracted_text:
        file.extracted_text = extract_text_from_pdf(file.file_path)
        db.session.commit()

    flash('✅ Text extracted successfully!', 'success')
    return render_template('extracted_text.html', text=file.extracted_text, file=file)  # ✅ Pass file




# Logout Route
@app.route('/logout')
@login_required
def logout():
    logout_user()
    flash('Logged out successfully.', 'info')
    return redirect(url_for('login'))


if __name__ == '__main__':
    with app.app_context():
        db.create_all()  # Ensure tables are created before running
    app.run(debug=True)
