from sqlalchemy import create_engine, Column, Integer, String, Float
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import json

Base = declarative_base()

class Student(Base):
    __tablename__ = 'students'
    id = Column(Integer, primary_key=True)
    name = Column(String(50), nullable=False)
    roll_number = Column(String(10), unique=True, nullable=False)
    grades = Column(String(500), default='{}')  # JSON string storage

    def get_grades(self):
        return json.loads(self.grades)

    def set_grades(self, grades_dict):
        self.grades = json.dumps(grades_dict)

def init_db():
    import os
    if 'DATABASE_URL' in os.environ:
        engine = create_engine(os.environ['DATABASE_URL'])
    else:
        engine = create_engine('sqlite:///student_tracker.db')
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)