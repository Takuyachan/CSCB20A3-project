from datetime import datetime, timedelta
from flask import Flask, render_template, request, redirect, flash, session, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import Bcrypt


app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///assignment3.db'
app.config['SECRET_KEY'] = 'secret_key'
app.config['PERMANENT_SESSION_LIFETIME'] = timedelta(minutes = 15)
db = SQLAlchemy(app)
bcrypt = Bcrypt(app)

class Person(db.Model):
	__tablename__ = 'Person'
	id = db.Column(db.Integer, primary_key = True)
	username = db.Column(db.String(20), nullable = False, unique = True)
	firstname = db.Column(db.String(20), nullable = False)
	lastname = db.Column(db.String(20), nullable = False)
	email = db.Column(db.String(100), unique=True, nullable=False)
	password = db.Column(db.String(20), nullable = False)
	role = db.Column(db.String(15), nullable = False)
	#role is either Studenr or Instructor
db.create_all()

def __repr__(self):
	return f"Person('{self.firstname}', '{self.email}', '{self.role}')"

class Courses(db.Model):
	__tablename__ = 'Courses'
	username = db.Column(db.String(20), db.ForeignKey(Person.username), nullable = False, primary_key = True)
	course = db.Column(db.String(10), nullable = False, primary_key = True)
db.create_all()

class Grades(db.Model):
	__tablename__ = 'Grades'
	username = db.Column(db.String(20), db.ForeignKey(Person.username), nullable = False, primary_key = True)
	assignment = db.Column(db.String(50), nullable = False, primary_key = True)
	grade = db.Column(db.Float, nullable = False)
	outof = db.Column(db.Integer, nullable = False)
	remark = db.Column(db.String(500), nullable = True)
db.create_all()

def __repr__(self):
	return f"Grades('{self.username}', '{self.assignment}', '{self.grade}')"

class Feedback(db.Model):
	__tablename__ = 'Feedback'
	instructorname = db.Column(db.String(30), nullable = False, primary_key = True)
	coursecode = db.Column(db.String(10), nullable = False, primary_key = True)
	time = db.Column(db.String(20), nullable = False, default = datetime.utcnow)
	feedback_a = db.Column(db.String(500), nullable = False, primary_key = True)
	feedback_b = db.Column(db.String(500), nullable = False)
	feedback_c = db.Column(db.String(500), nullable = False)
	feedback_d = db.Column(db.String(500), nullable = False)
db.create_all()

@app.route('/')
@app.route('/index')
def index():
	return render_template("index.html")

# Signup method
@app.route('/signup', methods = ['GET', 'POST'])
def signup():
	if request.method == 'POST':
		# Extracting all the information that are entered by the user.
		username = request.form['username']
		firstname = request.form.get('firstname')
		lastname = request.form.get('lastname')
		email = request.form.get('email')
		role = request.form.get('role')
		hashed_password = bcrypt.generate_password_hash(request.form['password']).decode('utf-8')

		#Extra code added here
		query_username_result = db.session.query(Person.username, Person.email)
		cur_usernames = []
		cur_emails = []
		for one in query_username_result:
			cur_usernames.append(one[0])
			cur_emails.append(one[1])

		if(username in cur_usernames):
			flash('The username already exists. Please enter a different one.')
			return render_template('signup.html')
		
		elif(email in cur_emails):
			flash('The email is already used for registeration. Please use another one.')
			return render_template('signup.html')
		#original code from here

		else:
			# Storing the information into the variable named reg_details
			reg_details =(
			username,
			firstname,
			lastname,
			email,
			role,
			hashed_password
			)
			# Calling add_users() method and add the data to the database.
			add_users(reg_details)
			# Calling the flash message to notify the user.
			flash('Registration Successful! Please login now.')
			# Redirect to the login page
			return redirect(url_for('login'))

	else:
		return render_template('signup.html')

