import datetime
from flask import Flask, render_template, jsonify, request, redirect, url_for, flash, session
import json
import os
import json
import os
from flask import Flask, render_template, request, redirect, url_for, flash, session, jsonify

import psycopg2
from psycopg2.extras import RealDictCursor

import firebase_admin
from firebase_admin import credentials
from firebase_admin import auth

cred = credentials.Certificate("D:/TaskaApp/taskaappdb-firebase-adminsdk-2eil3-d7065c794d.json")
firebase_admin.initialize_app(cred)



app = Flask(__name__)  
app.secret_key = 'your_secret_key'

TASKS_FILE = 'tasks_list.json'
USERS_FILE = 'users.json'

def load_users():
    # Проверяем, существует ли файл
    if not os.path.exists(USERS_FILE):
        # Если файл не существует, создаем его с пустым массивом
        with open(USERS_FILE, 'w', encoding='utf-8') as file:
            json.dump([], file, ensure_ascii=False, indent=4)  # Создаем пустой JSON массив
        return []  # Возвращаем пустой список

    # Если файл существует, загружаем пользователей
    try:
        with open(USERS_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except json.JSONDecodeError:
        print("Ошибка декодирования JSON. Файл будет сброшен.")
        # Если произошла ошибка декодирования, создадим новый файл
        with open(USERS_FILE, 'w', encoding='utf-8') as file:
            json.dump([], file, ensure_ascii=False, indent=4)
        return []

def save_users(users):
    with open(USERS_FILE, 'w', encoding='utf-8') as file:
        json.dump(users, file, ensure_ascii=False, indent=4)

def load_tasks():
    if not os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'w', encoding='utf-8') as file:
            json.dump([], file, ensure_ascii=False, indent=4)  # Создаем пустой JSON массив
        return []

    try:
        with open(TASKS_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    except json.JSONDecodeError:
        print("Ошибка декодирования JSON. Файл будет сброшен.")
        with open(TASKS_FILE, 'w', encoding='utf-8') as file:
            json.dump([], file, ensure_ascii=False, indent=4)
        return []

def save_tasks(tasks):
    with open(TASKS_FILE, 'w', encoding='utf-8') as file:
        json.dump(tasks, file, ensure_ascii=False, indent=4)

users = load_users()

@app.route('/telegram_login', methods=['POST'])
def telegram_login():
    user_data = request.json
    user_id = user_data['id']
    
    # Проверяем, существует ли пользователь
    existing_user = next((user for user in users if user['id'] == user_id), None)
    
    if not existing_user:
        # Если пользователь новый, добавим его в массив пользователей и сохраним в файле
        users.append({
            'id': user_id,
            'first_name': user_data['first_name'],
            'last_name': user_data['last_name'],
            'username': user_data.get('username', ''),
            'photo_url': user_data.get('photo_url', ''),
        })
        save_users(users)
    
    # Устанавливаем сессионные данные
    session['logged_in'] = True
    session['email'] = f"{user_data['first_name']} {user_data['last_name']}"
    
    return jsonify(success=True)

def load_tasks():
    if os.path.exists(TASKS_FILE):
        with open(TASKS_FILE, 'r', encoding='utf-8') as file:
            return json.load(file)
    else:
        return []

def save_tasks():
    with open(TASKS_FILE, 'w', encoding='utf-8') as file:
        json.dump(tasks, file, ensure_ascii=False, indent=4)

tasks = load_tasks()

default_email = 'admin@example.com'
default_password = 'password123'

@app.route('/')
def index():
    return render_template('welcome.html')


@app.route('/registration', methods=['GET', 'POST'])
def registration():

    return render_template('registration.html')

@app.route('/register', methods=['POST'])
def register():
    email = request.json.get('email')
    password = request.json.get('password')
    
    try:
        user = auth.create_user(
            email=email,
            password=password
        )
        return jsonify({'success': True, 'uid': user.uid}), 201
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 400

@app.route('/login', methods=['POST'])
def login():
    id_token = request.json.get('idToken')
    
    try:
        sign_in_result = auth.verify_id_token(id_token)
        uid = sign_in_result.get('uid')
        
        if uid:
            session['logged_in'] = True
            session['email'] = sign_in_result.get('email') 
            return jsonify({'success': True}), 200
        else:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 401


@app.route('/logout')
def logout():
    session.pop('logged_in', None)
    session.pop('email', None)
    return redirect(url_for('login'))

@app.route('/dashboard')
def dashboard():
    tasks = load_tasks()
    return render_template('dashboard.html', tasks=tasks)


@app.route('/tasks')
def tasks_page():
    tasks = load_tasks()
    return render_template('tasks.html', tasks=tasks)

@app.route('/get_tasks_by_date')
def get_tasks_by_date():
    date = request.args.get('date')
    tasks = load_tasks()
    
    filtered_tasks = [task for task in tasks if task['due_date'] == date]
    
    return jsonify({
        'tasks': filtered_tasks,
        'totalTasks': len(tasks)
    })

@app.route('/createNewTask', methods=['GET', 'POST'])
def create_new_task():
    if request.method == 'POST':
        task_title = request.form['task_title']
        task_description = request.form['task_description']
        due_date_time = request.form['due_date'] + 'T' + request.form['due_time']
        
        new_task = {
            'name': task_title,
            'description': task_description,
            'progress': 0,
            'due_date': due_date_time,
            'subtasks': [],
        }
        global tasks
        tasks.append(new_task)
        save_tasks()
        return redirect(url_for('tasks_page'))
    return render_template('createNewTask.html')

@app.route('/update_tasks', methods=['POST'])
def update_tasks():
    date = request.json['date']
    tasks = load_tasks()
    
    date_obj = datetime.fromisoformat(date)
    
    filtered_tasks = [task for task in tasks if task['due_date'] == date_obj]
    return jsonify({
        'tasks': filtered_tasks,
        'totalTasks': len(tasks)
    })

@app.route('/get_current_task')
def get_current_task():
    if len(tasks):
        return jsonify({'task': tasks[-1]})
    else:
        return jsonify({'task': None})


@app.route('/add_subtask/<int:task_index>', methods=['POST'])
def add_subtask(task_index):
    subtask_title = request.form['subtask_title']
    if 0 <= task_index < len(tasks):
        tasks[task_index]['subtasks'].append({
            'title': subtask_title,
            'completed': False 
        })
        save_tasks() 
    return redirect(url_for('tasks_page'))

@app.route('/complete_subtask/<int:task_index>/<int:subtask_index>', methods=['POST'])
def complete_subtask(task_index, subtask_index):
    if 0 <= task_index < len(tasks):
        if 0 <= subtask_index < len(tasks[task_index]['subtasks']):
            tasks[task_index]['subtasks'][subtask_index]['completed'] = True  # Устанавливаем состояние как выполнено
            save_tasks() 
    return redirect(url_for('tasks_page'))

@app.route('/taskDetails')
def task_details():

        return render_template('taskDetails.html')


@app.route('/setting')
def settings_page():
    return render_template('settings.html')

if __name__ == '__main__':
    app.run(debug=True)