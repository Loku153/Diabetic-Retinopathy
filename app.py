from flask import Flask, render_template, request, redirect, url_for, session, flash
from tensorflow.keras.models import load_model
from tensorflow.keras.preprocessing import image
from werkzeug.utils import secure_filename
from flask import current_app
from flask import jsonify
from PIL import Image
from reportlab.pdfgen import canvas
from datetime import datetime
from chatbot import EyeCareChatbot
import numpy as np
import os
import sqlite3

app = Flask(__name__)
app.secret_key = 'supersecretkey'
app.config['UPLOAD_FOLDER'] = 'static/uploads'
bot = EyeCareChatbot()

# Set a maximum file size limit (optional)
app.config['MAX_CONTENT_LENGTH'] = 16 * 1024 * 1024  # 16MB limit

ALLOWED_EXTENSIONS = {'pdf', 'jpg', 'jpeg', 'png', 'txt'}

def allowed_file(filename):
    return '.' in filename and filename.rsplit('.', 1)[1].lower() in ALLOWED_EXTENSIONS

def get_db_connection():
    conn = sqlite3.connect("users.db")
    conn.row_factory = sqlite3.Row
    return conn


# Load model
model = load_model(r"C:\Users\Lokesh\OneDrive\Desktop\Vision-Care-AI-2\Vision-Care-AI\models\densenet_dr_multiclass.h5")
class_labels = ['Mild', 'Moderate', 'No_DR', 'Proliferative_DR', 'Severe']

