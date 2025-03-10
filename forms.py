from flask_wtf import FlaskForm
from flask_wtf.file import FileField, FileRequired, FileAllowed

class UploadForm(FlaskForm):
    pdf_file = FileField('Upload PDF', validators=[
        FileRequired(),
        FileAllowed(['pdf'], '⚠️ Invalid file type! Only PDF files are allowed.')
    ])
