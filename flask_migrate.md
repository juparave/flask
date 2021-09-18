# Flask-Migrate

ref: [Flask Migrate](https://flask-migrate.readthedocs.io/en/latest/)

```python
from flask import Flask
from flask_sqlalchemy import SQLAlchemy
from flask_migrate import Migrate

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///app.db'

db = SQLAlchemy(app)
migrate = Migrate(app, db)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(128))
```

Create a migration repository

    $ flask db init
  
Generate initial migration

    $ flask db migrate -m "Initial migration."
  
Apply the migration to the database

    $ flask db upgrade
  
