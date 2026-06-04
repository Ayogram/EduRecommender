"""
One-off script: update all lesson video_urls in the DB from the curated library.
Run once: python scripts/refresh_videos_from_library.py
"""
import sqlite3
import sys
import os

# Add project root to path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from engine.video_library import get_lesson_video

DB_PATH = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),
                       "database", "edurecommender.db")

db = sqlite3.connect(DB_PATH)
db.row_factory = sqlite3.Row

lessons = db.execute("""
    SELECT ml.id, ml.title, c.title as course_title
    FROM module_lessons ml
    JOIN course_modules cm ON ml.module_id = cm.id
    JOIN courses c ON cm.course_id = c.id
""").fetchall()

print(f"Updating {len(lessons)} lessons...")
for lesson in lessons:
    url = get_lesson_video(lesson["title"], lesson["course_title"])
    db.execute("UPDATE module_lessons SET video_url = ? WHERE id = ?",
               (url, lesson["id"]))
    print(f"  [{lesson['id']:>3}] {lesson['title'][:55]:<55}  ->  ...{url[-20:]}")

db.commit()
db.close()
print(f"\nDone — {len(lessons)} lesson videos updated from curated library.")
