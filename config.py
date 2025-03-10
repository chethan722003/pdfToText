import os 

class Config:
    SECRET_KEY = 'os.urandom(24)'

    # Database Configuration
    SQLALCHEMY_DATABASE_URI = "postgresql://postgres:Jeevan@localhost:5433/flaskapi"
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # File Upload Config (Separate Folders)
    BASE_UPLOAD_FOLDER = os.path.abspath(os.path.join(os.getcwd(), "uploads"))  
    PDF_UPLOAD_FOLDER = os.path.join(BASE_UPLOAD_FOLDER, "pdf")
    IMAGE_UPLOAD_FOLDER = os.path.join(BASE_UPLOAD_FOLDER, "images")

    MAX_CONTENT_LENGTH = 50 * 1024 * 1024  # 50MB max file size

    # Ensure upload folders exist
    for folder in [PDF_UPLOAD_FOLDER, IMAGE_UPLOAD_FOLDER]:
        if not os.path.exists(folder):
            os.makedirs(folder)
