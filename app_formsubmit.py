import logging
from flask import Flask, request, jsonify, render_template_string, send_from_directory
import jwt
from datetime import datetime, timedelta
from werkzeug.security import check_password_hash, generate_password_hash
from werkzeug.utils import secure_filename
from flask import render_template
from quotes import movie_quotes
import pytz
import os
import sqlite3
conn = sqlite3.connect('db.sqlite', check_same_thread=False)
cursor = conn.cursor()

# --- Custom Formatter for IST Timezone ---
class ISTFormatter(logging.Formatter):
    converter = lambda *args: datetime.now(pytz.timezone('Asia/Kolkata')).timetuple()

# Logging setup with IST time
formatter = ISTFormatter(
    fmt='%(asctime)s - %(levelname)s - %(message)s',
    datefmt='%Y-%m-%d %H:%M:%S'
)

file_handler = logging.FileHandler("app.log")
file_handler.setFormatter(formatter)

stream_handler = logging.StreamHandler()
stream_handler.setFormatter(formatter)

logging.basicConfig(level=logging.INFO, handlers=[file_handler, stream_handler])

# --- Flask App Setup ---
app = Flask(__name__)
app.secret_key = 'your-secret-key'  # Change this to a secure key

@app.route('/favicon.ico')
def favicon():
    return send_from_directory('.', 'favicon.ico', mimetype='image/vnd.microsoft.icon')

# Upload configuration
UPLOAD_FOLDER = 'uploads'
ALLOWED_EXTENSIONS = {'txt', 'pdf', 'png', 'jpg', 'jpeg', 'gif'}
MAX_CONTENT_LENGTH = 1 * 1024 * 1024  # 1 MB

app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

# In-memory databases (for CTF/demo purposes)
# users_db = {}          # username: password
forms_db = {}          # form_id: form_data
user_tokens = {}       # username: jwt_token
request_counter = 0

@app.route('/home/ikajakam/lab/poc/<path:filename>')
def serve_custom_static(filename):
    return send_from_directory('/home/ikajakam/lab/poc', filename)

# Log all incoming requests
@app.before_request
def log_request_info():
    global request_counter
    request_counter += 1

    ip_address = request.headers.get('X-Forwarded-For', request.remote_addr)
    method = request.method
    url = request.url
    referrer = request.referrer or 'None'
    user_agent = request.user_agent.string or 'None'
    query_params = dict(request.args)

    try:
        if request.is_json:
            body = request.get_json()
        else:
            body = request.form.to_dict()
    except Exception:
        body = "Could not parse body"

    logging.info("=================================================================================================")
    logging.info(f" x x x x x  New Request {request_counter} x x x x x")
    logging.info(f"IP          : {ip_address}")
    logging.info(f"Method      : {method}")
    logging.info(f"URL         : {url}")
    logging.info(f"Referrer    : {referrer}")
    logging.info(f"User-Agent  : {user_agent}")
    logging.info(f"Query Params: {query_params}")
    logging.info(f"Body        : {body}")
    logging.info("=================================================================================================")

# JWT token generator
def generate_token(username):
    expiration = datetime.utcnow() + timedelta(hours=13)
    return jwt.encode({"username": username, "exp": expiration}, app.secret_key, algorithm="HS256")

# File extension validator
def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

# 1. Register
@app.route('/api/register', methods=['POST'])
def register():
    data = request.json
    username = data.get('username')
    password = data.get('password')

    if not username or not password:
        return jsonify({"error": "Username and password required"}), 400

    conn = sqlite3.connect('db.sqlite')
    cursor = conn.cursor()

    # Check if user already exists
    cursor.execute("SELECT id FROM users WHERE username = ?", (username,))
    existing = cursor.fetchone()
    if existing:
        conn.close()
        return jsonify({"error": "User already exists!"}), 400

    hashed_password = generate_password_hash(password)
    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    user_id = cursor.lastrowid
    conn.commit()
    conn.close()

    return jsonify({"message": "User registered successfully!", "user_id": user_id}), 201

