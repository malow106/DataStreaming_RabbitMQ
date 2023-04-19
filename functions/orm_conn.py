from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
from .models import Base
from dotenv import dotenv_values, load_dotenv

load_dotenv()

CONFIG = dotenv_values("class-4/.env")


def CreateEngine():
    engine = create_engine(
        "mysql+mysqlconnector://%s:%s@localhost:3307/%s" %
        (CONFIG['DB_USER'], CONFIG['DB_PASSWORD'], CONFIG['DB_NAME'])
    )

    # connection = engine.connect()
    Base.metadata.create_all(engine)

    Session = sessionmaker(bind=engine)
    session = Session()

    return session