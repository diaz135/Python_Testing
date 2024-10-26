import json
import os
import re
from datetime import datetime
from flask import Flask, render_template, request, redirect, flash, url_for
from flask_sqlalchemy import SQLAlchemy

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///:memory:'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)
with app.app_context():
    db.create_all()


class Club(db.Model):
    __tablename__ = 'clubs'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    email = db.Column(db.String(100), unique=True, nullable=False)
    points = db.Column(db.Integer, default=0)


class Competition(db.Model):
    __tablename__ = 'competitions'
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(100), nullable=False)
    date = db.Column(db.DateTime, nullable=False)
    numberOfPlaces = db.Column(db.Integer, default=0)


app.secret_key = os.environ.get('SECRET_KEY', 'something_special')


def loadClubs():
    try:
        with open('clubs.json') as c:
            return json.load(c)['clubs']
    except (FileNotFoundError, json.JSONDecodeError):
        flash("Erreur lors du chargement des clubs.")
        return []


def loadCompetitions():
    try:
        with open('competitions.json') as comps:
            return json.load(comps)['competitions']
    except (FileNotFoundError, json.JSONDecodeError):
        flash("Erreur lors du chargement des compétitions.")
        return []


def validate_email(email):
    """Validation simple de l'email à l'aide d'une regex."""
    email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
    return bool(re.match(email_regex, email))


competitions = loadCompetitions()
clubs = loadClubs()


@app.route('/')
def index():
    return render_template('index.html', clubs=clubs)


@app.route('/showSummary', methods=['POST'])
def showSummary():
    email = request.form['email']

    if not validate_email(email):
        flash("Veuillez entrer une adresse e-mail valide.")
        return redirect(url_for('index'))

    club = next((club for club in clubs if club['email'] == email), None)

    if club:
        current_date = datetime.now()
        future_competitions = [
            comp for comp in competitions
            if datetime.strptime(comp['date'],
                                 '%Y-%m-%d %H:%M:%S') > current_date
        ]
        return render_template('welcome.html', club=club,
                               competitions=future_competitions)
    else:
        flash("Email saisi non reconnu. Veuillez reessayer.")
        return redirect(url_for('index'))


@app.route('/book/<competition>/<club>')
def book(competition, club):
    foundClub = next((c for c in clubs if c['name'] == club), None)
    foundCompetition = next((c for c in competitions if c['name']
                             == competition), None)

    if foundClub and foundCompetition:
        competition_date = datetime.strptime(
            foundCompetition['date'], '%Y-%m-%d %H:%M:%S'
        )
        current_date = datetime.now()

        if competition_date > current_date:
            return render_template('booking.html',
                                   club=foundClub,
                                   competition=foundCompetition)
        else:
            flash("La compétition est déjà passée. Réservation impossible.")
            return redirect(url_for('index'))
    else:
        flash("Erreur : Club ou compétition introuvable.")
        return redirect(url_for('index'))


@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition_name = request.form['competition']
    club_name = request.form['club']
    placesRequired = request.form['places']

    competition = next((c for c in competitions
                        if c['name'] == competition_name), None)
    club = next((c for c in clubs
                 if c['name'] == club_name), None)

    if not placesRequired.isdigit() or int(placesRequired) <= 0:
        flash("Le nombre de places doit etre un entier positif.")
        return render_template('booking.html',
                               club=club,
                               competition=competition)

    placesRequired = int(placesRequired)

    if placesRequired > 12:
        flash("Vous ne pouvez pas reserver plus de 12 places.")
        return render_template('booking.html',
                               club=club,
                               competition=competition)

    if not competition or not club:
        flash('Erreur lors de la réservation. '
              'Compétition ou club introuvable.')
        return render_template('booking.html',
                               club=club,
                               competition=competition)

    if placesRequired > int(competition['numberOfPlaces']):
        flash("Pas assez de places disponibles pour cette compétition.")
        return render_template('booking.html',
                               club=club,
                               competition=competition)

    total_points_needed = placesRequired
    if int(club['points']) >= total_points_needed:
        club['points'] = int(club['points']) - total_points_needed
        competition['numberOfPlaces'] = int(competition['numberOfPlaces']) \
            - placesRequired
        flash(f"Reservation reussie ! Vous avez reserve "
              f"{placesRequired} places.")
    else:
        flash("Pas assez de points pour reserver ces places.")
        return render_template('booking.html',
                               club=club,
                               competition=competition)

    current_date = datetime.now()
    future_competitions = [
        comp for comp in competitions
        if datetime.strptime(comp['date'], '%Y-%m-%d %H:%M:%S') > current_date
    ]

    return render_template('welcome.html',
                           club=club,
                           competitions=future_competitions)


@app.route('/logout')
def logout():
    return redirect(url_for('index'))


if __name__ == "__main__":
    app.run(debug=True)
