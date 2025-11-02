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
# DATA VISUALIZATION PAGE (Combined Dataset)
# -----------------------------
@app.route('/data')
def data_page():
    # --- Base static dataset (Botpress-style defaults) ---
    base_data = [
        {"title": "USF Bulls vs UCF Knights", "date": "2025-10-25", "location": "USF Stadium", "price": 30},
        {"title": "Buccaneers vs Saints", "date": "2025-11-02", "location": "Raymond James Stadium", "price": 80},
        {"title": "Lightning vs Hurricanes", "date": "2025-11-06", "location": "Amalie Arena", "price": 60},
        {"title": "Rowdies vs Orlando City", "date": "2025-11-14", "location": "Al Lang Stadium", "price": 35},
        {"title": "USF Volleyball vs Miami", "date": "2025-11-10", "location": "Yuengling Center", "price": 22},
        {"title": "USF Basketball vs Florida Gators", "date": "2025-12-05", "location": "Yuengling Center", "price": 35},
        {"title": "Buccaneers vs Falcons", "date": "2025-11-16", "location": "Raymond James Stadium", "price": 85},
        {"title": "Lightning vs Panthers", "date": "2025-11-15", "location": "Amalie Arena", "price": 70},
        {"title": "Rowdies vs Miami FC", "date": "2025-11-25", "location": "Al Lang Stadium", "price": 38},
        {"title": "USF Soccer vs FIU", "date": "2026-01-08", "location": "Corbett Stadium", "price": 18}
    ]

    # --- Events from database ---
    db_events = Event.query.all()
    db_data = [
        {"title": e.title, "date": e.date, "location": e.location, "price": e.price}
        for e in db_events
    ]

    # --- Combine both datasets ---
    all_events = base_data + db_data

    # --- Prepare chart data ---
    avg_price_data = {}
    venue_counts = {}
    date_price_pairs = []

    for e in all_events:
        # average by team
        avg_price_data[e["title"]] = avg_price_data.get(e["title"], []) + [e["price"]]
        # venue distribution
        venue_counts[e["location"]] = venue_counts.get(e["location"], 0) + 1
        # time-series
        date_price_pairs.append((e["date"], e["price"]))

    avg_price_data = {k: sum(v) / len(v) for k, v in avg_price_data.items()}
    date_price_pairs = sorted(date_price_pairs)

    return render_template(
        "data.html",
        avg_price_data=avg_price_data,
        venue_counts=venue_counts,
        date_price_pairs=date_price_pairs
    )

# -----------------------------
# ABOUT PAGE
# -----------------------------
@app.route('/about')
def about():
    return render_template('about.html')

# -----------------------------
# API PAGE – Unified Live Data
# -----------------------------
@app.route('/api')
def api_page():
    """
    Combines Botpress-style Tampa Bay data with new events from the DB.
    """
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

    data = base_data + db_data
    return render_template('api.html', data=data)

# -----------------------------
# MAIN
# -----------------------------
if __name__ == '__main__':
    app.run(debug=True)