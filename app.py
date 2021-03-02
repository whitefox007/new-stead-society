from stead import app
from flask import render_template


@app.route('/about')
def about():
    return render_template('about.html', title='About Page')


@app.route('/events')
def events():
    return render_template('events.html', title='Events')


@app.route('/events/space-competition-sierra-leone')
def competition():
    return render_template('space_competition_sierra_leone.html', title='SPACE SCIENCE AND ASTRONOMY COMPETITION IN '
                                                                        'SIERRA LEONE')


if __name__ == '__main__':
    app.run()
