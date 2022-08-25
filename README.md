# mobile.de scraper
Python script to scrape mobile.de web for cars of interest and send email with the most recent scraped cars. It enables to set up a car make, car model,
year of first registration, fuel type, price range and mileage range. The idea is to run this script on Raspberry PI once a day and get notification via 
mail of newly added cars. It uses mysql as underlying DB but can be used with any relational DB as it uses SQLAlchemy and models. Cheers!


