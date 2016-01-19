from flask import Flask
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///slnky.db'
db = SQLAlchemy(app)
api = Api(app)

class Links(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String, unique=True)
    url = db.Column(db.String)

    def __init__(self, url):
        self.url = url
            
    @staticmethod
    def get_or_create(url):
        result = Links.query.filter_by(url=url).first()
        created = False
        
        if not result:
            result, created = Links(url), True
            db.session.add(result)
            db.session.commit()

        return result, created



