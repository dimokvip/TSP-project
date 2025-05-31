from flask import Flask, render_template, request, redirect, url_for, make_response
import requests

app = Flask(__name__)
API_URL = "http://127.0.0.1:8000/api"  # <-- Заменить на реальный URL API, если другой

# ---------------------------
# JWT Utility
# ---------------------------

def get_token(request):
    return request.cookies.get("token")

def auth_headers(request):
    token = get_token(request)
    if token:
        return {"Authorization": f"Bearer {token}"}
    return {}

# ---------------------------
# Routes
# ---------------------------

@app.route('/')
def index():
    return redirect(url_for('tasks'))

# --- Register ---
@app.route('/register', methods=['GET', 'POST'])
def register():
    error = ""
    if request.method == 'POST':
        data = {
            "email": request.form['email'],
            "name": request.form['name'],
            "password": request.form['password']
        }
        res = requests.post(f"{API_URL}/register", json=data)
        if res.status_code == 201:
            return redirect(url_for('login'))
        error = res.json().get('detail', 'Ошибка регистрации')
    return render_template("newapp/templates/register.html", error=error, token=get_token(request))

# --- Login ---
@app.route('/login', methods=['GET', 'POST'])
def login():
    error = ""
    if request.method == 'POST':
        data = {
            "email": request.form['email'],
            "password": request.form['password']
        }
        res = requests.post(f"{API_URL}/login", json=data)
        if res.status_code == 200:
            token = res.json().get("access_token")
            resp = make_response(redirect(url_for('tasks')))
            resp.set_cookie("token", token, httponly=True)
            return resp
        error = res.json().get('detail', 'Ошибка входа')
    return render_template("newapp/templates/login.html", error=error, token=get_token(request))

# --- Logout ---
@app.route('/logout')
def logout():
    resp = make_response(redirect(url_for('login')))
    resp.delete_cookie("token")
    return resp

# --- List Tasks ---
@app.route('/tasks')
def tasks():
    headers = auth_headers(request)
    res = requests.get(f"{API_URL}/tasks", headers=headers)
    if res.status_code == 200:
        tasks = res.json()
        return render_template("newapp/templates/tasks.html", tasks=tasks, token=get_token(request))
    return redirect(url_for('login'))

# --- Create Task ---
@app.route('/tasks/new', methods=['GET', 'POST'])
def new_task():
    if request.method == 'POST':
        data = {
            "title": request.form['title'],
            "description": request.form['description']
        }
        res = requests.post(f"{API_URL}/tasks", json=data, headers=auth_headers(request))
        return redirect(url_for('tasks'))
    return render_template("newapp/templates/task_form.html", task=None, token=get_token(request))

# --- Edit Task ---
@app.route('/tasks/<int:task_id>/edit', methods=['GET', 'POST'])
def edit_task(task_id):
    headers = auth_headers(request)
    if request.method == 'POST':
        data = {
            "title": request.form['title'],
            "description": request.form['description']
        }
        requests.put(f"{API_URL}/tasks/{task_id}", json=data, headers=headers)
        return redirect(url_for('tasks'))

    res = requests.get(f"{API_URL}/tasks/{task_id}", headers=headers)
    if res.status_code == 200:
        task = res.json()
        return render_template("newapp/templates/task_form.html", task=task, token=get_token(request))
    return redirect(url_for('tasks'))

# --- Delete Task ---
@app.route('/tasks/<int:task_id>/delete')
def delete_task(task_id):
    requests.delete(f"{API_URL}/tasks/{task_id}", headers=auth_headers(request))
    return redirect(url_for('tasks'))


if __name__ == "__main__":
    app.run(debug=True)