from flask import Flask, request, jsonify, g
import os
import app.main.models.push_ups as push_ups
from werkzeug.utils import secure_filename
import json
from flask_mysqldb import MySQL
import sqlite3
app = Flask(__name__)

# Configure uploads directory (optional, but improves security)
app.config['UPLOAD_FOLDER'] = 'uploads'

@app.route('/process_video', methods=['POST'])
def process_video():
    if request.method == 'POST':
        # Check for uploaded video file
        video_file = request.files.get('video')
        if video_file:
            # Secure the filename
            filename = secure_filename(video_file.filename)

            # Save the video temporarily (optional, but recommended for larger files)
            if app.config['UPLOAD_FOLDER']:
                video_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
                video_file.save(video_path)
            else:
                video_path = filename  # Temporary file in-memory (less secure)

            # Process the video using your function
            result = push_ups.countPushUps(video_path)

            # Remove temporary video file (if using upload folder)
            if app.config['UPLOAD_FOLDER']:
                os.remove(video_path)

            # Return the result as JSON
            return jsonify({'result': result}), 201
        else:
            return jsonify({'error': 'No video file uploaded'}), 400
    else:
        return jsonify({'error': 'Method not allowed'}), 405

@app.route('/test', methods=['POST'])
def test():
    if request.method == 'POST':
        
        result = 'i hear you'


        # Return the result as JSON
        return jsonify({'result': result}), 201

@app.route('/save_data', methods=['POST'])
def save_data():
  # Access data from request
  data = request.get_json()

  # Write data to JSON file (modify path as needed)
  with open('data.json', 'a') as f:
    json.dump(data, f, indent=True)

  return jsonify({'message': 'Data saved successfully!'}), 200

@app.route('/read_data', methods=['GET'])
def get_data():
  # Read data from JSON file (modify path as needed)
  with open('data.json', 'r') as f:
    data = json.load(f)

  # Return data as JSON response
  return jsonify(data), 200


##########################################################################################
#data partition


import time
import logging

DATABASE = 'users.sqlite'
table = "users"

logging.basicConfig(level=logging.INFO)

def get_db():
    if 'db' not in g:
        retries = 10
        while retries > 0:
            try:
                g.db = sqlite3.connect(DATABASE, timeout=10)
                g.db.execute("PRAGMA journal_mode=WAL;")
                logging.info("Connected to the database")
                return g.db
            except sqlite3.OperationalError as e:
                if 'database is locked' in str(e):
                    retries -= 1
                    logging.warning(f"Database is locked, retrying... {retries} retries left")
                    time.sleep(2)
                else:
                    logging.error(f"OperationalError: {e}")
                    raise e
        logging.error("Failed to open database after multiple retries")
        raise sqlite3.OperationalError("Failed to open database after multiple retries")
    return g.db

@app.teardown_appcontext
def close_db(exception):
    db = g.pop('db', None)
    if db is not None:
        db.close()

@app.route('/add_user', methods=['POST'])
def add_user():   
    conn = get_db()
    try:
        data = request.get_json()
        name = data.get("name")
        name = data.get("name")
        password = data.get("password")
        height = data.get("height")
        weight = data.get("weight")
        age = data.get("age")
        gender = data.get("gender")
        prefeardFoot = data.get("prefeardFoot")
        sql = f"INSERT INTO {table}(name, password, height, weight, age, gender, prefeardFoot) VALUES (?, ?, ?, ?, ?,?,?)"
        retries = 5
        while retries > 0:
            try:
                cursor = conn.execute(sql, (name, password, height, weight, age, gender, prefeardFoot))
                conn.commit()
                logging.info(f"User added with id: {cursor.lastrowid}")
                return jsonify({"message": f"user with id: {cursor.lastrowid} created"}), 201
            except sqlite3.OperationalError as e:
                if 'database is locked' in str(e):
                    retries -= 1
                    logging.warning(f"Database is locked, retrying... {retries} retries left")
                    time.sleep(2)
                else:
                    logging.error(f"OperationalError: {e}")
                    raise e
        logging.error("Failed to add user after multiple retries")
        return "Failed to add user after multiple retries", 500
    except Exception as e:
        logging.error(f"Error while adding user: {e}")
        return "Internal server error", 500


@app.route('/get_user', methods=['POST'])
def read_users():
    conn = get_db()
    try:
        data = request.get_json()
        name = data.get("name")
        print(2)
        print(name)
        cursor = conn.execute(f"SELECT * FROM {table} where name='{name}'")
        print(cursor)
        row = cursor.fetchall()[0]
        print(row)
        user = dict(name=row[0], password = row[1], height=row[2], weight=row[3], age=row[4], gender=row[5], prefeardFoot=row[6])
        
        logging.info(f"Users retrieved: {user}")
        return jsonify(user), 201
    except Exception as e:
        logging.error(f"Error while reading users: {e}")
        return "Internal server error", 500

if __name__ == '__main__':
    app.run(debug=True)