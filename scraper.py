import time
from datetime import datetime
import requests
import csv
from io import StringIO
from urllib.parse import urlencode
from models import Company, Record, db


def scrape_data(symbol: str, start_date: int = 0, end_date: int = int(time.time())):
    url_params = {
        'period1': start_date,
        'period2': end_date,
        'interval': '1d',
        'events': 'history'
    }
    resp = requests.get(
        f'https://query1.finance.yahoo.com/v7/finance/download/{symbol}?' + urlencode(url_params)
    )

    with StringIO(resp.text) as csv_file:
        reader = csv.reader(csv_file)
        params = next(reader)
        result = []
        for item in reader:
            result.append({params[i]: item[i] for i in range(len(params))})

    return {symbol: result}


def add_data_to_model(data):
    company = Company.query.filter_by(symbol=tuple(data)[0]).first()
    if not company:
        company = Company(symbol=tuple(data)[0])
        db.session.add(company)
    for item in tuple(data.values())[0]:
        if not Record.query.filter_by(company=company, date=datetime.strptime(item['Date'], '%Y-%m-%d').date()).first():
            db.session.add(
                Record(
                    company=company,
                    date=datetime.strptime(item['Date'], '%Y-%m-%d'),
                    open=item['Open'],
                    high=item['High'],
                    low=item['Low'],
                    close=item['Close'],
                    adj_close=item['Adj Close'],
                    volume=item['Volume']
                )
            )
    db.session.commit()


def get_data_from_db(symbol: str):
    result = []
    for record in Record.query.filter_by(company=Company.query.filter_by(symbol=symbol).first()):
        result.append({
            'date': datetime.strftime(record.date, '%d-%m-%Y'),
            'high': record.high,
            'low': record.low,
            'close': record.close,
            'adj_close': record.adj_close,
            'volume': record.volume
        })
    return result
