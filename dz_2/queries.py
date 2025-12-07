from datetime import datetime, timedelta
from pymongo import MongoClient
from pprint import pformat
import json

class UniversityQueries:
    def __init__(self, client: MongoClient, db: str):
        self.db = client[db]

    @staticmethod
    def _safe_output(query_result, query_name: str, query_number: int):
        """
        Красиво форматирует результаты запроса для вывода в консоль
        """
        header = f"Запрос #{query_number}: {query_name}"
        separator = "=" * len(header)

        print(f"\n{separator}")
        print(header)
        print(separator)

        if not query_result:
            print("Нет данных")
            return

        if isinstance(query_result, dict):
            print("Структура документа:")
            print(pformat(query_result, indent=2, width=100))

        elif isinstance(query_result, list):
            count = len(query_result)
            print(f"Найдено записей: {count}")

            if count > 5:
                print("Показаны первые 5 записей:")
                display_data = query_result[:5]
            else:
                display_data = query_result

            for i, item in enumerate(display_data, 1):
                if isinstance(item, dict):
                    print(f"\nЗапись #{i}")
                    print(pformat(item, indent=2, width=100))
                else:
                    print(f"{i}. {item}")

            if count > 5:
                print(f"\nИтого: {count} записей (показаны первые 5)")

        elif isinstance(query_result, int) or isinstance(query_result, float):
            print(f"Результат: {query_result}")

        else:
            print("Результат:")
            print(str(query_result))

    def get_it_students(self):
        """1. Все студенты факультета ИТ (course_id = 1)"""
        return list(self.db.students.find({"course_id": 1}, {"_id": 0}))

    def get_popular_courses(self, limit: int = 3):
        """2. Курсы с количеством студентов (топ-N по популярности)"""
        pipeline = [
            {"$lookup": {
                "from": "students",
                "localField": "course_id",
                "foreignField": "course_id",
                "as": "enrollments"
            }},
            {"$addFields": {"student_count": {"$size": "$enrollments"}}},
            {"$sort": {"student_count": -1}},
            {"$limit": limit},
            {"$project": {"title": 1, "student_count": 1, "_id": 0}}
        ]
        return list(self.db.courses.aggregate(pipeline))

    def get_late_submissions(self):
        """3. Студенты с просроченными заданиями"""
        return list(self.db.submissions.find({
            "$expr": {
                "$and": [
                    {"$gt": ["$submitted_at", "$deadline"]},
                    {"$eq": ["$status", "late"]}
                ]
            }
        }, {"_id": 0}))

    def get_course_averages(self):
        """4. Средняя оценка по каждому курсу"""
        pipeline = [
            {"$group": {
                "_id": "$course_id",
                "avg_grade": {"$avg": "$grade"}
            }},
            {"$lookup": {
                "from": "grades",
                "localField": "_id",
                "foreignField": "course_id",
                "as": "course_info"
            }},
            {"$unwind": "$course_info"},
            {"$project": {
                "course_name": "$course_info.title",
                "average_grade": {"$round": ["$avg_grade", 2]},
                "_id": 0
            }},
            {"$sort": {"average_grade": -1}}
        ]
        return list(self.db.grades.aggregate(pipeline))

    def get_low_attendance_students(self, course_id: int = 1, min_attendance_rate: float = 0.7):
        """5. Студенты с посещаемостью < X% по курсу"""
        total_classes = self.db.attendance.count_documents({"course_id": course_id})
        threshold = int(total_classes * min_attendance_rate)

        pipeline = [
            {"$match": {"course_id": course_id}},
            {"$group": {
                "_id": "$student_id",
                "attended": {"$sum": {"$cond": [{"$eq": ["$status", "present"]}, 1, 0]}}
            }},
            {"$match": {"attended": {"$lt": threshold}}},
            {"$lookup": {
                "from": "students",
                "localField": "_id",
                "foreignField": "student_id",
                "as": "student_info"
            }},
            {"$unwind": "$student_info"},
            {"$project": {
                "name": "$student_info.name",
                "surname": "$student_info.surname",
                "attended_classes": "$attended",
                "total_classes": total_classes,
                "_id": 0
            }}
        ]
        return list(self.db.attendance.aggregate(pipeline))

    def get_pending_assignments_for_student(self, student_id: int = 1):
        """6. Все невыполненные задания для студента"""
        courses = self.db.grades.distinct("course_id", {"student_id": student_id})
        all_assignments = list(self.db.assignments.find({"course_id": {"$in": courses}}))
        submitted_ids = self.db.submissions.distinct("assignment_id", {"student_id": student_id})
        return [a for a in all_assignments if a["assignment_id"] not in submitted_ids]

    def get_top_students(self, limit: int = 5):
        """7. Топ-N студентов по успеваемости"""
        pipeline = [
            {"$group": {
                "_id": "$student_id",
                "avg_grade": {"$avg": "$grade"}
            }},
            {"$sort": {"avg_grade": -1}},
            {"$limit": limit},
            {"$lookup": {
                "from": "students",
                "localField": "_id",
                "foreignField": "student_id",
                "as": "student_info"
            }},
            {"$unwind": "$student_info"},
            {"$project": {
                "full_name": {"$concat": ["$student_info.name", " ", "$student_info.surname"]},
                "average_score": {"$round": ["$avg_grade", 2]},
                "_id": 0
            }}
        ]
        return list(self.db.grades.aggregate(pipeline))

    def get_upcoming_assignments(self, days_ahead: int = 7):
        """8. Задания с дедлайнами в ближайшие N дней"""
        now = datetime.now()
        future = now + timedelta(days=days_ahead)
        return list(self.db.assignments.find({
            "deadline": {"$gte": now, "$lt": future}
        }, {"_id": 0}))

    def get_student_submissions_with_feedback(self, student_id: int = 1):
        """9. Сдачи заданий студента с комментариями"""
        pipeline = [
            {"$match": {"student_id": student_id, "feedback": {"$exists": True}}},
            {"$lookup": {
                "from": "assignments",
                "localField": "assignment_id",
                "foreignField": "assignment_id",
                "as": "assignment_details"
            }},
            {"$unwind": "$assignment_details"},
            {"$lookup": {
                "from": "courses",
                "localField": "course_id",
                "foreignField": "course_id",
                "as": "course_info"
            }},
            {"$unwind": "$course_info"},
            {"$project": {
                "course": "$course_info.title",
                "assignment": "$assignment_details.title",
                "submitted_at": 1,
                "grade": 1,
                "feedback": 1,
                "_id": 0
            }}
        ]
        return list(self.db.submissions.aggregate(pipeline))

    def get_student_attendance_in_period(self, student_id: int, start_date: datetime, end_date: datetime):
        """10. Посещаемость студента за период"""
        pipeline = [
            {"$match": {
                "student_id": student_id,
                "date": {"$gte": start_date, "$lt": end_date}
            }},
            {"$lookup": {
                "from": "courses",
                "localField": "course_id",
                "foreignField": "course_id",
                "as": "course_info"
            }},
            {"$unwind": "$course_info"},
            {"$project": {
                "course": "$course_info.title",
                "date": 1,
                "status": 1,
                "_id": 0
            }},
            {"$sort": {"date": 1}}
        ]
        return list(self.db.attendance.aggregate(pipeline))

    def get_courses_by_lowest_average(self, limit: int = 3):
        """11. Курсы с самым низким средним баллом"""
        pipeline = [
            {"$group": {
                "_id": "$course_id",
                "avg_grade": {"$avg": "$grade"}
            }},
            {"$sort": {"avg_grade": 1}},
            {"$limit": limit},
            {"$lookup": {
                "from": "courses",
                "localField": "_id",
                "foreignField": "course_id",
                "as": "course_info"
            }},
            {"$unwind": "$course_info"},
            {"$project": {
                "course_name": "$course_info.title",
                "average_grade": {"$round": ["$avg_grade", 2]},
                "_id": 0
            }}
        ]
        return list(self.db.grades.aggregate(pipeline))

    def get_submission_status_stats(self):
        """12. Статистика по статусам сдачи заданий"""
        pipeline = [
            {"$group": {
                "_id": "$status",
                "count": {"$sum": 1}
            }},
            {"$project": {
                "status": "$_id",
                "count": 1,
                "_id": 0
            }}
        ]
        return list(self.db.submissions.aggregate(pipeline))

    def get_student_grades_for_course(self, course_id: int):
        """13. Все студенты и их оценки по курсу"""
        pipeline = [
            {"$match": {"course_id": course_id}},
            {"$lookup": {
                "from": "students",
                "localField": "student_id",
                "foreignField": "student_id",
                "as": "student_info"
            }},
            {"$unwind": "$student_info"},
            {"$project": {
                "student": {"$concat": ["$student_info.name", " ", "$student_info.surname"]},
                "grade": 1,
                "date": 1,
                "_id": 0
            }},
            {"$sort": {"grade": -1}}
        ]
        return list(self.db.grades.aggregate(pipeline))

    def get_student_full_profile(self, student_id: int):
        """15. Полный профиль студента (для API/приложения)"""
        return {
            "profile": self.db.students.find_one({"student_id": student_id}, {"_id": 0}),
            "courses": self.get_student_grades_for_course(1),  # или агрегировать все курсы
            "submissions": list(self.db.submissions.find(
                {"student_id": student_id},
                {"_id": 0, "assignment_id": 1, "submitted_at": 1, "status": 1, "grade": 1}
            ))
        }

    # Запрос №14 (сложный) — упрощённая версия
    def get_frequent_absentees(self, min_absences: int = 3):
        """14. Студенты с большим количеством пропусков (упрощённо)"""
        pipeline = [
            {"$match": {"status": "absent"}},
            {"$group": {
                "_id": "$student_id",
                "absence_count": {"$sum": 1}
            }},
            {"$match": {"absence_count": {"$gte": min_absences}}},
            {"$lookup": {
                "from": "students",
                "localField": "_id",
                "foreignField": "student_id",
                "as": "student_info"
            }},
            {"$unwind": "$student_info"},
            {"$project": {
                "name": "$student_info.name",
                "surname": "$student_info.surname",
                "absences": "$absence_count",
                "_id": 0
            }}
        ]
        return list(self.db.attendance.aggregate(pipeline))

    def get_all_queries_result(self):
        print("\n" + "=" * 70)
        print("УНИВЕРСИТЕТСКАЯ АНАЛИТИКА: ВЫПОЛНЕНИЕ ВСЕХ ЗАПРОСОВ")
        print("=" * 70)

        queries_config = [
            (1, "Все студенты факультета ИТ", self.get_it_students, {}),
            (2, "Топ-3 популярных курса", self.get_popular_courses, {"limit": 3}),
            (3, "Просроченные задания", self.get_late_submissions, {}),
            (4, "Средняя оценка по курсам", self.get_course_averages, {}),
            (5, "Студенты с низкой посещаемостью", self.get_low_attendance_students,
             {"course_id": 1, "min_attendance_rate": 0.7}),
            (6, "Невыполненные задания для студента #1", self.get_pending_assignments_for_student, {"student_id": 1}),
            (7, "Топ-5 студентов по успеваемости", self.get_top_students, {"limit": 5}),
            (8, "Ближайшие дедлайны (7 дней)", self.get_upcoming_assignments, {"days_ahead": 7}),
            (9, "Сдачи заданий студента #1 с комментариями", self.get_student_submissions_with_feedback,
             {"student_id": 1}),
            (10, "Посещаемость студента #1 за октябрь 2025", self.get_student_attendance_in_period, {
                "student_id": 1,
                "start_date": datetime(2025, 10, 1),
                "end_date": datetime(2025, 11, 1)
            }),
            (11, "Курсы с низким средним баллом", self.get_courses_by_lowest_average, {"limit": 3}),
            (12, "Статистика по статусам сдачи заданий", self.get_submission_status_stats, {}),
            (13, "Оценки по курсу 'Базы данных'", self.get_student_grades_for_course, {"course_id": 1}),
            (14, "Студенты с частыми пропусками", self.get_frequent_absentees, {"min_absences": 2}),
            (15, "Полный профиль студента #1", self.get_student_full_profile, {"student_id": 1})
        ]

        for query_num, query_name, query_method, params in queries_config:
            try:
                # Выполняем запрос и получаем результат
                result = query_method(**params)
                # Выводим результат через красивый форматер
                self._safe_output(result, query_name, query_num)
            except Exception as e:
                print(f"\n{'=' * 60}")
                print(f"ОШИБКА в запросе #{query_num}: {query_name}")
                print(f"Ошибка: {str(e)}")
                print(f"{'=' * 60}")

        print("\n" + "=" * 70)
        print("ВСЕ ЗАПРОСЫ ВЫПОЛНЕНЫ")
        print("=" * 70)