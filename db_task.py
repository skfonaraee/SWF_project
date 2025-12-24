from database import db
import subprocess
import os
import datetime

def run_queries():
    try:
        with db.connection.cursor() as cursor:

            # -----------------------------
            # 1️⃣ Страны
            # -----------------------------
            cursor.execute("SELECT id, name FROM countries ORDER BY name;")
            countries = cursor.fetchall()
            print("✅ Страны:", [c[1] for c in countries])

            # -----------------------------
            # 2️⃣ Университеты по странам
            # -----------------------------
            for country in countries:
                country_id, country_name = country
                cursor.execute("""
                    SELECT u.name, u.card, u.website
                    FROM universities u
                    WHERE u.country_id = %s
                    ORDER BY u.name;
                """, (country_id,))
                unis = cursor.fetchall()
                print(f"✅ {country_name}, Университеты:", unis)

            # -----------------------------
            # 3️⃣ Программы по университетам
            # -----------------------------
            cursor.execute("""
                SELECT u.name AS university, p.name AS program, p.degree
                FROM programs p
                JOIN universities u ON p.university_id = u.id
                ORDER BY u.name, p.name;
            """)
            programs = cursor.fetchall()
            print("✅ Программы по университетам:")
            for row in programs:
                print(row)

            # -----------------------------
            # 4️⃣ Стипендии / гранты
            # -----------------------------
            cursor.execute("""
                SELECT u.name AS university, s.description
                FROM scholarships s
                JOIN universities u ON s.university_id = u.id
                ORDER BY u.name;
            """)
            scholarships = cursor.fetchall()
            print("✅ Стипендии / гранты:")
            for row in scholarships:
                print(row)

            # -----------------------------
            # 5️⃣ Вопросы и ответы
            # -----------------------------
            cursor.execute("""
                SELECT q.text AS question, a.text AS answer, u.username
                FROM questions q
                LEFT JOIN answers a ON q.id = a.question_id
                LEFT JOIN users u ON q.user_id = u.id
                ORDER BY q.id;
            """)
            qa = cursor.fetchall()
            print("✅ Вопросы и ответы пользователей:")
            for row in qa:
                print(row)

            # -----------------------------
            # 6️⃣ AI-логи
            # -----------------------------
            cursor.execute("""
                SELECT u.username, l.prompt, l.response, l.created_at
                FROM ai_logs l
                JOIN users u ON l.user_id = u.id
                ORDER BY l.created_at DESC;
            """)
            ai_logs = cursor.fetchall()
            print("✅ AI-логи пользователей:")
            for row in ai_logs:
                print(row)

            # -----------------------------
            # 7️⃣ Отзывы пользователей
            # -----------------------------
            cursor.execute("""
                SELECT u.username, f.rating, f.message
                FROM feedback f
                JOIN users u ON f.user_id = u.id
                ORDER BY f.created_at DESC;
            """)
            feedbacks = cursor.fetchall()
            print("✅ Отзывы пользователей:")
            for row in feedbacks:
                print(row)

            # -----------------------------
            # 8️⃣ Опросы пользователей
            # -----------------------------
            cursor.execute("""
                SELECT u.username, s.title, us.answer
                FROM user_surveys us
                JOIN surveys s ON us.survey_id = s.id
                JOIN users u ON us.user_id = u.id
                ORDER BY u.username;
            """)
            surveys = cursor.fetchall()
            print("✅ Пройденные опросы пользователей:")
            for row in surveys:
                print(row)

            # -----------------------------
            # 9️⃣ Сложные запросы с GROUP BY
            # -----------------------------
            # Количество программ по университетам
            cursor.execute("""
                SELECT u.name AS university, COUNT(p.id) AS num_programs
                FROM universities u
                LEFT JOIN programs p ON u.id = p.university_id
                GROUP BY u.name
                ORDER BY num_programs DESC;
            """)
            program_counts = cursor.fetchall()
            print("✅ Количество программ по университетам:")
            for row in program_counts:
                print(row)

            # Количество стипендий по университетам
            cursor.execute("""
                SELECT u.name AS university, COUNT(s.id) AS num_scholarships
                FROM universities u
                LEFT JOIN scholarships s ON u.id = s.university_id
                GROUP BY u.name
                ORDER BY num_scholarships DESC;
            """)
            scholarship_counts = cursor.fetchall()
            print("✅ Количество стипендий по университетам:")
            for row in scholarship_counts:
                print(row)

            # -----------------------------
            # 10️⃣ Создание VIEW
            # -----------------------------
            cursor.execute("""
                CREATE OR REPLACE VIEW user_activity_summary AS
                SELECT 
                    u.id AS user_id,
                    u.username,
                    COUNT(DISTINCT q.id) AS questions_count,
                    COUNT(DISTINCT a.id) AS answers_count,
                    COUNT(DISTINCT l.id) AS ai_interactions
                FROM users u
                LEFT JOIN questions q ON u.id = q.user_id
                LEFT JOIN answers a ON q.id = a.question_id
                LEFT JOIN ai_logs l ON u.id = l.user_id
                GROUP BY u.id, u.username;
            """)
            print("✅ VIEW user_activity_summary создан/обновлен.")

            # -----------------------------
            # 11️⃣ Индексы
            # -----------------------------
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_questions_user_date ON questions(user_id, created_at DESC);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_answers_question_date ON answers(question_id, created_at DESC);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_universities_country ON universities(country_id);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_user_surveys_user ON user_surveys(user_id);")
            print("✅ Индексы созданы/проверены.")

            db.connection.commit()

    except Exception as e:
        print("❌ Ошибка при выполнении SQL-запросов:", e)
        db.connection.rollback()


# -----------------------------
# Резервное копирование
# -----------------------------
def backup_database(full=True):
    today = datetime.datetime.now().strftime("%Y-%m-%d")
    backup_dir = "backups"
    os.makedirs(backup_dir, exist_ok=True)

    try:
        if full:
            backup_file = os.path.join(backup_dir, f"backup_full_{today}.dump")
            subprocess.run([
                "pg_dump", "-U", "postgres", "-F", "c", "-b", "-v", "-f", backup_file, "bot_db"
            ], check=True)
            print(f"✅ Полный бэкап базы данных выполнен: {backup_file}")
        else:
            wal_dir = os.path.join(backup_dir, "wal")
            os.makedirs(wal_dir, exist_ok=True)
            print(f"ℹ️ Инкрементальный бэкап: нужно настроить archive_command в postgresql.conf")
    except Exception as e:
        print("❌ Ошибка при резервном копировании:", e)


if __name__ == "__main__":
    run_queries()
    backup_database(full=True)
    backup_database(full=False)
    db.close()
