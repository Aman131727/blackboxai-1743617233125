from flask import Flask, render_template, request, redirect, url_for, flash, send_file
from database import init_db, Student
from database_operations import StudentTrackerOperations
from sqlalchemy.orm import Session
import os
import json
import matplotlib.pyplot as plt
import io
import base64

class StudentTracker:
    def __init__(self):
        self.Session = init_db()

    def add_student(self, name, roll_number):
        session = self.Session()
        try:
            student = Student(name=name, roll_number=roll_number)
            session.add(student)
            session.commit()
            return True
        except:
            session.rollback()
            return False
        finally:
            session.close()

    def get_all_students(self):
        session = self.Session()
        try:
            return session.query(Student).all()
        finally:
            session.close()

    def add_grades(self, roll_number, subject, grade):
        session = self.Session()
        try:
            student = session.query(Student).filter_by(roll_number=roll_number).first()
            if not student:
                return False
            
            grades = json.loads(student.grades) if student.grades else {}
            grades[subject] = float(grade)
            student.grades = json.dumps(grades)
            session.commit()
            return True
        except:
            session.rollback()
            return False
        finally:
            session.close()

    def get_student_details(self, roll_number):
        session = self.Session()
        try:
            student = session.query(Student).filter_by(roll_number=roll_number).first()
            if not student:
                return None
            
            grades = json.loads(student.grades) if student.grades else {}
            average = sum(grades.values())/len(grades) if grades else 0
            return {
                'name': student.name,
                'roll_number': student.roll_number,
                'grades': grades,
                'average': round(average, 2)
            }
        finally:
            session.close()

app = Flask(__name__)
app.secret_key = os.urandom(24)
tracker = StudentTracker()

@app.route('/')
def index():
    students = tracker.get_all_students()
    return render_template('index.html', students=students)

@app.route('/add_student', methods=['GET', 'POST'])
def add_student():
    if request.method == 'POST':
        name = request.form.get('name')
        roll_number = request.form.get('roll_number')
        if not name or not roll_number:
            flash('Name and Roll Number are required', 'error')
        elif tracker.add_student(name, roll_number):
            flash('Student added successfully!', 'success')
            return redirect(url_for('index'))
        else:
            flash('Roll number already exists', 'error')
    return render_template('add_student.html')

@app.route('/add_grades/<roll_number>', methods=['GET', 'POST'])
def add_grades(roll_number):
    student = tracker.get_student_details(roll_number)
    if not student:
        flash('Student not found', 'error')
        return redirect(url_for('index'))
    
    if request.method == 'POST':
        subject = request.form.get('subject')
        grade = request.form.get('grade')
        try:
            grade = float(grade)
            if not 0 <= grade <= 100:
                raise ValueError
        except ValueError:
            flash('Grade must be a number between 0-100', 'error')
        else:
            if tracker.add_grades(roll_number, subject, grade):
                flash(f'Grade for {subject} added successfully!', 'success')
                return redirect(url_for('view_student', roll_number=roll_number))
            else:
                flash('Failed to add grade', 'error')
    
    subjects = ['Math', 'Science', 'English']
    return render_template('add_grades.html', student=student, subjects=subjects)

@app.route('/student/<roll_number>')
def view_student(roll_number):
    student = tracker.get_student_details(roll_number)
    if not student:
        flash('Student not found', 'error')
        return redirect(url_for('index'))
    return render_template('student_details.html', student=student)

@app.route('/subject_topper/<subject>')
def subject_topper(subject):
    operations = StudentTrackerOperations()
    topper, score = operations.get_subject_topper(subject)
    if not topper:
        flash(f'No grades recorded for {subject}', 'error')
        return redirect(url_for('index'))
    return render_template('subject_topper.html',
                         subject=subject,
                         topper_name=topper.name,
                         topper_roll=topper.roll_number,
                         score=score)

@app.route('/class_average/<subject>')
def class_average(subject):
    operations = StudentTrackerOperations()
    average = operations.get_class_average(subject)
    if average == 0:
        flash(f'No grades recorded for {subject}', 'error')
        return redirect(url_for('index'))
    return render_template('class_average.html',
                         subject=subject,
                         average=average)

if __name__ == '__main__':
    app.run(debug=True)