# 2. Login
@app.route('/api/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        username = data.get('username', '')
        password = data.get('password', '')

        if not username or not password:
            return jsonify({"error": "Username and password are required!"}), 400

        # 🔐 Always validate from SQLite
        conn = sqlite3.connect('db.sqlite')
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()

        if result:
            user_id, stored_hash = result
            if check_password_hash(stored_hash, password):
                token = generate_token(username)
                return jsonify({"token": token, "user_id": user_id}), 200
            else:
                return jsonify({"error": "Invalid credentials!"}), 401
        else:
            return jsonify({"error": "Invalid credentials!"}), 401

        # 🔍 Fallback to SQLite with hashed check
        conn = sqlite3.connect('db.sqlite')
        cursor = conn.cursor()
        cursor.execute("SELECT id, password FROM users WHERE username = ?", (username,))
        result = cursor.fetchone()
        conn.close()

        if result:
            user_id, stored_hash = result
            logging.info(f"[DEBUG] user_id={user_id}, username={username}, DB hash={stored_hash}, Password input={password}")

            if check_password_hash(stored_hash, password):
                token = generate_token(username)
                return jsonify({"token": token, "user_id": user_id}), 200
            else:
                return jsonify({"error": "Invalid credentials!"}), 401

                token = generate_token(username)
                return jsonify({"token": token, "user_id": user_id}), 200
        else:
            return jsonify({"error": "Invalid credentials!"}), 401

    except Exception as e:
        logging.error(f"Login Error: {e}")
        return jsonify({"error": "Internal server error"}), 500

# 3. Submit form (allows ?id=0 to be used)
from flask import request, jsonify, Response
from urllib.parse import parse_qs
import random
import json

# Example user token storage (you must define this)
user_tokens = {
    "attacker": "your_jwt_token_here"
}

# Example form storage (in-memory)
forms_db = {}

@app.route('/api/form', methods=['POST'])
def submit_form():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Unauthorized"}), 401

    token = auth_header.split(' ')[1]
    if token not in user_tokens.values():
        return jsonify({"error": "Unauthorized"}), 401

    raw_query = request.query_string.decode()
    parsed_query = parse_qs(raw_query)
    raw_id_list = parsed_query.get('id')
    form_id_str = raw_id_list[0] if raw_id_list else None

    if form_id_str is not None and form_id_str.isdigit():
        form_id = int(form_id_str)

        if form_id == 0 and 'id=0' in raw_query:
            return jsonify({"error": "Form ID 0 is not allowed in plain form!"}), 403

        if form_id == 0:
            data = request.json
            forms_db[form_id] = data    
            selected_quote = random.choice(movie_quotes).strip()
            selected_quote = selected_quote.replace("’", "'")
            response_data = {
                "flag": selected_quote.lower(),
                "form?id=0": "success"
            }
            return Response(
                json.dumps(response_data, indent=2, ensure_ascii=False) + "\n",
                status=201,
                mimetype='application/json'
            )

    # Auto-increment form ID
    form_id = 1 if not forms_db else max(forms_db.keys()) + 1
    data = request.json
    forms_db[form_id] = data
    return jsonify({"message": "Form submitted successfully!", "form_id": form_id}), 201

# Disable PUT for /api/form?id=0
@app.route('/api/form', methods=['PUT'])
def update_form():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Unauthorized"}), 401

    token = auth_header.split(' ')[1]
    if token not in user_tokens.values():
        return jsonify({"error": "Unauthorized"}), 401

    raw_query = request.query_string.decode()
    parsed_query = parse_qs(raw_query)
    raw_id_list = parsed_query.get('id')
    form_id_str = raw_id_list[0] if raw_id_list else None

    if form_id_str == "0":
        return jsonify({"error": "PUT method is not allowed for form ID 0"}), 403

    # Proceed normally for other form IDs
    if form_id_str is not None and form_id_str.isdigit():
        form_id = int(form_id_str)
        data = request.json
        forms_db[form_id] = data
        return jsonify({"message": "Form updated successfully - Flag Acquired!"}), 200

    return jsonify({"error": "Invalid form ID"}), 400

# 4. View or Edit Form (IDOR + XSS via message field)
@app.route('/api/form', methods=['GET', 'PUT', 'DEL'])
def handle_form():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Unauthorized"}), 401

    token = auth_header.split(' ')[1]
    if token not in user_tokens.values():
        return jsonify({"error": "Unauthorized"}), 401

    form_id = request.args.get('id')
    if not form_id or not form_id.isdigit() or int(form_id) not in forms_db:
        return jsonify({"error": "Form not found"}), 404

    form_id = int(form_id)

    if request.method == 'GET':
        return jsonify(forms_db[form_id]), 200

    elif request.method == 'PUT':
        forms_db[form_id] = request.json
        return jsonify({"message": "Form updated successfully - Flag Acquired!"}), 200

# 5. Upload file endpoint
@app.route('/api/upload', methods=['POST'])
def upload_file():
    auth_header = request.headers.get('Authorization')
    if not auth_header or not auth_header.startswith('Bearer '):
        return jsonify({"error": "Unauthorized"}), 401

    token = auth_header.split(' ')[1]
    if token not in user_tokens.values():
        return jsonify({"error": "Unauthorized"}), 401

    if 'file' not in request.files:
        return jsonify({"error": "No file part in request"}), 400

    file = request.files['file']

    if file.filename == '':
        return jsonify({"error": "No selected file"}), 400

    if file and allowed_file(file.filename):
        filename = secure_filename(file.filename)
        file_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        file.save(file_path)
        logging.info(f"File uploaded: {filename} by token: {token}")
        return jsonify({"message": "File uploaded successfully", "filename": filename}), 201
    else:
        return jsonify({"error": "Invalid file type"}), 400

# 6. Serve uploaded files (optional)
@app.route('/uploads/<filename>')
def uploaded_file(filename):
    return send_from_directory(app.config['UPLOAD_FOLDER'], filename)

# 7. Root route: CTF instructions
@app.route('/')
def index():
    return render_template("index.html")

# 8. Render stored XSS
@app.route('/view-form')
def view_form():
    form_id = request.args.get('id')
    if not form_id or not form_id.isdigit() or int(form_id) not in forms_db:
        return "Form not found", 404

    form_data = forms_db[int(form_id)]
    message = form_data.get('message', '') if isinstance(form_data, dict) else ''

    html_template = """
    <html>
        <head><title>View Form</title></head>
        <body>
            <h2>Form ID: {{ form_id }}</h2>
            <pre>{{ form_data }}</pre>
            <p>Message: {{ message|safe }}</p> <!-- XSS renders here -->
        </body>
    </html>
    """
    return render_template_string(html_template, form_id=form_id, form_data=form_data, message=message)

@app.route('/api/change-password', methods=['POST'])
def change_password():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({"error": "Unauthorized"}), 401

        token = auth_header.split(' ')[1]
        try:
            payload = jwt.decode(token, app.secret_key, algorithms=["HS256"])
        except jwt.ExpiredSignatureError:
            return jsonify({"error": "Token expired"}), 401
        except jwt.InvalidTokenError:
            return jsonify({"error": "Invalid token"}), 401

        changer = payload.get("user_id")
        logging.info(f"[!] Password change requested by {changer}")

        data = request.get_json()
        target_user_id = data.get("user_id")
        raw_password = data.get("new_password")

        if not target_user_id or not raw_password:
            return jsonify({"error": "User ID and new password required"}), 400

        hashed_password = generate_password_hash(raw_password)
        conn = sqlite3.connect('db.sqlite')
        cursor = conn.cursor()
        # ⚠️ VULNERABLE TO SQLi – for CTF/demo purposes only
        query = f"UPDATE users SET password = '{hashed_password}' WHERE id = {target_user_id}"
        logging.warning(f"[SQLi DEBUG] Executing query: {query}")
        cursor.execute(query)
        conn.commit()
        conn.close()

        return jsonify({
            "message": f"Password changed for user ID {target_user_id}",
            "flag": "flag{idor_or_sqli_found}"
        }), 200

    except Exception as e:
        logging.error(f"Password Change Error: {e}")
        return jsonify({"error": "Internal server error"}), 500

if __name__ == '__main__':
    app.run(host='127.0.0.1', port=5000, debug=True)

    # updated 13/7/25
