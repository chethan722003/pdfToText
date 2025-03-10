# Flask PDF Upload and Text Extraction Application with Authentication

This is a simple Flask web application that allows users to register, log in, upload PDF files, extract text while maintaining formatting, and display the extracted text. The application includes user authentication and stores the extracted text temporarily.

## Features
- **User Authentication**: Register, login, and logout functionality.
- **PDF Upload**: Users can upload PDF files (max size: 50MB).
- **Text Extraction**: Extracts text from PDFs using `PyMuPDF` (fitz) while preserving basic formatting.
- **Formatted Display**: Extracted text is displayed on a new page.
- **Error Handling**: Alerts for unsupported file types and large files.

## Tech Stack
- **Backend**: Flask (Python 3.8+), Flask-Login, Flask-WTF, Flask-Bcrypt, Flask-SQLAlchemy, PyMuPDF
- **Frontend**: HTML, CSS, JavaScript (Bootstrap optional for styling)
- **Database**: SQLite (default) for storing user credentials
- **Storage**: Local folder for storing uploaded PDF files

## Installation Instructions

### Prerequisites
- Python 3.8+
- `pip` for installing Python packages

### 1. Clone the Repository
Clone this repository to your local machine:

```bash
git clone https://github.com/yourusername/flask-pdf-upload-text-extraction.git
cd flask-pdf-upload-text-extraction
