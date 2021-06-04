from datetime import datetime
from flask import Flask, request
from flask_restful import Resource, Api
from models import db, Company
from scraper import add_data_to_model, scrape_data, get_data_from_db


app = Flask(__name__)
api = Api(app)
app.config.from_object('config')
db.init_app(app)


@app.before_first_request
def before_first_request():
    global last_scraped_date_dict
    last_scraped_date_dict = dict()
    db.drop_all()
    db.create_all()


class history(Resource):
    def get(self, symbol):
        print(last_scraped_date_dict)
        if not Company.query.filter_by(symbol=symbol).first():
            return app.make_response(
                ({'Status': 'Error', 'Description': f'Firstly you have to add {symbol} into the db'}, 404)
            )
        if datetime.now().date() - last_scraped_date_dict[symbol]:
            add_data_to_model(scrape_data(symbol))
        last_scraped_date_dict[symbol] = datetime.now().date()
        return get_data_from_db(symbol)


class history_without_args(Resource):
    def get(self):
        print(last_scraped_date_dict, 'HIST')
        result = dict()
        for company in Company.query.all():
            symbol = company.symbol
            if not last_scraped_date_dict.get(symbol) or datetime.now().date() - last_scraped_date_dict[symbol]:
                add_data_to_model(scrape_data(symbol))
            last_scraped_date_dict[symbol] = datetime.now().date()
            result[symbol] = get_data_from_db(symbol)
        return result

    def post(self):
        print(last_scraped_date_dict, 'POST')
        symbol = request.get_json(force=True).get('Symbol')
        data = scrape_data(symbol)
        if not data:
            return app.make_response(
                ({'Status': 'Error', 'Description': 'This company does not exist'}, 404)
            )
        if not Company.query.filter_by(symbol=symbol).first():
            add_data_to_model(data)
            last_scraped_date_dict[symbol] = datetime.now().date()
            return {'Status': 'Success', 'Description': f'Successfully added {symbol} into the db'}


api.add_resource(history, '/history/<string:symbol>')
api.add_resource(history_without_args, '/history/')


if __name__ == '__main__':
    app.run()
