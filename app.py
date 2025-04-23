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
    'user': 'root',
    'password': 'root',
    'database': 'fitness'
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

        # USER table (User_ID as VARCHAR, added Phone_Number)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS USER (
                User_ID VARCHAR(50) PRIMARY KEY,
                Name VARCHAR(100),
                Age INT,
                Height FLOAT,
                Weight FLOAT,
                Gender VARCHAR(20),
                Phone_Number VARCHAR(15)
            )
        ''')

        # ACTIVITY table (User_ID as VARCHAR)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS ACTIVITY (
                Activity_ID INT AUTO_INCREMENT PRIMARY KEY,
                User_ID VARCHAR(50),
                Activity_type VARCHAR(50),
                Calories_Burned INT,
                Duration INT,
                FOREIGN KEY (User_ID) REFERENCES USER(User_ID)
            )
        ''')

        # GOAL table (User_ID as VARCHAR)
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

        # DIET table (User_ID as VARCHAR)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS DIET (
                Diet_ID INT AUTO_INCREMENT PRIMARY KEY,
                User_ID VARCHAR(50),
                Calories INT,
                FOREIGN KEY (User_ID) REFERENCES USER(User_ID)
            )
        ''')

        # FRIEND table (User_ID and Friend_ID as VARCHAR)
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

        # BADGE table (User_ID as VARCHAR)
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS BADGE (
                Badge_ID INT AUTO_INCREMENT PRIMARY KEY,
                User_ID VARCHAR(50),
                Badge_Type VARCHAR(50),
                Badge_Desc TEXT,
                FOREIGN KEY (User_ID) REFERENCES USER(User_ID)
            )
        ''')

        # Insert test users into USER table
        cursor.execute('INSERT IGNORE INTO USER (User_ID, Name, Age, Height, Weight, Gender, Phone_Number) VALUES (%s, %s, %s, %s, %s, %s, %s)', 
                       ('user', 'Test User', 24, 111, 32, 'Male', '9867654132'))
        cursor.execute('INSERT IGNORE INTO USER (User_ID, Name, Age, Height, Weight, Gender, Phone_Number) VALUES (%s, %s, %s, %s, %s, %s, %s)', 
                       ('user1', 'Test User1', 25, 165, 60, 'Female', '9876543210'))

        # Insert test users into LOGIN_CREDENTIALS table
        cursor.execute('INSERT IGNORE INTO LOGIN_CREDENTIALS (User_ID, Password) VALUES (%s, %s)', ('user', 'user'))
        cursor.execute('INSERT IGNORE INTO LOGIN_CREDENTIALS (User_ID, Password) VALUES (%s, %s)', ('user1', 'user1'))

        # Insert a sample trainer
        cursor.execute('INSERT IGNORE INTO TRAINER (Trainer_ID, Name, Specialization) VALUES (%s, %s, %s)', 
                       ('trainer1', 'John Doe', 'Strength Training'))

        connection.commit()
        print("Test users 'user' and 'user1' added to USER and LOGIN_CREDENTIALS tables.")
        print("Sample trainer 'trainer1' added to TRAINER table.")
    except Error as e:
        print(f"Error initializing database: {e}")
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
                # Ensure the user exists in the USER table
                cursor.execute('SELECT User_ID FROM USER WHERE User_ID = %s', (user_id,))
                if not cursor.fetchone():
                    cursor.execute('INSERT INTO USER (User_ID) VALUES (%s)', (user_id,))
                    connection.commit()
                    print(f"Inserted user {user_id} into USER table")
                return jsonify({'message': 'Login successful'}), 200
            else:
                return jsonify({'error': 'Invalid credentials'}), 401
        except Error as e:
            print(f"Error during login: {e}")
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

    user_id = session['user_id']
    profile = {}
    goals = []
    diets = []
    trainer = {}
    badges = []
    friends = []
    activities = []

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        # Fetch user profile
        cursor.execute('SELECT Name, Age, Height, Weight, Gender, Phone_Number FROM USER WHERE User_ID = %s', (user_id,))
        profile = cursor.fetchone() or {}

        # Fetch goals
        cursor.execute('SELECT Goal_type, Exer_Hours, Target_Weight FROM GOAL WHERE User_ID = %s', (user_id,))
        goals = cursor.fetchall()

        # Fetch diet details
        cursor.execute('SELECT Calories FROM DIET WHERE User_ID = %s', (user_id,))
        diets = cursor.fetchall()

        # Fetch trainer (for demo, assume user is assigned to trainer1)
        cursor.execute('SELECT Name, Specialization FROM TRAINER WHERE Trainer_ID = %s', ('trainer1',))
        trainer = cursor.fetchone() or {}

        # Fetch badges
        cursor.execute('SELECT Badge_Type, Badge_Desc FROM BADGE WHERE User_ID = %s', (user_id,))
        badges = cursor.fetchall()

        # Fetch friends
        cursor.execute('SELECT Friend_ID, Friendship_Streak FROM FRIEND WHERE User_ID = %s', (user_id,))
        friends = cursor.fetchall()

        # Fetch activities
        cursor.execute('SELECT Activity_type, Calories_Burned, Duration FROM ACTIVITY WHERE User_ID = %s', (user_id,))
        activities = cursor.fetchall()

    except Error as e:
        print(f"Error fetching dashboard data: {e}")
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

    return render_template('dashboard.html', profile=profile, goals=goals, diets=diets, trainer=trainer, badges=badges, friends=friends, activities=activities)

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

        print(f"Received activity data: user_id={user_id}, activity_type={activity_type}, calories_burned={calories_burned}, duration={duration}")

        try:
            connection = mysql.connector.connect(**db_config)
            cursor = connection.cursor()

            # Verify user exists in USER table
            cursor.execute('SELECT User_ID FROM USER WHERE User_ID = %s', (user_id,))
            if not cursor.fetchone():
                cursor.execute('INSERT INTO USER (User_ID) VALUES (%s)', (user_id,))
                connection.commit()
                print(f"Inserted user {user_id} into USER table")

            # Insert into ACTIVITY table
            cursor.execute('''
                INSERT INTO ACTIVITY (User_ID, Activity_type, Calories_Burned, Duration)
                VALUES (%s, %s, %s, %s)
            ''', (user_id, activity_type, calories_burned, duration))
            connection.commit()
            print("Activity inserted successfully")
            return jsonify({'message': 'Activity logged successfully'}), 200
        except Error as e:
            print(f"Error inserting activity: {e}")
            return jsonify({'error': str(e)}), 500
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return render_template('activity.html')

