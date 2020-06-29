import requests
import time
from datetime import datetime

BITCOIN_PRICE_THRESHOLD = 10000.00
BITCOIN_API_URL = 'https://pro-api.coinmarketcap.com/v1/cryptocurrency/listings/latest'
IFTTT_WEBHOOKS_URL = 'https://maker.ifttt.com/trigger/{}/with/key/IFTTT API key goes here'

params = {
  'start':'1',
  'limit':'1',
  'convert':'USD',
}

headers = {
  'Accepts': 'application/json',
  'X-CMC_PRO_API_KEY': 'Coinmarket API key goes here,
}

# Get the latest Bitcoin price in USD currency from the Coinmarket API
def get_latest_BTC_price():
    response = requests.get(BITCOIN_API_URL, params=params, headers=headers)
    data = response.json()
    return float("{:.2f}".format(data['data'][0]['quote']['USD']['price']))  # Convert the price to a floating point number

# Post the price or prices to an email or mobile notification depending on the event
def post_ifttt_webhook(event, value):
    data = {'value1': value}    # The payload that will be sent to IFTTT service
    ifttt_event_url = IFTTT_WEBHOOKS_URL.format(event)  # Inserts the desired event
    requests.post(ifttt_event_url, json=data)   # Sends a HTTP POST request to the webhook URL


def format_BTC_history(bitcoin_history):
    rows = []
    for bitcoin_price in bitcoin_history:
        date = bitcoin_price['date'].strftime('%d/%m/%Y %I:%M %p') # Formats the date into a string: '24/02/2018 5:09 PM'
        price = bitcoin_price['price']
        # <b> (bold) tag creates bolded text
        # 24/02/2018 5:09 PM: $<b>10123.4</b>
        row = '{}: $<b>{}</b>'.format(date, price)
        rows.append(row)

    # Use a <br> (break) tag to create a new line
    # Join the rows delimited by <br> tag: row1<br>row2<br>row3
    return '<br>'.join(rows)


def main():
    bitcoin_history = []
    ye_day = datetime.now()
    notification = False
    while True:
        price = get_latest_BTC_price()
        date = datetime.now()
        bitcoin_history.append({'date': date, 'price': price})

        # Send an emergency notification
        if notification:
            if ye_day.day > date.day or ye_day.month > date.month or ye_day.year > date.year:
                notification = False
                ye_day = date
        else:
            if price < BITCOIN_PRICE_THRESHOLD:
                post_ifttt_webhook('bitcoin_price_emergency', price)
                notification = True

        # Send an email notification
        # Once there are 5 items in bitcoin_history send an update
        if len(bitcoin_history) == 5:
            post_ifttt_webhook('bitcoin_price_update', format_BTC_history(bitcoin_history))
            bitcoin_history = []    # Reset the history

        time.sleep(5 * 60)  # Sleep for 5 minutes to wait for Coinmarket API to update

if __name__ == '__main__':
    main()