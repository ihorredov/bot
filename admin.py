import os
from flask import Flask, render_template, request, redirect, url_for, send_file, session
from functools import wraps
from werkzeug.security import check_password_hash, generate_password_hash
import zipfile
from io import BytesIO

app = Flask(__name__)
app.secret_key = os.getenv('FLASK_SECRET_KEY', 'your-secret-key-here')  # Change in production

# Admin credentials (in production, use a database)
ADMIN_USERNAME = 'admin'
ADMIN_PASSWORD = generate_password_hash('admin123')  # Change in production

def login_required(f):
    @wraps(f)
    def decorated_function(*args, **kwargs):
        if 'logged_in' not in session:
            return redirect(url_for('login'))
        return f(*args, **kwargs)
    return decorated_function

@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form.get('username')
        password = request.form.get('password')
        
        if username == ADMIN_USERNAME and check_password_hash(ADMIN_PASSWORD, password):
            session['logged_in'] = True
            return redirect(url_for('dashboard'))
        return 'Invalid credentials'
    
    return render_template('login.html')

@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    return redirect(url_for('login'))

@app.route('/')
@login_required
def dashboard():
    participants_data = []
    documents_dir = 'documents'
    
    # Read all user folders
    for user_id in os.listdir(documents_dir):
        user_folder = os.path.join(documents_dir, user_id)
        if os.path.isdir(user_folder):
            user_data = {}
            # Read user_data.txt
            try:
                with open(os.path.join(user_folder, 'user_data.txt'), 'r', encoding='utf-8') as f:
                    lines = f.readlines()
                    for line in lines:
                        if ':' in line:
                            key, value = line.strip().split(':', 1)
                            user_data[key.strip()] = value.strip()
                user_data['id'] = user_id
                participants_data.append(user_data)
            except FileNotFoundError:
                continue
    
    return render_template('dashboard.html', participants=participants_data)

@app.route('/documents/<user_id>/<filename>')
@login_required
def get_document(user_id, filename):
    file_path = os.path.join('documents', user_id, filename)
    if os.path.exists(file_path):
        return send_file(file_path)
    return 'File not found', 404

@app.route('/download-all')
@login_required
def download_all():
    memory_file = BytesIO()
    with zipfile.ZipFile(memory_file, 'w', zipfile.ZIP_DEFLATED) as zipf:
        for root, dirs, files in os.walk('documents'):
            for file in files:
                file_path = os.path.join(root, file)
                arcname = os.path.relpath(file_path, 'documents')
                zipf.write(file_path, arcname)
    
    memory_file.seek(0)
    return send_file(
        memory_file,
        mimetype='application/zip',
        as_attachment=True,
        download_name='all_documents.zip'
    )

if __name__ == '__main__':
    app.run(debug=True, port=5000, host='0.0.0.0')