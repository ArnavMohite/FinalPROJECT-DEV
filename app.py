from flask import Flask, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)

# -----------------------------
# DATABASE CONFIGURATION
# -----------------------------
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///events.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)

# -----------------------------
# DATABASE MODEL
# -----------------------------
class Event(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    title = db.Column(db.String(200), nullable=False)
    date = db.Column(db.String(100))
    location = db.Column(db.String(200))
    price = db.Column(db.Float)

    def __repr__(self):
        return f"<Event {self.title}>"

# Create database tables if not existing
with app.app_context():
    db.create_all()

# -----------------------------
# ROUTES
# -----------------------------

# HOME PAGE – Manage Events (CRUD)
@app.route('/')
def index():
    events = Event.query.all()
    return render_template('index.html', events=events)

# ADD EVENT
@app.route('/add', methods=['GET', 'POST'])
def add_event():
    if request.method == 'POST':
        title = request.form['title']
        date = request.form['date']
        location = request.form['location']
        price = request.form['price']

        new_event = Event(title=title, date=date, location=location, price=price)
        db.session.add(new_event)
        db.session.commit()
        return redirect(url_for('index'))

    return render_template('add_event.html')

# EDIT EVENT
@app.route('/edit/<int:id>', methods=['GET', 'POST'])
def edit_event(id):
    event = Event.query.get_or_404(id)
    if request.method == 'POST':
        event.title = request.form['title']
        event.date = request.form['date']
        event.location = request.form['location']
        event.price = request.form['price']
        db.session.commit()
        return redirect(url_for('index'))
    return render_template('edit_event.html', event=event)

# DELETE EVENT
@app.route('/delete/<int:id>')
def delete_event(id):
    event = Event.query.get_or_404(id)
    db.session.delete(event)
    db.session.commit()
    return redirect(url_for('index'))

# -----------------------------
# STATIC PAGES
# -----------------------------
@app.route('/data')
def data_page():
    return render_template('data.html')

@app.route('/about')
def about():
    return render_template('about.html')

# -----------------------------
# API PAGE – Unified Live Data
# -----------------------------
@app.route('/api')
def api_page():
    """
    This API view merges default Botpress-style Tampa Bay data
    with any new events added by the user in Manage Events.
    """

    # Base default dataset (Botpress-aligned)
    base_data = [
        {"strEvent": "USF Bulls vs UCF Knights", "dateEvent": "2025-10-25", "venue": "USF Stadium, Tampa", "price": "$30"},
        {"strEvent": "Buccaneers vs Saints", "dateEvent": "2025-11-02", "venue": "Raymond James Stadium", "price": "$80"},
        {"strEvent": "Tampa Bay Lightning vs Hurricanes", "dateEvent": "2025-11-06", "venue": "Amalie Arena", "price": "$60"},
        {"strEvent": "Rowdies vs Orlando City", "dateEvent": "2025-11-14", "venue": "Al Lang Stadium", "price": "$35"},
        {"strEvent": "USF Volleyball vs Miami", "dateEvent": "2025-11-10", "venue": "Yuengling Center", "price": "$22"},
        {"strEvent": "USF Basketball vs Florida Gators", "dateEvent": "2025-12-05", "venue": "Yuengling Center", "price": "$35"},
        {"strEvent": "Buccaneers vs Falcons", "dateEvent": "2025-11-16", "venue": "Raymond James Stadium", "price": "$85"},
        {"strEvent": "Tampa Bay Lightning vs Panthers", "dateEvent": "2025-11-15", "venue": "Amalie Arena", "price": "$70"},
        {"strEvent": "Rowdies vs Miami FC", "dateEvent": "2025-11-25", "venue": "Al Lang Stadium", "price": "$38"},
        {"strEvent": "USF Soccer vs FIU", "dateEvent": "2026-01-08", "venue": "Corbett Stadium", "price": "$18"}
    ]

    # Dynamic data from the database
    db_events = Event.query.all()
    db_data = [
        {
            "strEvent": e.title,
            "dateEvent": e.date,
            "venue": e.location,
            "price": f"${e.price:.2f}"
        }
        for e in db_events
    ]

    # Combine default + user-added events
    data = base_data + db_data

    return render_template('api.html', data=data)

# -----------------------------
# MAIN
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)