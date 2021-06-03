from datetime import datetime
from flask import Flask
from flask_restful import Resource, Api
from models import db, Record, Company
from scraper import add_data_to_model, scrape_data, get_data_from_db


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
            add_data_to_model(scrape_data(symbol))
        last_scraped_date_dict[symbol] = datetime.now().date()
        return get_data_from_db(symbol)


class history_of_all_symbols_in_database(Resource):
    def get(self):
        result = dict()
        for company in Company.query.all():
            symbol = company.symbol
            if not last_scraped_date_dict.get(symbol) or datetime.now().date() - last_scraped_date_dict[symbol]:
                add_data_to_model(scrape_data(symbol))
            last_scraped_date_dict[symbol] = datetime.now().date()
            result[symbol] = get_data_from_db(symbol)
        return result


api.add_resource(history, '/history/<string:symbol>')
api.add_resource(history_of_all_symbols_in_database, '/history/')


if __name__ == '__main__':
    app.run()
