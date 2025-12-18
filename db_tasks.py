from database import db
import subprocess
from psycopg2 import sql
import os
import datetime

def run_queries():
    """
    Выполнение SQL-запросов для проекта:
    - Простые SELECT/INSERT/UPDATE
    - Сложные JOIN, GROUP BY, подзапросы
    - Оптимизация (индексы, фильтры, лимиты)
    - Создание VIEW для аналитики
    - Автообновление данных
    """
    try:
        with db.connection.cursor() as cursor:
            # -----------------------------
            # 1️⃣ Простые запросы
            # -----------------------------
            cursor.execute("SELECT id, name FROM countries ORDER BY name;")
            countries = cursor.fetchall()
            print("✅ Страны:", countries)

            cursor.execute("""
                SELECT u.id, u.name, u.card, u.website
                FROM universities u
                JOIN countries c ON u.country_id = c.id
                WHERE c.name = %s
                ORDER BY u.name;
            """, ('Germany',))
            universities = cursor.fetchall()
            print("✅ Университеты в Германии:", universities)

            cursor.execute("""
                INSERT INTO universities (name, country_id, card, website)
                VALUES (%s, %s, %s, %s)
                RETURNING id;
            """, ('New Uni', 1, 'Описание карточки', 'https://newuni.edu'))
            new_uni_id = cursor.fetchone()[0]
            print("✅ Добавлен новый университет с id:", new_uni_id)

            cursor.execute("""
                UPDATE programs
                SET price = 12000
                WHERE name = %s AND university_id = %s;
            """, ('Computer Science', 1))
            print("✅ Обновлены цены программ.")

            # -----------------------------
            # 2️⃣ Сложные запросы
            # -----------------------------
            cursor.execute("""
                SELECT u.name AS university_name, c.name AS country_name, COUNT(p.id) AS programs_count
                FROM universities u
                JOIN countries c ON u.country_id = c.id
                LEFT JOIN programs p ON u.id = p.university_id
                GROUP BY u.id, u.name, c.name
                ORDER BY programs_count DESC;
            """)
            overview = cursor.fetchall()
            print("✅ Обзор университетов с количеством программ:", overview)

            cursor.execute("""
                SELECT u.name, u.card, c.name AS country_name
                FROM universities u
                JOIN countries c ON u.country_id = c.id
                WHERE u.id IN (
                    SELECT university_id FROM programs WHERE name ILIKE %s
                )
                ORDER BY u.name;
            """, ('%business%',))
            business_unis = cursor.fetchall()
            print("✅ Университеты по направлению 'Business':", business_unis)

            # -----------------------------
            # 3️⃣ Оптимизация: индексы
            # -----------------------------
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_programs_name ON programs(name);")
            cursor.execute("CREATE INDEX IF NOT EXISTS idx_universities_country ON universities(country_id);")
            print("✅ Индексы созданы/проверены.")

            cursor.execute("""
                SELECT u.name, c.name AS country_name
                FROM universities u
                JOIN countries c ON u.country_id = c.id
                WHERE u.name ILIKE %s
                ORDER BY u.name
                LIMIT 10;
            """, ('%tech%',))
            limited_unis = cursor.fetchall()
            print("✅ Поиск университетов с лимитом 10:", limited_unis)

            # -----------------------------
            # 4️⃣ Создание VIEW для аналитики
            # -----------------------------
            cursor.execute("""
                CREATE OR REPLACE VIEW university_overview AS
                SELECT u.id, u.name AS university_name, c.name AS country_name, COUNT(p.id) AS programs_count
                FROM universities u
                JOIN countries c ON u.country_id = c.id
                LEFT JOIN programs p ON u.id = p.university_id
                GROUP BY u.id, u.name, c.name;
            """)
            print("✅ VIEW university_overview создан/обновлен.")

            # -----------------------------
            # 5️⃣ Автообновление данных (например, цены программ)
            # -----------------------------
            cursor.execute("""
                UPDATE programs
                SET price = price * 1.05
                WHERE updated_at < NOW() - INTERVAL '30 days';
            """)
            print("✅ Цены программ обновлены автоматически.")

            db.connection.commit()
    
    except Exception as e:
        print("❌ Ошибка при выполнении SQL-запросов:", e)
        db.connection.rollback()


# -----------------------------
# Резервное копирование
# -----------------------------
def backup_database(full=True):
    """
    Полный и инкрементальный бэкап базы данных.
    Полный: создается полный дамп базы.
    Инкрементальный: копируются только изменения через WAL (настроить архивирование PostgreSQL)
    """
    try:
        today = datetime.datetime.now().strftime("%Y-%m-%d")
        backup_dir = "backups"
        os.makedirs(backup_dir, exist_ok=True)

        if full:
            backup_file = os.path.join(backup_dir, f"backup_full_{today}.dump")
            subprocess.run([
                "pg_dump", "-U", "postgres", "-F", "c", "-b", "-v", "-f", backup_file, "bot_db"
            ], check=True)
            print(f"✅ Полный бэкап базы данных выполнен: {backup_file}")
        else:
            # Инкрементальный бэкап через WAL-архив
            wal_dir = os.path.join(backup_dir, "wal")
            os.makedirs(wal_dir, exist_ok=True)
            print(f"ℹ️ Инкрементальный бэкап: нужно настроить archive_command в postgresql.conf")
            print(f"Сохраняются WAL-файлы в директорию: {wal_dir}")

    except Exception as e:
        print("❌ Ошибка при резервном копировании:", e)


if __name__ == "__main__":
    # Выполнение всех SQL-запросов и операций
    run_queries()

    # Резервное копирование: сначала полный, потом можно запускать инкрементальный
    backup_database(full=True)
    backup_database(full=False)

    # Закрываем соединение
    db.close()
