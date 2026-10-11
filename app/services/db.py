from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session
from app.models import Base

class Database:
    def __init__(self, db_url="sqlite:///data/critical_save.db"):
        if "sqlite:///" in db_url and not db_url.startswith("sqlite:///:memory:"):
            import os
            db_path = db_url.replace("sqlite:///", "")
            parent_dir = os.path.dirname(os.path.abspath(db_path))
            if parent_dir:
                os.makedirs(parent_dir, exist_ok=True)
        self.engine = create_engine(db_url, connect_args={"check_same_thread": False} if "sqlite" in db_url else {})
        self.SessionFactory = sessionmaker(bind=self.engine)
        self.session = scoped_session(self.SessionFactory)

    def init_db(self):
        Base.metadata.create_all(self.engine)

db = None

def get_db():
    global db
    return db
