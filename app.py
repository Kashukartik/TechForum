from flask import Flask, render_template, request, redirect, url_for, session, flash
import sqlite3
from flask import render_template
from werkzeug.security import generate_password_hash, check_password_hash
app = Flask(__name__)

app.secret_key = '#21/12@2002#'

# Initialize the database
conn = sqlite3.connect('techforum.db')
cursor = conn.cursor()


cursor.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        username TEXT NOT NULL,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    );
''')
# The rest of your table creation logic...


conn.execute('''
    CREATE TABLE IF NOT EXISTS users (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        email TEXT NOT NULL UNIQUE,
        password TEXT NOT NULL
    );
''')
conn.execute('''
    CREATE TABLE IF NOT EXISTS questions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        title TEXT NOT NULL,
        content TEXT NOT NULL
    );
''')

conn.execute('''
    CREATE TABLE IF NOT EXISTS answers (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        question_id INTEGER NOT NULL,
        content TEXT NOT NULL,
        FOREIGN KEY (question_id) REFERENCES questions (id)
    );
''')
conn.close()

@app.route('/')
def index():
    # Add logic for the home page if needed
    return render_template('index.html')


# @app.route('/new')
# def new():
#     if 'user_id' not in session:
#         flash('Please log in to access your account.', 'warning')
#         return redirect(url_for('login'))
#     return render_template('new.html')


@app.route('/index')
def home():
    # Fetch all questions from the database
    conn = sqlite3.connect('techforum.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM questions ORDER BY id DESC')
    questions = cursor.fetchall()
    conn.close()
    return render_template('home.html', questions=questions)

@app.route('/ask', methods=['GET', 'POST'])
def ask():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']
        # Insert the question into the database
        conn = sqlite3.connect('techforum.db')
        conn.execute('INSERT INTO questions (title, content) VALUES (?, ?)', (title, content))
        conn.commit()
        conn.close()
        return redirect(url_for('home'))
    return render_template('ask.html')

@app.route('/question/<int:question_id>', methods=['GET', 'POST'])
def question(question_id):
    conn = sqlite3.connect('techforum.db')
    cursor = conn.cursor()
    # Fetch the question details
    cursor.execute('SELECT * FROM questions WHERE id = ?', (question_id,))
    question = cursor.fetchone()
    if question is None:
        flash('Question not found.')
        return redirect(url_for('home'))
    if request.method == 'POST':
        answer_content = request.form['answer']
        # Insert the answer into the database
        cursor.execute('INSERT INTO answers (question_id, content) VALUES (?, ?)', (question_id, answer_content))
        conn.commit()
    # Fetch all answers for the question
    cursor.execute('SELECT * FROM answers WHERE question_id = ? ORDER BY id DESC', (question_id,))
    answers = cursor.fetchall()
    conn.close()
    # Pass the question data correctly as a dictionary
    return render_template('answer.html', question=question, answers=answers)



@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        print("Form submitted.")  # Check if the form submission is being captured
        email = request.form['email']
        password = request.form['password']
        print(f"Received email: {email}, password: {password}")

        # Connect to the database and fetch user data
        conn = sqlite3.connect('techforum.db')
        cursor = conn.cursor()
        cursor.execute('SELECT * FROM users WHERE email = ?', (email,))
        user = cursor.fetchone()
        conn.close()

        # Check if user exists and verify password
        if user:
            # Assuming password is stored in the 4th column (index 3)
            if check_password_hash(user[3], password):
                session['user_id'] = user[0]  # Store the user id in the session
                flash('Login successful!', 'success')
                print("Redirecting to home page...")
                return redirect(url_for('home'))  # Redirect to home page
            else:
                flash('Invalid email or password', 'danger')
        else:
            flash('Invalid email or password', 'danger')

    return render_template('login.html')





@app.route('/logout')
def logout():
    session.pop('user_id', None)  # Remove user_id from session
    flash('You have been logged out.', 'info')
    return redirect(url_for('index'))  # Redirect to the home page



@app.route('/signup', methods=['GET', 'POST'])
def signup():
    if request.method == 'POST':
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']
        confirm_password = request.form['confirm-password']

        if password != confirm_password:
            flash('Passwords do not match!', 'danger')
            return render_template('signup.html')

        hashed_password = generate_password_hash(password)

        # Insert the new user into the database
        conn = sqlite3.connect('techforum.db')
        try:
            conn.execute('INSERT INTO users (username, email, password) VALUES (?, ?, ?)', (username, email, hashed_password))
            conn.commit()
            flash('Registration successful! You can log in now.', 'success')
            return redirect(url_for('login'))
        except sqlite3.IntegrityError:
            flash('Email already exists!', 'danger')
        finally:
            conn.close()
    
    return render_template('signup.html')



@app.route('/account')
def account():
    if 'user_id' not in session:
        flash('Please log in to access your account.', 'warning')
        return redirect(url_for('login'))

    # Fetch user details from the database
    conn = sqlite3.connect('techforum.db')
    cursor = conn.cursor()
    cursor.execute('SELECT * FROM users WHERE id = ?', (session['user_id'],))
    user = cursor.fetchone()
    conn.close()

    if user is None:
        flash('User not found.', 'danger')
        return redirect(url_for('login'))

    return render_template('account.html', user=user)






if __name__ == '__main__':
    app.run(debug=True)

