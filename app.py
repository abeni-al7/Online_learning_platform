from flask import Flask, render_template

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/register')
def register():
    return render_template('register.html')

@app.route('/login')
def login():
    return render_template('login.html')

@app.route('/courses')
def courses():
    courses = [
        {
            'name': 'Python Programming',
            'code': 'PY101',
            'description': 'Learn Python Programming from scratch'
        },
        {
            'name': 'Web Development',
            'code': 'WD101',
            'description': 'Learn Web Development from scratch'
        },
        {
            'name': 'Data Science',
            'code': 'DS101',
            'description': 'Learn Data Science from scratch'
        },
    ]
    role = 'student'
    return render_template('courses.html', role=role, courses=courses)

if __name__ == '__main__':
    app.run(debug=True)