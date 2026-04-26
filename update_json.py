import json
import mysql.connector
from mysql.connector import Error

# =========================
# پیکربندی اتصال به دیتابیس
# =========================
DB_HOST = "localhost"
DB_USER = "root"
DB_PASSWORD = ""          # اگر رمز داری اینجا وارد کن
DB_NAME = "library_db"     # نام دیتابیس
DB_TABLE = "books"         # نام جدول کتاب‌ها

# =========================
# تابع اصلی به‌روزرسانی فایل JSON
# =========================
def update_json_from_db():
    try:
        # اتصال به دیتابیس
        connection = mysql.connector.connect(
            host=DB_HOST,
            user=DB_USER,
            password=DB_PASSWORD,
            database=DB_NAME
        )

        if connection.is_connected():
            print("✅ اتصال به دیتابیس برقرار شد.")
            cursor = connection.cursor(dictionary=True)

            # کوئری برای گرفتن همه کتاب‌ها
            query = f"SELECT * FROM {DB_TABLE};"
            cursor.execute(query)
            result = cursor.fetchall()

            if not result:
                print("⚠️ هیچ داده‌ای در جدول پیدا نشد.")
                return

            # ساختاردهی داده‌ها برای JSON
            books_data = []
            for row in result:
                # فرض بر این است که ستون‌ها این‌ها هستند:
                # name, author, translator, publisher, year, edition, version
                books_data.append({
                    "book_name": row.get("book_name", ""),
                    "author": row.get("author", ""),
                    "translator": row.get("translator", ""),
                    "publisher": row.get("publisher", ""),
                    "publish_year": row.get("publish_year", ""),
                    "edition": row.get("edition", ""),
                    "version": row.get("version", ""),
                    "active_loans": [],
                    "loan_history": []
                })

            # نوشتن در فایل JSON
            with open("library_data_fa.json", "w", encoding="utf-8") as json_file:
                json.dump(books_data, json_file, ensure_ascii=False, indent=4)

            print("✅ اطلاعات با موفقیت در فایل 'library_data_fa.json' ذخیره شد!")

    except Error as e:
        print(f"❌ خطا در اتصال یا اجرای کوئری: {e}")

    finally:
        if 'connection' in locals() and connection.is_connected():
            cursor.close()
            connection.close()
            print("🔒 اتصال به دیتابیس بسته شد.")

# اجرای تابع اصلی
if __name__ == "__main__":
    update_json_from_db()
