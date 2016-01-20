from flask import Flask, redirect, url_for
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

    @property
    def redirect_url(self):
        return api.url_for(Redirector,
                           redirect_id=self.id,
                           _external=True)
    
    def serialize(self):
        return {'id': self.id,
                'url': self.url,
                'redirect_url': self.redirect_url}
            
    @staticmethod
    def get_or_create(url):
        result = Links.query.filter_by(url=url).first()
        created = False
        
        if not result:
            result, created = Links(url), True
            db.session.add(result)
            db.session.commit()

        return result, created

class Redirector(Resource):

    def get(self, redirect_id):
        redirect_url = None
        try:
            result = Links.query.get_or_404(redirect_id)
            redirect_url = result.url
        except NotFound:
            redirect_url = api.url_for(Viewer, redirect_id=redirect_id)

        return {}, 301, {'Location': redirect_url}

class Viewer(Resource):

    def get(self, redirect_id=None):
        if redirect_id:
            redirect_url = None
            try:
                result = Links.query.get_or_404(redirect_id)
                redirect_url = result.url
            except NotFound:
                pass

            return {'redirect_id':redirect_id,
                    'redirect_url': redirect_url,
                    'slnky_url': result.redirect_url if redirect_url else None,}
        else:
            return [link.serialize() for link in Links.query.all()]


class Slnky(Resource):

    def get(self, url):
        result, created = Links.get_or_create(url)
        return {}, 301, {'Location': api.url_for(Viewer, redirect_id=result.id)}
    
    def put(self, url):
        result, created = Links.get_or_create(url)
        return {'slnky_url': api.url_for(Redirector, redirect_id=result.id, _external=True)}

api.add_resource(Redirector, '/<int:redirect_id>')
api.add_resource(Viewer, '/v', '/v/<int:redirect_id>')
api.add_resource(Slnky, '/c/<path:url>')

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')