# Goal route
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
            print(f"Error inserting goal: {e}")
            return jsonify({'error': str(e)}), 500
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return render_template('goal.html')

# Diet route
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
            print(f"Error inserting diet: {e}")
            return jsonify({'error': str(e)}), 500
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return render_template('diet.html')

# Friend route
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
            print(f"Error inserting friend: {e}")
            return jsonify({'error': str(e)}), 500
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return render_template('friend.html')

# Trainer route
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
            print(f"Error inserting trainer: {e}")
            return jsonify({'error': str(e)}), 500
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return render_template('trainer.html')

# Workout route
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
            print(f"Error inserting workout plan: {e}")
            return jsonify({'error': str(e)}), 500
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return render_template('workout.html')

# Exercise route
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
            print(f"Error inserting exercise: {e}")
            return jsonify({'error': str(e)}), 500
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return render_template('exercise.html')

# Badge route
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
            print(f"Error inserting badge: {e}")
            return jsonify({'error': str(e)}), 500
        finally:
            if connection.is_connected():
                cursor.close()
                connection.close()
    return render_template('badge.html')

# Database route
@app.route('/database')
def database():
    if 'user_id' not in session:
        return redirect(url_for('login'))
    return render_template('database.html')

# API to fetch table data
@app.route('/api/get_table_data', methods=['GET'])
def get_table_data():
    if 'user_id' not in session:
        return jsonify({'error': 'Unauthorized'}), 401

    table_name = request.args.get('table')
    if not table_name:
        return jsonify({'error': 'Table name required'}), 400

    # List of allowed tables to prevent SQL injection
    allowed_tables = [
        'USER', 'LOGIN_CREDENTIALS', 'ACTIVITY', 'GOAL', 'DIET', 
        'FRIEND', 'TRAINER', 'WORKOUT_PLAN', 'EXERCISE', 'BADGE'
    ]

    if table_name.upper() not in allowed_tables:
        return jsonify({'error': 'Invalid table name'}), 400

    try:
        connection = mysql.connector.connect(**db_config)
        cursor = connection.cursor(dictionary=True)

        # Fetch column names
        cursor.execute(f"SHOW COLUMNS FROM {table_name}")
        columns = [column['Field'] for column in cursor.fetchall()]

        # Fetch data
        cursor.execute(f"SELECT * FROM {table_name}")
        data = cursor.fetchall()

        return jsonify({'columns': columns, 'data': data}), 200
    except Error as e:
        print(f"Error fetching table data: {e}")
        return jsonify({'error': str(e)}), 500
    finally:
        if connection.is_connected():
            cursor.close()
            connection.close()

if __name__ == '__main__':
    init_db()
    app.run(debug=True)