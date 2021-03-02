from stead import db
from datetime import datetime


class Project(db.Model):

    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(255), nullable=False)
    content = db.Column(db.TEXT, nullable=False)
    date_posted = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    youtube_id = db.Column(db.String(20))
