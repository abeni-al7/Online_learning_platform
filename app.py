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
    user = {
        'name': 'John Doe',
    }
    role = 'teacher'
    return render_template('courses.html', role=role, courses=courses, user=user)

@app.route('/courses/browse')
def browse_courses():
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
    user = {
        'name': 'John Doe',
    }
    role = 'student'
    return render_template('browse_courses.html', courses=courses, user=user)

@app.route('/courses/enrolled')
def enrolled_courses():
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
    ]
    user = {
        'name': 'John Doe',
    }
    role = 'student'
    return render_template('enrolled_courses.html', courses=courses, user=user)


@app.route('/profile')
def profile():
    role = 'teacher'
    user = {
        'username': 'johndoe',
        'name': 'John Doe',
        'email': 'john@doe.com',
        'role': role,
        'grade': '10th Grade',
        'bio': 'I am a student at XYZ High School',
        'certificates': [
            {
                'name': 'Python Programming',
                'year': '1998',
                'institution': 'ABC Institute',
                'description': 'Learned Python Programming from scratch',
            },
            {
                'name': 'Web Development',
                'year': '1999',
                'institution': 'DEF Institute',
                'description': 'Learned Web Development from scratch',
            },
        ],
        'education': 'Bachelors',
        'experience': '5 years',
        'specializations': ['Python Programming', 'Web Development'],
    }
    return render_template('profile.html', user=user, role=role)

if __name__ == '__main__':
    app.run(debug=True)