# Create DB and tables
def init_db():
    with sqlite3.connect('users.db') as conn:
        cursor = conn.cursor()
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS doctors (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                email TEXT,
                designation TEXT,
                hospital TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS patients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL UNIQUE,
                password TEXT NOT NULL,
                email TEXT,
                height INTEGER,
                weight INTEGER,
                age INTEGER,
                gender TEXT
            )
        ''')
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS reports (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT NOT NULL,
                age INTEGER,
                gender TEXT,
                prediction_result TEXT,
                confidence REAL,
                report_path TEXT,
                timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        cursor.execute('''CREATE TABLE IF NOT EXISTS forms (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            patient_username TEXT,
            doctor_username TEXT,
            message TEXT,
            status TEXT,
            report_path TEXT,
            submission_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(patient_username) REFERENCES patients(username),
            FOREIGN KEY(doctor_username) REFERENCES doctors(username)
        )''')

        print("Database and tables created successfully.")

init_db()

@app.route("/")
def home():
    return render_template("index.html")


# Add these routes to your app.py
@app.route('/chatbot', methods=['GET', 'POST'])
def chatbot():
    if request.method == 'POST':
        user_input = request.form.get('user_input')
        response = bot.chat(user_input)
        return jsonify({'response': response})
    
    # Pass the initial greeting to the template
    initial_greeting = bot.greet()
    return render_template('chatbot.html', initial_greeting=initial_greeting)

@app.route('/get_chat_response', methods=['POST'])
def get_chat_response():
    try:
        data = request.get_json()
        user_input = data.get('user_input', '')
        print(f"Received input: '{user_input}'")
        
        # Ensure the bot instance exists and is properly initialized
        if not hasattr(bot, 'conversation_history'):
            bot.conversation_history = []
            
        response = bot.chat(user_input)
        print(f"Generated response: '{response}'")
        
        return jsonify({
            'status': 'success',
            'response': response
        })
    except Exception as e:
        print(f"Error in get_chat_response: {str(e)}")
        return jsonify({
            'status': 'error',
            'message': str(e),
            'response': "I'm sorry, I encountered an error. Please try again."
        })


# ---------------- PREDICT ----------------
@app.route("/predict", methods=["GET", "POST"])
def predict():
    prediction = None
    confidence = None
    image_url = None
    report_url = None
    username = session.get("username")

    if request.method == "POST":
        file = request.files["image"]
        if file:
            filepath = os.path.join(app.config['UPLOAD_FOLDER'], file.filename)
            file.save(filepath)

            img = Image.open(filepath).convert("RGB")
            img = img.resize((224, 224))
            img_array = image.img_to_array(img)
            img_array = np.expand_dims(img_array, axis=0)
            img_array /= 255.0

            predictions = model.predict(img_array)
            predicted_index = np.argmax(predictions[0])
            prediction = class_labels[predicted_index]
            confidence = float(predictions[0][predicted_index]) * 100
            image_url = url_for('static', filename='uploads/' + file.filename)

            # Fetch age and gender from database
            age = gender = "N/A"
            with sqlite3.connect("users.db") as conn:
                cursor = conn.cursor()
                cursor.execute("SELECT age, gender FROM patients WHERE username = ?", (username,))
                user_data = cursor.fetchone()
                if user_data:
                    age, gender = user_data

            # Generate PDF report
            report_path = os.path.join(app.config['UPLOAD_FOLDER'], f"{username}_report.pdf")
            c = canvas.Canvas(report_path)
            c.setFont("Helvetica-Bold", 16)
            c.drawString(100, 800, "Diabetic Retinopathy Report")
            c.setFont("Helvetica", 12)
            c.drawString(100, 770, f"Patient Name: {username}")
            c.drawString(100, 750, f"Age: {age}")
            c.drawString(100, 730, f"Gender: {gender}")
            c.drawString(100, 710, f"Date: {datetime.now().strftime('%d %B %Y')}")
            c.drawString(100, 690, f"Diagnosis: {prediction.replace('_', ' ')}")
            c.drawString(100, 450, f"Confidence: {confidence:.2f}%")
            # Add retina image to the report
            try:
                retina_image_path = img  # Path to the uploaded retina image
                c.drawImage(retina_image_path, 100, 500, width=200, height=200)  # Adjust position and size as needed
            except Exception as e:
                print(f"Error adding retina image to PDF: {e}")
            
            c.save()

            # Make report available to download
            report_url = url_for('static', filename='uploads/' + f"{username}_report.pdf")

            # Insert report data into the database
            with sqlite3.connect("users.db") as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO reports (username, age, gender, prediction_result, confidence, report_path)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (username, age, gender, prediction, confidence, report_path))
                conn.commit()

            return render_template("predict.html", prediction=prediction, confidence=confidence,
                                   image_url=image_url, report_url=report_url, username=username)

    return render_template("predict.html", prediction=prediction, confidence=confidence,
                           image_url=image_url, report_url=report_url, username=username)


# ---------------- SIGNUP ----------------
@app.route('/signup')
def signup_page():
    return render_template("mainsignup.html")

# ---------------- LOGIN ----------------
@app.route('/login')
def login_page():
    return render_template("login.html")

@app.route("/signup/<role>", methods=["GET", "POST"])
def signup(role):
    if request.method == "POST":
        username = request.form["username"]
        email = request.form["email"]
        password = request.form["password"]
        conformpassword = request.form["confirmpassword"]
        if role == 'doctor':
            designation = request.form["designation"]
            hospital = request.form["hospital"]
        else:
            height = request.form["height"]
            weight = request.form["weight"]
            age = request.form["age"]
            gender=request.form['gender']
        table = 'doctors' if role == 'doctor' else 'patients'

        if password != conformpassword:
            flash("Passwords do not match!", "danger")
            return redirect(url_for("signup", role=role))
        
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            try:
                if role == 'doctor':
                    cursor.execute(f"INSERT INTO {table} (username, password,email,designation,hospital) VALUES (?, ?,?,?,?)", (username, password,email,designation,hospital))
                else:
                    cursor.execute(f"INSERT INTO {table} (username, password,email,height,weight,age,gender) VALUES (?, ?,?,?,?,?,?)", (username, password,email,height,weight,age,gender))
                conn.commit()
                flash("Signup successful!", "success")
                return redirect(url_for("login", role=role))
            except sqlite3.IntegrityError:
                flash("Username already exists!", "danger")
    
    return render_template(f"{role}.html", role=role)

# ---------------- LOGIN ----------------
@app.route("/login/<role>", methods=["GET", "POST"])
def login(role):
    if request.method == "POST":
        username = request.form["username"]
        password = request.form["password"]
        table = 'doctors' if role == 'doctor' else 'patients'

        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute(f"SELECT * FROM {table} WHERE username = ? AND password = ?", (username, password))
            user = cursor.fetchone()

            if user:
                session["username"] = username
                session["role"] = role
                if role == 'doctor':
                    flash("Login successful!", "info")
                    return redirect(url_for("doctor_dashboard"))
                else:
                    flash("Login successful!", "info")
                    return redirect(url_for("patient_dashboard"))
            else:
                flash("Invalid credentials!", "danger")

    return render_template(f'login-{role}.html')


# ---------------- DASHBOARD ----------------
@app.route("/doctor_dashboard")
def doctor_dashboard():
    username = session.get("username")

    if username and session["role"] == "doctor":
        # Fetch all consultation forms for the logged-in doctor
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM forms WHERE doctor_username = ?", (username,))
            forms = cursor.fetchall()

        return render_template("doctor_dashboard.html", forms=forms, username=username)
    else:
        flash("You need to log in first!", "danger")
        return redirect(url_for("login_page"))

@app.route("/patient_dashboard")
def patient_dashboard():
    if "username" in session and session["role"] == 'patient':
        return render_template("patient-dashboard.html", username=session["username"])
    else:
        flash("You need to log in first!", "danger")
        return redirect(url_for("login_page"))
    

# ---------------- VIEW REPORTS ----------------
@app.route("/reports")
def reports():
    username = session.get("username")
    
    # If user is logged in, fetch their reports
    if username:
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute("SELECT * FROM reports WHERE username = ?", (username,))
            report_data = cursor.fetchall()
        
        # Render the page with the reports data
        return render_template("reports.html", reports=report_data, username=username)
    else:
        flash("You need to log in first!", "danger")
        return redirect(url_for("login_page"))


# ---------------- VIEW FORMS ----------------
@app.route("/doctor_consultation")
def doctor_consultation():
    # Fetch doctor details from the database
    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT username, hospital, designation FROM doctors")
        doctors = cursor.fetchall()

    return render_template("doctor_consultation.html", doctors=doctors)

# ---------------- CONSULT FORMS ----------------
@app.route("/consult_form/<doctor_username>", methods=["GET", "POST"])
def consult_form(doctor_username):
    username = session.get("username")

    if request.method == "POST":
        message = request.form["message"]
        report = request.files.get("report")

        report_path = None
        if report and allowed_file(report.filename):
            filename = secure_filename(report.filename)
            report_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
            report.save(report_path)

        # Insert the form data into the forms table
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO forms (patient_username, doctor_username, message, status, report_path)
                              VALUES (?, ?, ?, ?, ?)''', (username, doctor_username, message, "Pending", report_path))
            conn.commit()

        flash("Your consultation request has been submitted!", "success")
        return redirect(url_for("patient_dashboard"))

    return render_template("consult_form.html", doctor_username=doctor_username)

