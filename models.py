from flask_sqlalchemy import SQLAlchemy


db = SQLAlchemy()


class Company(db.Model):
    __tablename__ = 'company'
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    symbol = db.Column(db.String(5), nullable=False)

    def __repr__(self):
        return f'<Company {self.symbol}>'


class Record(db.Model):
    id = db.Column(db.Integer(), primary_key=True, autoincrement=True)
    company_id = db.Column(db.Integer, db.ForeignKey('company.id'))
    company = db.relationship('Company')
    date = db.Column(db.Date())
    open = db.Column(db.Float())
    high = db.Column(db.Float())
    low = db.Column(db.Float())
    close = db.Column(db.Float())
    adj_close = db.Column(db.Float())
    volume = db.Column(db.Integer())
