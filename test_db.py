import sqlite3

def test_connection():
    try:
        conn = sqlite3.connect('parking_system.db')
        print("SQLite connection OK")
        conn.close()
    except Exception as e:
        print(f"SQLite connection FAILED: {e}")

if __name__ == "__main__":
    test_connection()
