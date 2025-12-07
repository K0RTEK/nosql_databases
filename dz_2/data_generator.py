import random
from datetime import datetime, timedelta
from faker import Faker
from pymongo import MongoClient

class DataGenerator:
    STUDENTS = []
    ASSIGNMENTS = []
    SUBMISSIONS = []
    GRADES = []
    COURSES = [
            {
                "course_id": 1,
                "title": "Базы данных",
                "code": "CS-305",
                "credits": 4,
                "description": "Проектирование и управление реляционными и NoSQL базами данных"
            },
            {
                "course_id": 2,
                "title": "Микроэкономика",
                "code": "ECO-201",
                "credits": 3,
                "description": "Основы рыночной экономики, спрос и предложение"
            },
            {
                "course_id": 3,
                "title": "Анатомия человека",
                "code": "MED-101",
                "credits": 5,
                "description": "Строение и функции органов человеческого тела"
            }
        ]

    def __init__(self, client, db: str):
        self.db = client[db]
        self.fake = Faker('ru_RU')
        for collection in ['students', 'courses', 'assignments', 'attendance', 'grades', 'submissions']:
            self.db[collection].delete_many({})
        print("=" * 37)
        print("——>", "Данные в коллекциях очищенны", "<———")
        print("=" * 37)
        print("\n")

    def generate_students_data(self):
        for i in range(1, 50):
            student = {
                "student_id": i,
                "name": self.fake.first_name(),
                "surname": self.fake.last_name(),
                "age": random.randint(17, 22),
                "email": self.fake.email(),
                "course_id": random.choice([1, 2, 3]),
                "university_course_id": random.randint(1, 3)
            }
            self.STUDENTS.append(student)

        self.db.students.insert_many(self.STUDENTS)
        print("\tСгенерировано студентов:", len(self.STUDENTS))

    def generate_courses_data(self):
        self.db.courses.insert_many(self.COURSES)
        print("\tСгенерировано курсов:", len(self.COURSES))


    def generate_assignments_data(self):
        assignment_id_counter = 1

        for course in self.COURSES:
            for week in range(1, 50, 2):
                deadline = datetime(2025, 12, 1) + timedelta(weeks=week)

                assignment = {
                    "assignment_id": assignment_id_counter,
                    "course_id": course["course_id"],
                    "title": f"ДЗ #{week} по {course['title']}",
                    "description": self.fake.text(max_nb_chars=100),
                    "deadline": deadline,
                    "max_score": 10
                }
                self.ASSIGNMENTS.append(assignment)
                assignment_id_counter += 1

        self.db.assignments.insert_many(self.ASSIGNMENTS)
        print("\tСгенерировано заданий:", len(self.ASSIGNMENTS))

    def generate_attendance_data(self):
        attendance_records = []
        statuses = ["present", "absent", "late", "excused"]

        for student in self.STUDENTS:
            for course in self.COURSES:
                for _ in range(2):
                    date = datetime(2025, 10, 1) + timedelta(days=random.randint(1, 30))
                    record = {
                        "student_id": student["student_id"],
                        "course_id": course["course_id"],
                        "date": date,
                        "status": random.choice(statuses)
                    }
                    attendance_records.append(record)

        self.db.attendance.insert_many(attendance_records)
        print("\tСгенерировано записей о посещаемости:", len(attendance_records))

    def generate_grades_data(self):
        for student in self.STUDENTS:
            for course in self.COURSES:
                date = datetime(2025, 12, 10) + timedelta(days=random.randint(-5, 5))
                grade_record = {
                    "student_id": student["student_id"],
                    "course_id": course["course_id"],
                    "grade": random.randint(3, 5),
                    "date": date
                }
                self.GRADES.append(grade_record)

        self.db.grades.insert_many(self.GRADES)
        print("\tСгенерировано оценок:", len(self.GRADES))

    def generate_submissions_data(self):

        for assignment in self.ASSIGNMENTS:
            course_id = assignment["course_id"]

            for student in random.sample(self.STUDENTS, 3):
                submitted_at = assignment["deadline"] + timedelta(
                    hours=random.randint(-48, 24)
                )

                status = "late" if submitted_at > assignment["deadline"] else "submitted"

                grade_value = random.randint(4, 5) if status == "submitted" else 2
                feedback_value = self.fake.sentence() if status == "submitted" else ""

                submission = {
                    "student_id": student["student_id"],
                    "course_id": course_id,
                    "assignment_id": assignment["assignment_id"],
                    "submitted_at": submitted_at,
                    "status": status,
                    "grade": grade_value,
                    "feedback": feedback_value
                }

                self.SUBMISSIONS.append(submission)

        self.db.submissions.insert_many(self.SUBMISSIONS)

    def generate_all(self):
        print("=" * 26)
        print("——>", "Генерация данных", "<———")
        print("=" * 26)
        self.generate_students_data()
        self.generate_courses_data()

        self.generate_assignments_data()

        self.generate_attendance_data()
        self.generate_grades_data()
        self.generate_submissions_data()

        print("\n")

if __name__ == '__main__':
    client = MongoClient('localhost', 27017, username='kirill', password='5567')
    data_generator = DataGenerator(client, "university")
    data_generator.generate_all()
