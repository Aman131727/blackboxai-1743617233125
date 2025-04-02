from database import init_db, Student
import json

class StudentTrackerOperations:
    def __init__(self):
        self.Session = init_db()

    def get_subject_topper(self, subject):
        """Returns the top student and their score for a given subject"""
        session = self.Session()
        try:
            students = session.query(Student).all()
            topper = None
            highest_score = 0
            
            for student in students:
                grades = json.loads(student.grades) if student.grades else {}
                if subject in grades and grades[subject] > highest_score:
                    highest_score = grades[subject]
                    topper = student
            
            return topper, highest_score if topper else (None, 0)
        finally:
            session.close()

    def get_class_average(self, subject):
        """Calculates average score for a subject across all students"""
        session = self.Session()
        try:
            students = session.query(Student).all()
            total = 0
            count = 0
            
            for student in students:
                grades = json.loads(student.grades) if student.grades else {}
                if subject in grades:
                    total += grades[subject]
                    count += 1
            
            return round(total/count, 2) if count > 0 else 0
        finally:
            session.close()

    def export_student_data(self, filename='student_data_backup.txt'):
        """Exports all student data to a text file"""
        session = self.Session()
        try:
            students = session.query(Student).all()
            with open(filename, 'w') as f:
                for student in students:
                    grades = json.loads(student.grades) if student.grades else {}
                    f.write(f"Name: {student.name}\n")
                    f.write(f"Roll Number: {student.roll_number}\n")
                    f.write("Grades:\n")
                    for subject, score in grades.items():
                        f.write(f"  {subject}: {score}\n")
                    f.write("\n")
            return True
        except Exception as e:
            print(f"Export failed: {e}")
            return False
        finally:
            session.close()