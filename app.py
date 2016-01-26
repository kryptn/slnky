from flask import Flask, redirect, url_for
from flask_restful import Resource, Api
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///slnky.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = True  # to suppress an obnoxious warning
app.config['ERROR_404_HELP'] = False
db = SQLAlchemy(app)
api = Api(app)


class Links(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    slug = db.Column(db.String, unique=True)
    url = db.Column(db.String)

    def __init__(self, url):
        self.url = url

    def slughash(self, key):
        return str(key)

    @property
    def slug_url(self):
        return api.url_for(Redirector,
                           slug=self.slug,
                           _external=True)

    def serialize(self):
        return {'id': self.id,
                'url': self.url,
                'slug': self.slug,
                'slug_url': self.slug_url}

    @staticmethod
    def get_or_create(url):
        result = Links.query.filter_by(url=url).first()

        if not result:
            result = Links(url)
            db.session.add(result)
            db.session.commit()
            result.slug = result.slughash(result.id)
            db.session.commit()

        return result


class Redirector(Resource):

    def get(self, slug):
        # Redirect user to url if available
        result = Links.query.filter_by(slug=slug).first()
        if result:
            return {}, 301, {'Location': result.url}

        # Otherwise redirect to main viewer
        return {}, 302, {'Location': api.url_for(Viewer, slug=None)}


class Viewer(Resource):

    def get(self, slug=None):
        # Show an individual shortened link
        if slug:
            result = Links.query.filter_by(slug=slug).first()
            if result:
                return result.serialize()
            else:
                return {}, 302, {'Location': api.url_for(Viewer, slug=None)}

        # Show all links
        return [link.serialize() for link in Links.query.all()]


class Creator(Resource):

    def get(self, url):
        # On a get request we want to show the viewer
        result = Links.get_or_create(url)
        return {}, 301, {'Location': api.url_for(Viewer, slug=result.slug)}

    def put(self, url):
        # Return the shortened url on PUT
        result = Links.get_or_create(url)
        return {'slug_url': result.slug_url}

api.add_resource(Redirector, '/<string:slug>')
api.add_resource(Viewer, '/v', '/v/<int:slug>')
api.add_resource(Creator, '/c/<path:url>')


@app.before_first_request
def create_db():
    db.create_all()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0')
