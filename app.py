from flask import Flask, render_template, redirect, url_for, request
from flask_mail import Mail, Message
from models import db, Task
from forms import TaskForm
from datetime import datetime, timedelta

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///tasks.db'
app.config['MAIL_SERVER'] = 'smtp.example.com'
app.config['MAIL_PORT'] = 587
app.config['MAIL_USERNAME'] = 'your_email@example.com'
app.config['MAIL_PASSWORD'] = 'your_email_password'
app.config['MAIL_USE_TLS'] = True
app.config['MAIL_USE_SSL'] = False

db.init_app(app)
mail = Mail(app)

@app.route('/')
def index():
    tasks = Task.query.all()
    return render_template('index.html', tasks=tasks)

@app.route('/task/new', methods=['GET', 'POST'])
def new_task():
    form = TaskForm()
    if form.validate_on_submit():
        task = Task(
            title=form.title.data,
            description=form.description.data,
            due_date=form.due_date.data,
            priority=form.priority.data,
            status=form.status.data
        )
        db.session.add(task)
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('task_form.html', form=form)

@app.route('/task/<int:id>/edit', methods=['GET', 'POST'])
def edit_task(id):
    task = Task.query.get_or_404(id)
    form = TaskForm(obj=task)
    if form.validate_on_submit():
        task.title = form.title.data
        task.description = form.description.data
        task.due_date = form.due_date.data
        task.priority = form.priority.data
        task.status = form.status.data
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('task_form.html', form=form)

@app.route('/task/<int:id>/delete', methods=['POST'])
def delete_task(id):
    task = Task.query.get_or_404(id)
    db.session.delete(task)
    db.session.commit()
    return redirect(url_for('index'))

@app.route('/dashboard')
def dashboard():
    today = datetime.today().date()
    tasks_due_today = Task.query.filter_by(due_date=today).all()
    tasks_overdue = Task.query.filter(Task.due_date < today).all()
    tasks_by_priority = {
        'Low': Task.query.filter_by(priority='Low').count(),
        'Medium': Task.query.filter_by(priority='Medium').count(),
        'High': Task.query.filter_by(priority='High').count()
    }
    return render_template('dashboard.html', tasks_due_today=tasks_due_today, tasks_overdue=tasks_overdue, tasks_by_priority=tasks_by_priority)

def send_email(task):
    msg = Message('Task Due Soon', sender='your_email@example.com', recipients=['user@example.com'])
    msg.body = f"Task '{task.title}' is due on {task.due_date}."
    mail.send(msg)

def check_due_dates():
    today = datetime.today().date()
    upcoming_tasks = Task.query.filter(Task.due_date == today + timedelta(days=1)).all()
    for task in upcoming_tasks:
        send_email(task)

if __name__ == '__main__':
    with app.app_context():
        db.create_all()
    app.run(debug=True)
