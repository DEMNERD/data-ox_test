import json
from datetime import datetime
from flask import Flask
from flask_restful import Resource, Api
from models import db, Record
from scraper import add_data_to_model, get_data


app = Flask(__name__)
api = Api(app)
last_scraped_date_dict = dict()
app.config.from_object('config')
db.init_app(app)


@app.before_first_request
def before_first_request():
    db.drop_all()
    db.create_all()


class history(Resource):
    def get(self, symbol):
        if not last_scraped_date_dict.get(symbol) or datetime.now().date() - last_scraped_date_dict[symbol]:
            add_data_to_model(get_data(symbol))
        result = []
        for record in Record.query.all():
            result.append({
                'date': datetime.strftime(record.date, '%d-%m-%Y'),
                'high': record.high,
                'low': record.low,
                'close': record.close,
                'adj_close': record.adj_close,
                'volume': record.volume
            })
        last_scraped_date_dict[symbol] = datetime.now().date()
        return result


api.add_resource(history, '/history/<string:symbol>')


if __name__ == '__main__':
    app.run()
