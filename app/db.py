from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker


engine = create_engine("postgresql+psycopg2://postgres:meow@localhost:5432/tictactoe")

Session = sessionmaker(engine)


def get_session():
    with Session() as session:
        yield session
