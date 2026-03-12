from __future__ import annotations

import argparse
import random
import time
from concurrent.futures import ThreadPoolExecutor, as_completed
from statistics import mean
from pathlib import Path

import matplotlib.pyplot as plt
import pandas as pd

from app.db import get_db


def read_submission(db, course_ids):
    course_id = random.choice(course_ids)
    start = time.perf_counter()
    list(db.submissions.find({"course_id": course_id}).limit(50))
    return time.perf_counter() - start, "read"


def read_student(db, student_ids):
    student_id = random.choice(student_ids)
    start = time.perf_counter()
    db.students.find_one({"student_id": student_id})
    return time.perf_counter() - start, "read"


def aggregate_grades(db, student_ids):
    student_id = random.choice(student_ids)
    pipeline = [
        {"$match": {"student_id": student_id}},
        {"$group": {"_id": "$student_id", "avg_grade": {"$avg": "$grade"}}}
    ]
    start = time.perf_counter()
    list(db.grades.aggregate(pipeline))
    return time.perf_counter() - start, "aggregate"


def worker():
    db = get_db()
    student_ids = [x["student_id"] for x in db.students.find({}, {"student_id": 1, "_id": 0}).limit(1000)]
    course_ids = [x["course_id"] for x in db.courses.find({}, {"course_id": 1, "_id": 0})]
    op = random.choice(["submission", "student", "aggregate"])
    if op == "submission":
        return read_submission(db, course_ids)
    if op == "student":
        return read_student(db, student_ids)
    return aggregate_grades(db, student_ids)


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--operations", type=int, default=3000)
    parser.add_argument("--workers", type=int, default=20)
    args = parser.parse_args()

    latencies = []
    labels = []
    started = time.perf_counter()

    with ThreadPoolExecutor(max_workers=args.workers) as executor:
        futures = [executor.submit(worker) for _ in range(args.operations)]
        for future in as_completed(futures):
            latency, label = future.result()
            latencies.append(latency)
            labels.append(label)

    total_time = time.perf_counter() - started
    throughput = args.operations / total_time if total_time else 0

    df = pd.DataFrame({"operation": labels, "latency_sec": latencies})
    summary = df.groupby("operation", as_index=False).agg(
        avg_latency_sec=("latency_sec", "mean"),
        max_latency_sec=("latency_sec", "max"),
        min_latency_sec=("latency_sec", "min"),
        count=("latency_sec", "size")
    )
    summary.loc[len(summary)] = ["ALL", mean(latencies), max(latencies), min(latencies), len(latencies)]
    summary["throughput_ops_per_sec"] = throughput

    out_dir = Path("tests/results")
    out_dir.mkdir(parents=True, exist_ok=True)
    summary.to_csv(out_dir / "load_test_summary.csv", index=False)

    plt.figure(figsize=(10, 6))
    plt.hist(latencies, bins=30)
    plt.xlabel("Задержка (сек)")
    plt.ylabel("Количество")
    plt.title("Распределение задержек при нагрузочном тестировании")
    plt.tight_layout()
    plt.savefig(out_dir / "latency_histogram.png", dpi=150)

    print(summary.to_string(index=False))
    print(f"\nОбщее время выполнения теста: {total_time:.4f} сек")
    print(f"Производительность (throughput): {throughput:.2f} операций/сек")
    print(f"Файлы с результатами сохранены в каталоге: {out_dir}")


if __name__ == "__main__":
    main()
