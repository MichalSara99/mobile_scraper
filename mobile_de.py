from datetime import datetime
from app.mobile_parser import mobileParser
from app.models import Mobile_cars,Mobile_sent_cars
from app.email import Email
from sqlalchemy import func,and_
from app import Session



def scrapeAndInsert(car_make_str="BMW",car_model_str="Z3",ft="petrol", fr=2002,ml_min=0,
                    ml_max=70000,price_min=0, price_max=20000):
    mobile_df = mobileParser(car_make_str,car_model_str,ft,fr,
                             ml_min,ml_max,price_min,price_max)
    # start DB session
    session = Session()
    try:
        # insert the mobile_de into DB:
        for idx,row in mobile_df.iterrows():
            rec = Mobile_cars(row['car_model_id'],
                              row['car_model'],
                              row['car_make_id'],
                              row['car_make'],
                              row['car_make_model_link'],
                              row['car_title'],
                              row['first_registration'],
                              row['price'],
                              row['mileage'],
                              row['power'],
                              row['zipcode'],
                              row['zipcode_flag'],
                              row['car_ad_link'],
                              row['download'])
            session.add(rec)
        session.commit()
    finally:
        session.close()

def insertIntoSentCars(car_make_str="BMW",car_model_str="Z3"):
    # start DB session
    session = Session()
    try:
        latest_sent_subq0 = session.query(func.max(Mobile_sent_cars.insert).label('latest_insert'))\
                                    .filter(Mobile_sent_cars.car_model == car_model_str,
                                           Mobile_sent_cars.car_make == car_make_str).subquery()
        latest_sent_q = session.query(Mobile_sent_cars.car_title)\
                        .join(latest_sent_subq0,and_(Mobile_sent_cars.insert == latest_sent_subq0.c.latest_insert))\
                        .filter(Mobile_sent_cars.car_model == car_model_str,
                                Mobile_sent_cars.car_make == car_make_str)

        latest_subq0 = session.query(func.max(Mobile_cars.download).label('latest'))\
                        .filter(Mobile_cars.car_model == car_model_str,
                                Mobile_cars.car_make == car_make_str).subquery()
        latest_q = session.query(Mobile_cars.car_model_id,
                                 Mobile_cars.car_model,
                                 Mobile_cars.car_make_id,
                                 Mobile_cars.car_make,
                                 Mobile_cars.car_make_model_link,
                                 Mobile_cars.car_title,
                                 Mobile_cars.first_registration,
                                 Mobile_cars.price,
                                 Mobile_cars.mileage,
                                 Mobile_cars.power,
                                 Mobile_cars.zipcode,
                                 Mobile_cars.car_ad_link) \
                        .join(latest_subq0, and_(Mobile_cars.download == latest_subq0.c.latest))\
                        .filter(Mobile_cars.car_title.not_in(latest_sent_q),Mobile_cars.zipcode_flag=='T')\
                        .filter(Mobile_cars.car_model == car_model_str,
                                Mobile_cars.car_make == car_make_str)\
                        .all()
        for rec in latest_q:
            new_rec = Mobile_sent_cars(rec[0],rec[1],rec[2],rec[3],rec[4],rec[5],
                                       rec[6],rec[7],rec[8],rec[9],rec[10],rec[11])
            session.add(new_rec)
        session.commit()
    finally:
        session.close()

def sentEmailOfRecent(car_make_str="BMW",car_model_str="Z3",email_to="michal.sara99@gmail.com"):
    # start DB session
    session = Session()
    today = datetime.today()
    latest_sent_q = None
    try:
        latest_sent_date = session.query(func.max(Mobile_sent_cars.insert).label('latest_insert'))\
                                .filter(Mobile_sent_cars.car_model == car_model_str,
                                        Mobile_sent_cars.car_make == car_make_str).all()[0][0]
        if latest_sent_date.date() != today.date():
            session.close()
            return

        latest_sent_subq = session.query(func.max(Mobile_sent_cars.insert).label('latest_insert')) \
                                    .filter(Mobile_sent_cars.car_model == car_model_str,
                                            Mobile_sent_cars.car_make == car_make_str).subquery()
        latest_sent_q = session.query(Mobile_sent_cars.car_title,
                                      Mobile_sent_cars.first_registration,
                                      Mobile_sent_cars.price,
                                      Mobile_sent_cars.mileage,
                                      Mobile_sent_cars.power,
                                      Mobile_sent_cars.zipcode,
                                      Mobile_sent_cars.car_ad_link)\
                        .join(latest_sent_subq,and_(Mobile_sent_cars.insert == latest_sent_subq.c.latest_insert))\
                        .all()
    finally:
        session.close()
    # sent the mail:
    subject_postfix = car_make_str + " " + car_model_str
    text_content = """
    New cars been scraped !!

    Hi Michal,
    This is the list of the newly scraped cars:
    
    """
    li=""
    for car in latest_sent_q:
        li = li + "*"
        li = li + car[0] +", "+ car[1]+", "+car[2]+", "+car[3]+", "+car[4]+", "+car[5]+", ("+car[6]+")"
    text_content = text_content + li

    html_content="""
        <h2>New cars been scraped !!</h2>

        <p>Hi Michal,</p>
        <p>This is the list of the newly scraped cars: </p>
        <div><ul>
        """
    li=""
    for car in latest_sent_q:
        li = li + "<li>"
        li = li + car[0] +", "+ car[1]+", "+car[2]+", "+car[3]+", "+car[4]+", "+car[5]+", (<a href="+car[6]+">link</a>)</li>"
    html_content = html_content + li + "</ul>"
    try:
        m = Email()
        m.send(text_content,html_content,subject_postfix,email_to)
        print("Mail successfully sent!")
    except:
        print("Mail failed to be sent!")





def main(car_make_str,car_model_str,ft,fr,ml_min,ml_max,price_min,price_max,email_to):
    scrapeAndInsert(car_make_str=car_make_str,car_model_str=car_model_str,ft=ft, fr=fr,
                    ml_min=ml_min,ml_max=ml_max,price_min=price_min, price_max=price_max)
    insertIntoSentCars(car_make_str=car_make_str,car_model_str=car_model_str)
    sentEmailOfRecent(car_make_str=car_make_str,car_model_str=car_model_str,email_to=email_to)


if __name__ =='__main__':
    main(car_make_str="BMW",car_model_str="Z3",ft="petrol", fr=2002,ml_min=0,
        ml_max=70000,price_min=0, price_max=20000,email_to="michal.sara99@gmail.com")
    main(car_make_str="BMW",car_model_str="Z4",ft="petrol", fr=2007,ml_min=0,
        ml_max=80000,price_min=0, price_max=20000,email_to="michal.sara99@gmail.com")



