from flask import Flask, request, jsonify, render_template, redirect, url_for, session
from flask_cors import CORS
import mysql.connector
from mysql.connector import Error

app = Flask(__name__)
app.secret_key = 'your_secret_key'
CORS(app)

# MySQL database configuration
db_config = {
    'host': 'localhost',
    'user': 'your_username',
    'password': 'your_password',
    'database': 'fitness_tracker'
}

# Initialize database and create tables
def init_db():
    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor()

        # LOGIN_CREDENTIALS table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS LOGIN_CREDENTIALS (
                User_ID VARCHAR(50) PRIMARY KEY,
                Password VARCHAR(100) NOT NULL
            )
        ''')

        # USER table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS USER (
                User_ID VARCHAR(50) PRIMARY KEY,
                Name VARCHAR(100),
                Height FLOAT,
                Weight FLOAT,
                Age INT,
                Gender VARCHAR(20)
            )
        ''')

        # ACTIVITY table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ACTIVITY (
                Activity_ID INT AUTO_INCREMENT PRIMARY KEY,
                User_ID VARCHAR(50),
                Act_type VARCHAR(50),
                Calories_burned INT,
                Duration INT,
                FOREIGN KEY (User_ID) REFERENCES USER(User_ID)
            )
        ''')

        # GOAL table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS GOAL (
                Goal_ID INT AUTO_INCREMENT PRIMARY KEY,
                User_ID VARCHAR(50),
                Goal_type VARCHAR(50),
                Exer_Hours INT,
                Target_Weight FLOAT,
                FOREIGN KEY (User_ID) REFERENCES USER(User_ID)
            )
        ''')

        # DIET table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS DIET (
                Diet_ID INT AUTO_INCREMENT PRIMARY KEY,
                User_ID VARCHAR(50),
                Calories INT,
                FOREIGN KEY (User_ID) REFERENCES USER(User_ID)
            )
        ''')

        # FRIEND table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS FRIEND (
                User_ID VARCHAR(50),
                Friend_ID VARCHAR(50),
                Friendship_Streak INT,
                PRIMARY KEY (User_ID, Friend_ID),
                FOREIGN KEY (User_ID) REFERENCES USER(User_ID),
                FOREIGN KEY (Friend_ID) REFERENCES USER(User_ID)
            )
        ''')

        # TRAINER table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS TRAINER (
                Trainer_ID VARCHAR(50) PRIMARY KEY,
                Name VARCHAR(100),
                Specialization VARCHAR(50)
            )
        ''')

        # WORKOUT_PLAN table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS WORKOUT_PLAN (
                Plan_ID INT AUTO_INCREMENT PRIMARY KEY,
                Plan_Type VARCHAR(50),
                Duration INT
            )
        ''')

        # EXERCISE table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS EXERCISE (
                Exercise_ID INT AUTO_INCREMENT PRIMARY KEY,
                Plan_ID INT,
                Exercise_Type VARCHAR(50),
                FOREIGN KEY (Plan_ID) REFERENCES WORKOUT_PLAN(Plan_ID)
            )
        ''')

        # BADGE table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS BADGE (
                Badge_ID INT AUTO_INCREMENT PRIMARY KEY,
                User_ID VARCHAR(50),
                Badge_Type VARCHAR(50),
                Badge_Desc TEXT,
                FOREIGN KEY (User_ID) REFERENCES USER(User_ID)
            )
        ''')

        # Relationships (e.g., USER PERFORMS ACTIVITY, USER HAS GOAL are already handled via foreign keys)
        connection.commit()
    except Error as e:
        print(f"Error: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

# Login route
@app.route('/')
@app.route('/login', methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        data = request.get_json()
        user_id = data['user_id']
        password = data['password']

        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute('SELECT Password FROM LOGIN_CREDENTIALS WHERE User_ID = %s', (user_id,))
            result = cursor.fetchone()

            if result and result[0] == password:
                session['user_id'] = user_id
                return jsonify({'message': 'Login successful'}), 200
            else:
                return jsonify({'error': 'Invalid credentials'}), 401
        except Error as e:
            return jsonify({'error': str(e)}), 500
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return render_template('login.html')

# Dashboard route
@app.route('/dashboard')
def dashboard():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('dashboard.html')

# Activity route
@app.route('/activity', methods=['GET', 'POST'])
def activity():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        data = request.get_json()
        user_id = session['user_id']
        activity_type = data['activity_type']
        calories_burned = data['calories_burned']
        duration = data['duration']

        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO ACTIVITY (User_ID, Act_type, Calories_burned, Duration)
                VALUES (%s, %s, %s, %s)
            ''', (user_id, activity_type, calories_burned, duration))
            connection.commit()
            return jsonify({'message': 'Activity logged successfully'}), 200
        except Error as e:
            return jsonify({'error': str(e)}), 500
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return render_template('activity.html')

# Goal route (similar structure for other routes)
@app.route('/goal', methods=['GET', 'POST'])
def goal():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        data = request.get_json()
        user_id = session['user_id']
        goal_type = data['goal_type']
        exer_hours = data['exer_hours']
        target_weight = data['target_weight']

        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute('''
                INSERT INTO GOAL (User_ID, Goal_type, Exer_Hours, Target_Weight)
                VALUES (%s, %s, %s, %s)
            ''', (user_id, goal_type, exer_hours, target_weight))
            connection.commit()
            return jsonify({'message': 'Goal set successfully'}), 200
        except Error as e:
            return jsonify({'error': str(e)}), 500
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return render_template('goal.html')

# Similar routes for other pages (diet, friend, trainer, workout, exercise, badge)
@app.route('/diet', methods=['GET', 'POST'])
def diet():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        data = request.get_json()
        user_id = session['user_id']
        calories = data['calories']
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute('INSERT INTO DIET (User_ID, Calories) VALUES (%s, %s)', (user_id, calories))
            connection.commit()
            return jsonify({'message': 'Diet logged successfully'}), 200
        except Error as e:
            return jsonify({'error': str(e)}), 500
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return render_template('diet.html')

@app.route('/friend', methods=['GET', 'POST'])
def friend():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        data = request.get_json()
        user_id = session['user_id']
        friend_id = data['friend_id']
        friendship_streak = data['friendship_streak']
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute('INSERT INTO FRIEND (User_ID, Friend_ID, Friendship_Streak) VALUES (%s, %s, %s)', 
                          (user_id, friend_id, friendship_streak))
            connection.commit()
            return jsonify({'message': 'Friend added successfully'}), 200
        except Error as e:
            return jsonify({'error': str(e)}), 500
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return render_template('friend.html')

@app.route('/trainer', methods=['GET', 'POST'])
def trainer():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        data = request.get_json()
        trainer_id = data['trainer_id']
        name = data['name']
        specialization = data['specialization']
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute('INSERT INTO TRAINER (Trainer_ID, Name, Specialization) VALUES (%s, %s, %s)', 
                          (trainer_id, name, specialization))
            connection.commit()
            return jsonify({'message': 'Trainer added successfully'}), 200
        except Error as e:
            return jsonify({'error': str(e)}), 500
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return render_template('trainer.html')

@app.route('/workout', methods=['GET', 'POST'])
def workout():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        data = request.get_json()
        plan_type = data['plan_type']
        duration = data['duration']
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute('INSERT INTO WORKOUT_PLAN (Plan_Type, Duration) VALUES (%s, %s)', (plan_type, duration))
            connection.commit()
            return jsonify({'message': 'Workout plan created successfully'}), 200
        except Error as e:
            return jsonify({'error': str(e)}), 500
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return render_template('workout.html')

@app.route('/exercise', methods=['GET', 'POST'])
def exercise():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        data = request.get_json()
        plan_id = data['plan_id']
        exercise_type = data['exercise_type']
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute('INSERT INTO EXERCISE (Plan_ID, Exercise_Type) VALUES (%s, %s)', (plan_id, exercise_type))
            connection.commit()
            return jsonify({'message': 'Exercise added successfully'}), 200
        except Error as e:
            return jsonify({'error': str(e)}), 500
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return render_template('exercise.html')

@app.route('/badge', methods=['GET', 'POST'])
def badge():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    if request.method == 'POST':
        data = request.get_json()
        user_id = session['user_id']
        badge_type = data['badge_type']
        badge_desc = data['badge_desc']
        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()
            cursor.execute('INSERT INTO BADGE (User_ID, Badge_Type, Badge_Desc) VALUES (%s, %s, %s)', 
                          (user_id, badge_type, badge_desc))
            connection.commit()
            return jsonify({'message': 'Badge added successfully'}), 200
        except Error as e:
            return jsonify({'error': str(e)}), 500
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return render_template('badge.html')

if __name__ == '__main__':
    init_db()
    app.run(debug=True)