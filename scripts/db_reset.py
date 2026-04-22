import subprocess
import os
import sys
import shutil
from argon2 import PasswordHasher
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

# 1. Paths
ROOT_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
SRC_DIR = os.path.join(ROOT_DIR, "src")
ALEMBIC_VERSIONS = os.path.join(ROOT_DIR, "alembic", "versions")
DB_FILE = os.path.join(SRC_DIR, "test.db")

sys.path.append(SRC_DIR)

# 2. Imports
try:
    # Import Base/User/UserRole to ensure they are mapped
    from database import Base 
    from modules.auth.models.user_model import User, UserRole
except ImportError as e:
    print(f"Path Error: {e}")
    sys.exit(1)

ph = PasswordHasher()

def run():
    # Kill old files
    if os.path.exists(DB_FILE):
        os.remove(DB_FILE)
    
    if os.path.exists(ALEMBIC_VERSIONS):
        for item in os.listdir(ALEMBIC_VERSIONS):
            path = os.path.join(ALEMBIC_VERSIONS, item)
            if item == ".gitignore": continue
            shutil.rmtree(path) if os.path.isdir(path) else os.remove(path)

    # Alembic Rebuild
    os.chdir(ROOT_DIR)
    subprocess.run(["alembic", "revision", "--autogenerate", "-m", "init db"], check=True)
    subprocess.run(["alembic", "upgrade", "head"], check=True)

    # 3. Direct Connection (Avoids config mismatches)
    # Use absolute path to the file Alembic just created
    engine = create_engine(f"sqlite:///{DB_FILE}")
    Session = sessionmaker(bind=engine)
    db = Session()

    try:
        admin = User(
            name="admin",
            email="admin@email.com",
            hashed_password=ph.hash("123123123"),
            role=UserRole.ADMIN,
            is_active=True
        )
        db.add(admin)
        db.commit()
        print(f"✓ Success. Admin seeded in {DB_FILE}")
    except Exception as e:
        print(f"× Seed error: {e}")
        db.rollback()
    finally:
        db.close()

if __name__ == "__main__":
    run()