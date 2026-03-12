sh.enableSharding("university_db")
sh.shardCollection("university_db.submissions", { course_id: 1, student_id: 1, assignment_id: 1 })
sh.shardCollection("university_db.attendances", { course_id: 1, student_id: 1, date: 1 })
sh.status()
