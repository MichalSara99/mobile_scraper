from app import Base
from sqlalchemy import Column,String,Integer,DateTime
from datetime import datetime


class Mobile_cars(Base):
    __tablename__ = 'mobile_cars'
    id = Column(Integer, primary_key=True)
    car_model_id = Column(Integer)
    car_model = Column(String(200))
    car_make_id = Column(Integer)
    car_make = Column(String(200))
    car_make_model_link = Column(String(20000))
    car_title = Column(String(200))
    first_registration = Column(String(200))
    price = Column(String(200))
    mileage = Column(String(200))
    power = Column(String(200))
    zipcode = Column(String(200))
    zipcode_flag = Column(String(1))
    car_ad_link = Column(String(20000))
    download = Column(DateTime)

    def __init__(self,car_model_id,car_model,car_make_id,car_make,
                 car_make_model_link,car_title,first_registration,price,mileage,power,
                 zipcode,zipcode_flag,car_ad_link,download):
        self.car_model_id = car_model_id
        self.car_model = car_model
        self.car_make_id = car_make_id
        self.car_make = car_make
        self.car_make_model_link = car_make_model_link
        self.car_title = car_title
        self.first_registration = first_registration
        self.price = price
        self.mileage = mileage
        self.power = power
        self.zipcode = zipcode
        self.zipcode_flag = zipcode_flag
        self.car_ad_link = car_ad_link
        self.download = download


class Mobile_sent_cars(Base):
    __tablename__ = 'mobile_sent_cars'
    id = Column(Integer, primary_key=True)
    car_model_id = Column(Integer)
    car_model = Column(String(200))
    car_make_id = Column(Integer)
    car_make = Column(String(200))
    car_make_model_link = Column(String(20000))
    car_title = Column(String(200))
    first_registration = Column(String(200))
    price = Column(String(200))
    mileage = Column(String(200))
    power = Column(String(200))
    zipcode = Column(String(200))
    car_ad_link = Column(String(20000))
    insert = Column(DateTime)

    def __init__(self,car_model_id,car_model,car_make_id,car_make,
                 car_make_model_link,car_title,first_registration,price,mileage,power,
                 zipcode,car_ad_link):
        self.car_model_id = car_model_id
        self.car_model = car_model
        self.car_make_id = car_make_id
        self.car_make = car_make
        self.car_make_model_link = car_make_model_link
        self.car_title = car_title
        self.first_registration = first_registration
        self.price = price
        self.mileage = mileage
        self.power = power
        self.zipcode = zipcode
        self.car_ad_link = car_ad_link
        self.insert = datetime.now()
