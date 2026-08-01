#!/usr/bin/env python3
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), "..", "backend"))
from app.core.database import Base, engine
from app import models

def main():
    print("Creating tables:")
    for table_name in Base.metadata.tables:
        print(f"  - {table_name}")
    Base.metadata.create_all(bind=engine)
    print("Done. Tables created (or already existed).")

if __name__ == "__main__":
    main()