@app.route('/login', methods = ['GET', 'POST'])
def login():
	if request.method == 'POST':
		# Extracting all the information entered by the user.
		username = request.form.get('username')
		password = request.form.get('password')
		# Find the corresponding user from the database.
		person = Person.query.filter_by(username = username).first()
		# Calling the flash message if either the email does not exist or password does not match.
		if not person or not bcrypt.check_password_hash(person.password, password):
			flash('The user verification failed. Please try again.')
			return render_template('login.html')
		# Else, declare the session and put username and role into it and redirect to the home page
		else:
			session['name'] = person.username
			session['fullname'] = person.firstname + " " + person.lastname
			session['role'] = person.role
			session.permanent = True
			flash('logged in!')
			return redirect(url_for('index'))
	else:
		# If the name variable is already in the session, display the flash message, telling the user is already logged in.
		if 'name' in session:
			flash('already logged in!')
			return redirect(url_for('index'))
		else:
			return render_template('login.html')

#Letting user to logout 
@app.route('/logout')
def logout():
	session.pop('name', default = None)
	return redirect(url_for('index'))


@app.route('/piazza')
def piazza():
	return render_template("Piazza.html")

@app.route('/markus')
def markus():
	return render_template("Markus.html")

@app.route('/labs')
def labs():
	return render_template("Labs.html")

@app.route('/syllabus')
def syllabus():
	return render_template("Syllabus.html")

@app.route('/assignments')
def assignments():
    return render_template("Assignments.html")

@app.route('/lectures')
def lectures():
	return render_template("Lectures.html")

@app.route('/resources')
def resources():
    return render_template("Resources.html")

@app.route('/courseteam')
def courseteam():
    return render_template("CourseTeam.html")

@app.route('/addcourse', methods = ['GET', 'POST'])
def addcourse():
	if(request.method == "POST"):
		courses = (
		request.form['username'],
		request.form['course']
		)
		course_username_result = db.session.query(Courses.course).filter(Courses.username == courses[0])
		for result in course_username_result:
			print(result[0])
			if(courses[1] == result[0]):
				flash("The course is added already.")
				return render_template("addcourse.html")
		
		course_1 = Courses(username = courses[0], course = courses[1])
		db.session.add(course_1)
		db.session.commit()
		flash("Course added!")
		return render_template("addcourse.html")
	else:
		return render_template("addcourse.html")

@app.route('/anonfeedback', methods = ['GET', 'POST'])
def anonfeedback():
	#If student accesses this page
	if(session['role'] == "Student"):
		#When the form is submitted:
		if (request.method == "POST"):
			#First get what was entered in the form
			feedbacks = (
				request.form['instructorname'],
				request.form['coursecode'],
				request.form['feedback_a'],
				request.form['feedback_b'],
				request.form['feedback_c'],
				request.form['feedback_d']
			)

			#Get the list of courses taught by the instructor chosen
			query_course_result = db.session.query(Courses.course).filter(Courses.username == feedbacks[0])
			#If the entered course code is in the above list, then store feedback
			for result in query_course_result:
				if (feedbacks[1] == result[0]):
					enteredfeedback = Feedback(instructorname = feedbacks[0], coursecode = feedbacks[1], feedback_a = feedbacks[2], 
					feedback_b = feedbacks[3], feedback_c = feedbacks[4], feedback_d = feedbacks[5])
					db.session.add(enteredfeedback)
					db.session.commit()

					# query_instructor_result = db.session.query(Person.username, Person.firstname, Person.lastname).filter(Person.role == "Instructor")
					# instructors = {}
					# for row in query_instructor_result:
					# 	instructors[row[0]] = row[1] + " " + row[2]
					flash('Feedback sent!')
					return render_template("AnonFeedback.html", instructors = get_instructornames())

			# query_instructor_result = db.session.query(Person.username, Person.firstname, Person.lastname).filter(Person.role == "Instructor")
			# instructors = {}
			# for row in query_instructor_result:
			# 	instructors[row[0]] = row[1] + " " + row[2]

			#If the course code is not in the list, prompt user to check again.
			flash('The instructor does not teach the course you have entered. Please check again and submit.')
			return render_template("AnonFeedback.html", instructors = get_instructornames())
		
		else:
			# query_instructor_result = db.session.query(Person.username, Person.firstname, Person.lastname).filter(Person.role == "Instructor")
			# instructors = {}
			# for row in query_instructor_result:
			# 	instructors[row[0]] = row[1] + " " + row[2]
			return render_template("AnonFeedback.html", instructors = get_instructornames())
	
	#Show the feedback for instructor
	else:
		#get all of the courses that instructor (who is logged in) teaches
		query_course_result = db.session.query(Courses.course).filter(Courses.username == session['name'])
		#get all feedbacks
		query_feedback_result = db.session.query(Feedback.coursecode, Feedback.time, Feedback.feedback_a, Feedback.feedback_b,
		Feedback.feedback_c, Feedback.feedback_d)
		courselist = []
		for one in query_course_result:
			courselist.append(one[0])
			resultfeedback = []
			for a_feedback in query_feedback_result:
				#check if the entered course is in the course list, if so add into the list of feedbacks to show
				if(a_feedback[0] in courselist):
					chosenfeedback = []
					chosenfeedback.append(a_feedback[0])
					chosenfeedback.append(a_feedback[1])
					chosenfeedback.append(a_feedback[2])
					chosenfeedback.append(a_feedback[3])
					chosenfeedback.append(a_feedback[4])
					chosenfeedback.append(a_feedback[5])
					resultfeedback.append(chosenfeedback)
		return render_template("AnonFeedbackInstructor.html", resultfeedback = resultfeedback)