# Route to handle prescription submission
@app.route('/submit_prescription', methods=['POST'])
def submit_prescription():
    form_id = request.form['form_id']
    prescription = request.form['prescription']

    with sqlite3.connect("users.db") as conn:
        cursor = conn.cursor()
        cursor.execute('UPDATE forms SET prescription = ?, status = ? WHERE id = ?', (prescription, 'Done', form_id))
        conn.commit()

    return redirect(url_for('doctor_dashboard'))

@app.route("/patient_messages")
def patient_messages():
    username = session.get("username")

    if username and session["role"] == 'patient':
        with sqlite3.connect("users.db") as conn:
            cursor = conn.cursor()
            cursor.execute('''
                SELECT forms.id, forms.doctor_username, forms.status, forms.prescription, forms.submission_date
                FROM forms
                WHERE patient_username = ?
                ORDER BY submission_date DESC
            ''', (username,))
            forms = cursor.fetchall()

        return render_template("patient_messages.html", username=username, forms=forms)
    else:
        flash("You need to log in first!", "danger")
        return redirect(url_for("login_page"))

# ---------------- LOGOUT ----------------
@app.route("/logout")
def logout():
    session.clear()
    flash("Logged out successfully.", "info")
    return redirect(url_for("home"))

# ---------------- MAIN ----------------
if __name__ == "__main__":
    os.makedirs(app.config['UPLOAD_FOLDER'], exist_ok=True)
    app.run(debug=True)
