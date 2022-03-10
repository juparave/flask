# Flask Shell

Install iPython for Flask Shell

    $ pip install flask-shell-ipython
  
Example sessioin to set users passwords

```python
from server.model.user import User, Role
from flask_security import hash_password
from server import db
users = db.session.query(User)
users = users.all()
for u in users:
    u.password = hash_password('pass')
db.session.commit()
```