@app.route('/InstGrades', methods = ['GET', 'POST'])
def InstGrades():
# An instructor can add the grade of each student for each assignments.
	if request.method == 'POST':
		username=request.form.get('username')
		assignment=request.form.get('assignment')
		grade=request.form.get('grade')
		outof=request.form.get('outof')

		assignments = db.session.query(Grades.assignment).filter(Grades.username == username)
		assignment_list = []
		for one in assignments:
			assignment_list.append(one[0])

		if(assignment in assignment_list):
			flash("The assignment grade for the student is entered already.")
			return render_template("InstGrades.html")
		
		else:
			post = Grades(username=username, assignment=assignment, grade=grade, outof=outof)
			db.session.add(post)
			db.session.commit()
			flash("Grade recorded!")
			return render_template("InstGrades.html")
	else:
		return render_template("InstGrades.html")
	
@app.route('/grades')
def grades():
	#Displaying all the grades that were added by an instructor
	if session["role"] == "Instructor":
		query_grade_result = Grades.query.all()
	else:
		query_grade_result = query_grade(session["name"])
	return render_template("Grades.html", query_grade_result = query_grade_result)

@app.route('/remark', methods = ['GET', 'POST'])
def remark():
	if request.method == 'POST':
		det_assignment = request.form['assignmentname']
		remark = request.form.get('remark')
		Grade_1 = db.session.query(Grades).filter(session["name"] == Grades.username, Grades.assignment == det_assignment)
		for i in Grade_1:
			i.remark = remark
		# remark=request.form.get('remark')
		# grade=Grades(Grades.username, Grades.assignment).filter(session["name"]==Grades.username, Grades.assignment==det_assignment)
		db.session.commit()
		return render_template("remark.html")
	else:
		assignments = db.session.query(Grades.assignment).filter(session["name"] == Grades.username)
		assignmentname =[]
		for assignment in assignments:
			assignmentname.append(assignment[0])
		return render_template("remark.html", assignmentname = assignmentname)

def query_grade(name):
	query_grade = db.session.query(Grades.username, Grades.assignment, Grades.grade, Grades.outof, Grades.remark).filter(Grades.username == name)
	return query_grade


def add_users(reg_details):
	person = Person(username = reg_details[0], firstname = reg_details[1], lastname = reg_details[2], email = reg_details[3], role = reg_details[4], password = reg_details[5])
	db.session.add(person)
	db.session.commit()

def get_instructornames():
	query_instructor_result = db.session.query(Person.username, Person.firstname, Person.lastname).filter(Person.role == "Instructor")
	instructors = {}
	for row in query_instructor_result:
		instructors[row[0]] = row[1] + " " + row[2]
	return instructors

if __name__ == '__main__':
	app.run(debug=True)






