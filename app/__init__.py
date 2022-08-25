from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from config import config,Config

engine = create_engine(config['development'].SQLALCHEMY_DATABASE_URI)
Session = sessionmaker(bind = engine)
Base = declarative_base()
