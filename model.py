from config import app
from flask_sqlalchemy import SQLAlchemy
# from datetime import datetime, timedelta
import logging

db = SQLAlchemy(app=app)

"""verificar de hosts estão cadastrados
"""
def agent_exists(db, hostname: str) -> bool:
    if db.session.query(Host).filter_by(hostname=hostname).count() < 1:
        return False
    return True

class Host(db.Model):
    __tablename__ = 'hosts'

    id = db.Column(db.Integer, primary_key=True)
    hostname = db.Column(db.String(50))
    apikey = db.Column(db.String(64))
    ip = db.Column(db.String(15))
    sha = db.Column(db.String(64))

    def __repr__(self):
        return '<Host %r>' % self.hostname

db.create_all()

hosts = {
    'test': {'api-key': 't@@wtqibbges@csudk_yfrdqgauzp@ta', 'ip': '127.0.0.1',
    'sha': 'c50bf5ade60439a898d9abde0bf310a4c17cde24'}
}

for hostname, attrs in hosts.items():
    if not agent_exists(db=db, hostname=hostname):
        host_temp = Host(hostname=hostname, apikey=attrs.get('api-key'),
            ip=attrs.get('ip'), sha=attrs.get('sha')) # expire=datetime.now()+timedelta(days=attrs.get('time'))
        logging.debug(' - user "%s" add in database SQLite' % host_temp.hostname)
        db.session.add(host_temp)

try:
    db.session.commit()
except Exception as err:
    db.session.rollback()
    logging.error(' - error to add user(s) in database: %s' % err)
