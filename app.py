from flask import Flask, request, jsonify, render_template, redirect, session
from flask_cors import CORS
import sqlite3
import os
from werkzeug.security import generate_password_hash, check_password_hash
from werkzeug.utils import secure_filename
from predict_advanced import predict_career

app = Flask(__name__)
app.secret_key = "secret123"
CORS(app)

UPLOAD_FOLDER = 'static/uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER

# ensure upload folder exists
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# ================= DATABASE =================
def init_db():
    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # USERS TABLE
    c.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE,
            first_name TEXT,
            last_name TEXT,
            password TEXT,
            profile_pic TEXT
        )
    ''')

    # HISTORY TABLE
    c.execute('''
        CREATE TABLE IF NOT EXISTS history (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT,
            career TEXT,
            score TEXT
        )
    ''')

    conn.commit()
    conn.close()

init_db()

# ================= FRONTEND PAGES =================
@app.route('/')
def home():
    return render_template('font.html')

@app.route('/about')
def about():
    return render_template('about.html')

@app.route('/skill')
def skill():
    return render_template('skill.html')


@app.route('/career_plan')
def career_plan():
    return render_template('career_plan.html')


@app.route('/user_about')
def user_about():
    return render_template('user_about.html')


@app.route('/user_font')
def user_font():
    return render_template('user_font.html')




@app.route('/explore_roles')
def explore_roles():
    return render_template('explore_roles.html')


@app.route('/user_explore_roles')
def User_explore_roles():
    return render_template('User_explore_roles.html')

@app.route('/user_skill')
def user_skill():
    return render_template('user_skill.html')

@app.route('/user_career_plan')
def user_career_plan():
    return render_template('user_career_plan.html')



# ================= REGISTER =================
@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        email = request.form['email']
        first_name = request.form['first_name']
        last_name = request.form['last_name']
        password = request.form['password']
        repeat = request.form['repeat_password']

        if password != repeat:
            return "Passwords do not match ❌"

        hashed_password = generate_password_hash(password)

        conn = sqlite3.connect('users.db')
        c = conn.cursor()

        c.execute("SELECT * FROM users WHERE email=?", (email,))
        if c.fetchone():
            return "Email already exists ❌"

        c.execute(
            "INSERT INTO users (email, first_name, last_name, password) VALUES (?, ?, ?, ?)",
            (email, first_name, last_name, hashed_password)
        )

        conn.commit()
        conn.close()

        return redirect('/login')

    return render_template('register.html')

# ================= LOGIN (WITH ADMIN SUPPORT) =================
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        email = request.form['email']
        password = request.form['password']

        # 1. Check if it is Admin
        # Aap ye email aur password apni marzi se badal sakte hain
        if email == "admin@gmail.com" and password == "admin123":
            session['user'] = email
            session['role'] = 'admin' # Admin role set kiya
            return redirect('/admin')

        # 2. If not admin, check in Database for regular User
        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE email=?", (email,))
        user = c.fetchone()
        conn.close()

        if user and check_password_hash(user[4], password):
            session['user'] = user[1]
            session['role'] = 'user' # Regular user role set kiya
            return redirect('/user_font')

        return "Invalid Email or Password ❌"

    return render_template('login.html')

# ================= PROFILE =================
@app.route('/profile')
def profile():
    if 'user' not in session:
        return redirect('/login')

    email = session['user']

    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # user data
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    user = c.fetchone()

    # history
    c.execute("SELECT career, score FROM history WHERE email=?", (email,))
    history = c.fetchall()

    conn.close()

    return render_template('profile.html', user=user, history=history)

# ================= EDIT PROFILE PAGE =================
@app.route('/edit_profile')
def edit_profile():
    if 'user' not in session:
        return redirect('/login')

    email = session['user']

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=?", (email,))
    user = c.fetchone()
    conn.close()

    return render_template('edit_profile.html', user=user)

# ================= UPDATE PROFILE =================
@app.route('/update_profile', methods=['POST'])
def update_profile():
    if 'user' not in session:
        return redirect('/login')

    email = session['user']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    new_password = request.form.get('password')  

    file = request.files.get('profile_pic')
    filename = None

    if file and file.filename != "":
        filename = secure_filename(file.filename)
        file.save(os.path.join(app.config['UPLOAD_FOLDER'], filename))

    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    # Dynamic SQL query taaki code mess na ho
    query = "UPDATE users SET first_name=?, last_name=?"
    params = [first_name, last_name]

    # Agar user ne nayi profile pic upload ki hai
    if filename:
        query += ", profile_pic=?"
        params.append(filename)
    
    # Agar user ne naya password type kiya hai (khali nahi chhoda)
    if new_password and new_password.strip() != "":
        hashed_password = generate_password_hash(new_password)
        query += ", password=?"
        params.append(hashed_password)

    query += " WHERE email=?"
    params.append(email)

    # Query run karenge
    c.execute(query, tuple(params))
    conn.commit()
    conn.close()

    return redirect('/profile')

# ================= DASHBOARD =================
@app.route('/dashboard')
def dashboard():
    if 'user' not in session:
        return redirect('/login')

    email = session['user']

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT career, score FROM history WHERE email=?", (email,))
    history = c.fetchall()
    conn.close()

    return render_template('dashboard.html', history=history)

# ================= LOGOUT =================
@app.route('/logout')
def logout():
    session.pop('user', None)
    session.pop('role', None) # Role ko bhi session se remove kiya
    return redirect('/login')

# ================= PREDICT =================
@app.route('/predict', methods=['POST'])
def predict():
    data = request.json
    result = predict_career(data)

    # SAVE HISTORY
    if 'user' in session and result.get("Predictions"):
        email = session['user']
        top = result["Predictions"][0]

        conn = sqlite3.connect('users.db')
        c = conn.cursor()
        c.execute("INSERT INTO history (email, career, score) VALUES (?, ?, ?)",
                  (email, top["Career"], str(top["Suitability Score (%)"])))
        conn.commit()
        conn.close()

    return jsonify(result)


# ================= ADMIN DASHBOARD PANEL =================

@app.route('/admin')
def admin_dashboard():
    # Security: Agar admin logged in nahi hai, toh page access nahi hoga
    if 'role' not in session or session['role'] != 'admin':
        return "Access Denied: Only Admins can access this page! ❌", 403

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("SELECT id, email, first_name, last_name FROM users")
    all_users = c.fetchall()
    conn.close()
    return render_template('admin.html', users=all_users)

# ================= ADMIN: UPDATE USER DETAILS =================
@app.route('/admin/update/<int:user_id>', methods=['POST'])
def admin_update_user(user_id):
    if 'role' not in session or session['role'] != 'admin':
        return "Unauthorized ❌", 403

    email = request.form['email']
    first_name = request.form['first_name']
    last_name = request.form['last_name']
    new_password = request.form['password']

    conn = sqlite3.connect('users.db')
    c = conn.cursor()

    if new_password:
        hashed_password = generate_password_hash(new_password)
        c.execute("""
            UPDATE users 
            SET email=?, first_name=?, last_name=?, password=? 
            WHERE id=?
        """, (email, first_name, last_name, hashed_password, user_id))
    else:
        c.execute("""
            UPDATE users 
            SET email=?, first_name=?, last_name=? 
            WHERE id=?
        """, (email, first_name, last_name, user_id))

    conn.commit()
    conn.close()
    return redirect('/admin')

# ================= ADMIN: DELETE USER =================
@app.route('/admin/delete/<int:user_id>')
def admin_delete_user(user_id):
    if 'role' not in session or session['role'] != 'admin':
        return "Unauthorized ❌", 403

    conn = sqlite3.connect('users.db')
    c = conn.cursor()
    c.execute("DELETE FROM users WHERE id=?", (user_id,))
    conn.commit()
    conn.close()
    return redirect('/admin')


# ================= RUN =================
if __name__ == '__main__':
    app.run(debug=True)