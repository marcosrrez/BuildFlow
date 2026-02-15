"""Initialize the BuildFlow database with all tables."""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from backend.database import Base, engine
import backend.models  # noqa: F401 - registers all models

if __name__ == "__main__":
    print("Creating all tables...")
    Base.metadata.create_all(bind=engine)
    print("Done! Database ready at buildflow.db")
