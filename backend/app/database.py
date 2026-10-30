from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from backend.app.config import settings

engine = create_engine(
    settings.DATABASE_URL,
    connect_args={"check_same_thread": False} if "sqlite" in settings.DATABASE_URL else {}
)

SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def init_db_schema():
    from sqlalchemy import text
    Base.metadata.create_all(bind=engine)
    with engine.connect() as conn:
        try:
            res = conn.execute(text("PRAGMA table_info(class_sessions)")).fetchall()
            col_names = [r[1] for r in res]
            if "academic_term" not in col_names:
                conn.execute(text("ALTER TABLE class_sessions ADD COLUMN academic_term VARCHAR(50) DEFAULT 'Semester Ganjil 2026/2027'"))
            if "department" not in col_names:
                conn.execute(text("ALTER TABLE class_sessions ADD COLUMN department VARCHAR(100) DEFAULT 'S1 Manajemen & Akuntansi Bisnis Digital FEB'"))
            if "description" not in col_names:
                conn.execute(text("ALTER TABLE class_sessions ADD COLUMN description TEXT"))
            conn.commit()
        except Exception as e:
            print(f"Schema sync notice: {e}")

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
