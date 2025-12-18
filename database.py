import psycopg2
from psycopg2.extras import DictCursor
import os
from dotenv import load_dotenv

load_dotenv()

class Database:
    def __init__(self):
        self.connection = None
        self.connect()
    
    def connect(self):
        """Подключение к PostgreSQL"""
        try:
            self.connection = psycopg2.connect(
                host=os.getenv('DB_HOST', 'localhost'),
                port=os.getenv('DB_PORT', '5433'),
                database=os.getenv('DB_NAME', 'bot_db'),
                user=os.getenv('DB_USER', 'postgres'),
                password=os.getenv('DB_PASSWORD', '1234')
            )
            print("✅ Подключение к базе данных установлено")
        except Exception as e:
            print(f"❌ Ошибка подключения к базе данных: {e}")
            raise
    
    def get_countries(self):
        """Получить все страны"""
        try:
            with self.connection.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("SELECT id, name FROM countries ORDER BY name")
                return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка при получении стран: {e}")
            return []
    
    def get_universities_by_country(self, country_name):
        """Получить университеты по названию страны"""
        try:
            with self.connection.cursor(cursor_factory=DictCursor) as cursor:
                cursor.execute("""
                    SELECT u.id, u.name, u.card, u.website, c.name as country_name
                    FROM universities u
                    JOIN countries c ON u.country_id = c.id
                    WHERE c.name = %s
                    ORDER BY u.name
                """, (country_name,))
                return cursor.fetchall()
        except Exception as e:
            print(f"Ошибка при получении университетов: {e}")
            return []
    
    def get_university_by_name(self, country_name, university_name):
        """Получить полную информацию об университете по названию и стране"""
        try:
            with self.connection.cursor(cursor_factory=DictCursor) as cursor:
                # Получаем основную информацию об университете
                cursor.execute("""
                    SELECT u.id, u.name, u.card, u.website, c.name as country_name
                    FROM universities u
                    JOIN countries c ON u.country_id = c.id
                    WHERE c.name = %s AND u.name = %s
                """, (country_name, university_name))
                
                university = cursor.fetchone()
                if not university:
                    return None
                
                university_id = university['id']
                
                # Получаем программы
                cursor.execute("""
                    SELECT name, degree, language, price 
                    FROM programs 
                    WHERE university_id = %s
                    ORDER BY name
                """, (university_id,))
                programs = cursor.fetchall()
                
                # Получаем документы
                cursor.execute("""
                    SELECT document_list 
                    FROM documents 
                    WHERE university_id = %s
                """, (university_id,))
                documents_row = cursor.fetchone()
                documents = documents_row['document_list'] if documents_row else None
                
                # Получаем стипендии
                cursor.execute("""
                    SELECT description 
                    FROM scholarships 
                    WHERE university_id = %s
                """, (university_id,))
                scholarships_row = cursor.fetchone()
                scholarships = scholarships_row['description'] if scholarships_row else None
                
                # Получаем дедлайны
                cursor.execute("""
                    SELECT description 
                    FROM deadlines 
                    WHERE university_id = %s
                """, (university_id,))
                deadlines_row = cursor.fetchone()
                deadlines = deadlines_row['description'] if deadlines_row else None
                
                # Получаем процесс поступления
                cursor.execute("""
                    SELECT steps 
                    FROM admission_process 
                    WHERE university_id = %s
                """, (university_id,))
                process_row = cursor.fetchone()
                process = process_row['steps'] if process_row else None
                
                # Получаем ссылки
                cursor.execute("""
                    SELECT website, admissions, scholarships 
                    FROM links 
                    WHERE university_id = %s
                """, (university_id,))
                links_row = cursor.fetchone()
                links = {
                    'website': links_row['website'] if links_row and links_row['website'] else '',
                    'admissions': links_row['admissions'] if links_row and links_row['admissions'] else '',
                    'scholarships': links_row['scholarships'] if links_row and links_row['scholarships'] else ''
                } if links_row else {}
                
                return {
                    'id': university['id'],
                    'name': university['name'],
                    'country': university['country_name'],
                    'card': university['card'],
                    'website': university['website'],
                    'programs': self._format_programs(programs),
                    'documents': documents,
                    'scholarships': scholarships,
                    'deadlines': deadlines,
                    'process': process,
                    'links': links
                }
                
        except Exception as e:
            print(f"Ошибка при получении информации об университете: {e}")
            return None
    
    def _format_programs(self, programs):
        """Форматировать список программ в строку"""
        if not programs:
            return "Информация о программах отсутствует"
        
        formatted = "📚 **Программы университета:**\n\n"
        for program in programs:
            formatted += f"• {program['name']} ({program['degree']})\n"
            formatted += f"  Язык: {program['language']}\n"
            formatted += f"  Стоимость: {program['price']}\n\n"
        return formatted
    
    def search_universities_by_direction(self, direction_keywords):
        """Поиск университетов по ключевым словам в направлениях"""
        try:
            with self.connection.cursor(cursor_factory=DictCursor) as cursor:
                # Используем ILIKE для поиска без учета регистра
                query = """
                    SELECT DISTINCT u.id, u.name, u.card, c.name as country_name
                    FROM universities u
                    JOIN countries c ON u.country_id = c.id
                    LEFT JOIN programs p ON u.id = p.university_id
                    WHERE u.card ILIKE ANY(%s) 
                       OR p.name ILIKE ANY(%s)
                    ORDER BY c.name, u.name
                """
                
                # Создаем список поисковых шаблонов
                like_patterns = [f'%{keyword}%' for keyword in direction_keywords]
                
                cursor.execute(query, (like_patterns, like_patterns))
                return cursor.fetchall()
                
        except Exception as e:
            print(f"Ошибка при поиске университетов по направлению: {e}")
            return []
    
    def close(self):
        """Закрыть соединение с базой данных"""
        if self.connection:
            self.connection.close()
            print("Соединение с базой данных закрыто")

# Создаем глобальный экземпляр базы данных
db = Database()