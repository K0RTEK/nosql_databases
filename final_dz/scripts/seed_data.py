import argparse
from app.db import get_db
from data.generate_sample_data import (
    generate_courses,
    generate_students,
    generate_assignments,
    generate_submissions,
    generate_grades,
    generate_attendances,
)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--students", type=int, default=1000)
    parser.add_argument("--courses", type=int, default=20)
    parser.add_argument("--assignments", type=int, default=100)
    args = parser.parse_args()

    db = get_db()

    db.students.delete_many({})
    db.courses.delete_many({})
    db.assignments.delete_many({})
    db.submissions.delete_many({})
    db.grades.delete_many({})
    db.attendances.delete_many({})

    courses = generate_courses(args.courses)
    students = generate_students(args.students, args.courses)
    assignments = generate_assignments(args.assignments, args.courses)
    submissions = generate_submissions(students, assignments)
    grades = generate_grades(students)
    attendances = generate_attendances(students)

    db.courses.insert_many(courses)
    db.students.insert_many(students)
    db.assignments.insert_many(assignments)
    db.submissions.insert_many(submissions, ordered=False)
    db.grades.insert_many(grades)
    db.attendances.insert_many(attendances)

    print("[OK] sample data inserted")
    print(f"students: {len(students)}")
    print(f"courses: {len(courses)}")
    print(f"assignments: {len(assignments)}")
    print(f"submissions: {len(submissions)}")
    print(f"grades: {len(grades)}")
    print(f"attendances: {len(attendances)}")


if __name__ == "__main__":
    main()
