class EventPost(db.Model):
    # Setup the relationship to the User table
    # Model for the Blog Posts on Website
    id = db.Column(db.Integer, primary_key=True)
    # Notice how we connect the BlogPost to a particular author
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    date = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    title = db.Column(db.String(140), nullable=False)
    text = db.Column(db.Text, nullable=False)
    date_of_event = db.Column(db.DateTime, nullable=False)
    picture = db.Column(db.String(20), nullable=False, default='default_profile.png')

    def __repr__(self):
        return '<BlogPost> %r' % self.title, self.text, self.picture, self.user_id