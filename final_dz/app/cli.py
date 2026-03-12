from pprint import pprint
from app.db import get_db


def menu() -> str:
    print("\n=== Mongo CLI ===")
    print("1. Показать 5 студентов")
    print("2. Найти студента по email")
    print("3. Показать курсы")
    print("4. Показать сдачи по course_id")
    print("5. Средняя оценка студента")
    print("0. Выход")
    return input("Выбор: ").strip()


def main():
    db = get_db()
    while True:
        choice = menu()
        if choice == "1":
            for doc in db.students.find({}, {"_id": 0}).limit(5):
                pprint(doc)
        elif choice == "2":
            email = input("Введите email: ").strip()
            doc = db.students.find_one({"email": email}, {"_id": 0})
            pprint(doc or {"message": "Студент не найден"})
        elif choice == "3":
            for doc in db.courses.find({}, {"_id": 0}).sort("course_id", 1):
                pprint(doc)
        elif choice == "4":
            course_id = int(input("Введите course_id: ").strip())
            for doc in db.submissions.find({"course_id": course_id}, {"_id": 0}).limit(20):
                pprint(doc)
        elif choice == "5":
            student_id = int(input("Введите student_id: ").strip())
            pipeline = [
                {"$match": {"student_id": student_id}},
                {"$group": {"_id": "$student_id", "avg_grade": {"$avg": "$grade"}}}
            ]
            result = list(db.grades.aggregate(pipeline))
            pprint(result[0] if result else {"message": "Оценки не найдены"})
        elif choice == "0":
            print("Выход")
            break
        else:
            print("Некорректный ввод")


if __name__ == "__main__":
    main()
