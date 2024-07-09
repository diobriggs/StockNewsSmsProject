import requests
from twilio.rest import Client
import datetime as dt
import os


STOCK = "TSLA"
COMPANY_NAME = "Tesla Inc"
twilio_account_sid = os.environ.get("TWILIO_ACCOUNT_SID")
twilio_auth_token = os.environ.get("TWILIO_AUTH_TOKEN")
alpha_api_key = os.environ.get("ALPHA_API_KEY")
news_api_key = os.environ.get("NEWS_API_KEY")
from_phone_no = os.environ.get("FROM_PHONE_NO")
to_phone_no = os.environ.get("TO_PHONE_NO")


now = dt.datetime.now()
today = now.date()
yesterday = today - dt.timedelta(days = 1)
weekday = now.weekday()


if weekday > 4:
    if weekday == 5:
        today = today - dt.timedelta(days = 1)
        yesterday = today - dt.timedelta(days=2)
    elif weekday == 6:
        today = today - dt.timedelta(days=2)
        yesterday = today - dt.timedelta(days=3)
elif weekday == 0:
    yesterday = today - dt.timedelta(days=3)



try:
    stock_response = requests.get(f"https://www.alphavantage.co/query?function=TIME_SERIES_DAILY&symbol={STOCK}&apikey={alpha_api_key}")
    stock_meta_data = stock_response.json()
    today_stock_price = stock_meta_data["Time Series (Daily)"][str(today)]["4. close"]
    yesterday_stock_price = stock_meta_data["Time Series (Daily)"][str(yesterday)]["4. close"]
    difference_in_price = float(today_stock_price) - float(yesterday_stock_price)
    print(f"Today Price: {today_stock_price}")
    print(f"Yesterday Price: {yesterday_stock_price}")
    print(f"Difference in Price: {round(difference_in_price, 2)}")
    percentage_inc_dec = (difference_in_price/float(yesterday_stock_price))*100



except KeyError as e:
    print(f"Data for {e} not found in stock data.")

else:
    ## STEP 1: Use https://www.alphavantage.co
    # When STOCK price increase/decreases by 5% between yesterday and the day before yesterday then print("Get News").
    if abs(percentage_inc_dec) >= 5:
        ## STEP 2: Use https://newsapi.org
        # Instead of printing ("Get News"), actually get the first 3 news pieces for the COMPANY_NAME.
        news_response = requests.get(f"https://newsapi.org/v2/everything?q={COMPANY_NAME}&from=2024-07-05&sortBy=popularity&apiKey={news_api_key}")
        news_meta_data = news_response.json()
        news_articles = news_meta_data["articles"]
        articles_to_send = []
        for article in news_articles[0:4]:
            article_title = article["title"]
            article_description = article["description"]
            articles_to_send.append({"title": article_title, "description": article_description})
        for article in articles_to_send:
            client = Client(twilio_account_sid, twilio_auth_token)
            headline = article['title']
            brief = article['description']
            if percentage_inc_dec > 0:
                ## STEP 3: Use https://www.twilio.com
                # Send a seperate message with the percentage change and each article's title and description to your phone number.
                up_message = client.messages \
                    .create(
                    body=f"️{STOCK} 🔺 {int(percentage_inc_dec)}\nHeadline: {headline}\nBrief: {brief} ",
                    from_= from_phone_no,
                    to=to_phone_no,
                )
                print(up_message.status)
            else:
                down_message = client.messages \
                    .create(
                    body=f"️{STOCK} 🔻 {int(percentage_inc_dec)}\nHeadline: {article['title']}\nBrief: {article['description']} ",
                    from_=from_phone_no,
                    to=to_phone_no,
                )
                print(down_message.status)


#Optional: Format the SMS message like this: 
"""
TSLA: 🔺2%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
or
"TSLA: 🔻5%
Headline: Were Hedge Funds Right About Piling Into Tesla Inc. (TSLA)?. 
Brief: We at Insider Monkey have gone over 821 13F filings that hedge funds and prominent investors are required to file by the SEC The 13F filings show the funds' and investors' portfolio positions as of March 31st, near the height of the coronavirus market crash.
"""

