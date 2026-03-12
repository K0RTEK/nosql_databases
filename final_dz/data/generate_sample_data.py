from __future__ import annotations

import random
from datetime import datetime, timedelta
from faker import Faker

fake = Faker("ru_RU")


def generate_courses(n: int):
    result = []
    for i in range(1, n + 1):
        result.append({
            "course_id": i,
            "title": f"Course {i}",
            "code": f"CS-{100 + i}",
            "credits": random.randint(2, 6),
            "description": f"Описание курса {i}"
        })
    return result


def generate_students(n: int, course_count: int):
    result = []
    for i in range(1, n + 1):
        course_id = random.randint(1, course_count)
        result.append({
            "student_id": i,
            "name": fake.first_name(),
            "surname": fake.last_name(),
            "age": random.randint(17, 28),
            "email": f"student{i}@example.com",
            "course_id": course_id,
            "university_course_id": course_id
        })
    return result


def generate_assignments(n: int, course_count: int):
    now = datetime.utcnow()
    result = []
    for i in range(1, n + 1):
        published_at = now - timedelta(days=random.randint(15, 60))
        deadline = now + timedelta(days=random.randint(1, 30))
        result.append({
            "assignment_id": i,
            "course_id": random.randint(1, course_count),
            "title": f"Assignment {i}",
            "description": f"Описание задания {i}",
            "deadline": deadline,
            "max_score": 5,
            "published_at": published_at,
        })
    return result


def generate_submissions(students, assignments, multiplier: int = 3):
    result = []
    statuses = ["submitted", "late", "reviewed"]
    for _ in range(len(students) * multiplier):
        student = random.choice(students)
        assignment = random.choice(assignments)
        submitted_at = datetime.utcnow() - timedelta(days=random.randint(0, 20))
        result.append({
            "student_id": student["student_id"],
            "course_id": assignment["course_id"],
            "assignment_id": assignment["assignment_id"],
            "submitted_at": submitted_at,
            "status": random.choice(statuses),
            "grade": random.randint(2, 5),
            "feedback": random.choice(["Хорошо", "Отлично", "Нужно доработать"]),
            "file_url": f"https://files.example.com/{student['student_id']}/{assignment['assignment_id']}"
        })
    return result


def generate_grades(students, count: int = 3000):
    result = []
    for _ in range(count):
        student = random.choice(students)
        result.append({
            "student_id": student["student_id"],
            "course_id": student["course_id"],
            "grade": random.randint(2, 5),
            "date": datetime.utcnow() - timedelta(days=random.randint(0, 120))
        })
    return result


def generate_attendances(students, count: int = 5000):
    result = []
    statuses = ["present", "absent", "late", "excused"]
    for _ in range(count):
        student = random.choice(students)
        result.append({
            "student_id": student["student_id"],
            "course_id": student["course_id"],
            "date": datetime.utcnow() - timedelta(days=random.randint(0, 180)),
            "status": random.choice(statuses)
        })
    return result
