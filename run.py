from app import create_app, db
from sqlalchemy import create_engine
from sqlalchemy_utils import database_exists, create_database



app = create_app()
engine = create_engine(app.config["SQLALCHEMY_DATABASE_URI"])
if not database_exists(engine.url):
    create_database(engine.url)
    print("Database created")
if __name__ == '__main__':
    with app.app_context():
        db.create_all() # Initialize the database
        
    app.run(debug=True, port=5001)