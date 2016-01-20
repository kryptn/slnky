from flask import Flask
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///slnky.db'
db = SQLAlchemy(app)
api = Api(app)

class Links(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    #slug = db.Column(db.String, unique=True)
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

class Slnky(Resource):
    def get(self, redirect_id):
        rurl = None
        try:
            result = Links.query.get_or_404(redirect_id)
            rurl = result.url
        except NotFound:
            pass

        return {'redirect_id':rurl, 'redirect': True}

    def put(self, url):
        result, created = Links.get_or_create(url)
        return {'redirect_id': result.id,
                'redirect_url': result.url,
                'redirect': False}

api.add_resource(Slnky, '/<int:redirect_id>', '/c/<string:url>')


if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')










