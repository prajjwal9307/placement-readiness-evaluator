from models.database import init_db

def test_database():
    engine, SessionLocal = init_db()
    print("Database initialized successfully!")
    print("Engine:", engine)

if __name__ == "__main__":
    test_database()