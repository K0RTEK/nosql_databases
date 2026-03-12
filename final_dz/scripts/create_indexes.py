from app.db import get_db


def main():
    db = get_db()

    db.students.create_index([("student_id", 1)], unique=True)
    db.students.create_index([("email", 1)], unique=True)
    db.students.create_index([("course_id", 1)])

    db.courses.create_index([("course_id", 1)], unique=True)
    db.courses.create_index([("code", 1)], unique=True)

    db.assignments.create_index([("assignment_id", 1)], unique=True)
    db.assignments.create_index([("course_id", 1)])

    db.submissions.create_index([("course_id", 1), ("student_id", 1), ("assignment_id", 1)])
    db.submissions.create_index([("student_id", 1), ("submitted_at", -1)])

    db.grades.create_index([("student_id", 1), ("course_id", 1), ("date", -1)])
    db.attendances.create_index([("course_id", 1), ("student_id", 1), ("date", -1)])

    print("[OK] indexes created")


if __name__ == "__main__":
    main()
