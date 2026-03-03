from database import engine, Base

def clear_all_data():
    metadata = Base.metadata
    
    with engine.begin() as connection:
        for table in reversed(metadata.sorted_tables):
            connection.execute(table.delete())
