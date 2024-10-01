import json
from flask import Flask, render_template, request, redirect, flash, url_for
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'something_special'

def loadClubs():
    with open('clubs.json') as c:
        return json.load(c)['clubs']

def loadCompetitions():
    with open('competitions.json') as comps:
        return json.load(comps)['competitions']

competitions = loadCompetitions()
clubs = loadClubs()

@app.route('/')
def index():
    # Passer la liste des clubs à la page d'accueil
    return render_template('index.html', clubs=clubs)

@app.route('/showSummary', methods=['POST'])
def showSummary():
    email = request.form['email']
    club = next((club for club in clubs if club['email'] == email), None)
    
    if club:
        current_date = datetime.now()
        future_competitions = [comp for comp in competitions if datetime.strptime(comp['date'], '%Y-%m-%d %H:%M:%S') > current_date]
        return render_template('welcome.html', club=club, competitions=future_competitions)
    else:
        flash("L'email saisi n'est pas reconnu. Veuillez essayer à nouveau.")
        return redirect(url_for('index'))

@app.route('/book/<competition>/<club>')
def book(competition, club):
    foundClub = next((c for c in clubs if c['name'] == club), None)
    foundCompetition = next((c for c in competitions if c['name'] == competition), None)
    
    if foundClub and foundCompetition:
        competition_date = datetime.strptime(foundCompetition['date'], '%Y-%m-%d %H:%M:%S')
        current_date = datetime.now()

        if competition_date > current_date:
            return render_template('booking.html', club=foundClub, competition=foundCompetition)
        else:
            flash("La compétition est déjà passée. Réservation impossible.")
            return redirect(url_for('index'))
    else:
        flash("Erreur: Club ou compétition introuvable.")
        return redirect(url_for('index'))

@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition_name = request.form['competition']
    club_name = request.form['club']
    placesRequired = request.form['places']

    # Validation si placesRequired est un entier et positif
    if not placesRequired.isdigit() or int(placesRequired) <= 0:
        flash("Le nombre de places doit être un entier positif.")
        return redirect(url_for('index'))

    placesRequired = int(placesRequired)
    
    competition = next((c for c in competitions if c['name'] == competition_name), None)
    club = next((c for c in clubs if c['name'] == club_name), None)
    
    if not competition or not club:
        flash('Erreur lors de la réservation. Compétition ou club introuvable.')
        return redirect(url_for('index'))

    # Vérification des points disponibles
    total_points_needed = placesRequired
    if int(club['points']) >= total_points_needed:
        club['points'] = int(club['points']) - total_points_needed
        competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - placesRequired
        flash(f"Réservation réussie ! Vous avez réservé {placesRequired} places.")
    else:
        flash("Vous n'avez pas assez de points pour réserver ces places.")

    # Filtrer les compétitions futures après la réservation
    current_date = datetime.now()
    future_competitions = [comp for comp in competitions if datetime.strptime(comp['date'], '%Y-%m-%d %H:%M:%S') > current_date]

    return render_template('welcome.html', club=club, competitions=future_competitions)

@app.route('/logout')
def logout():
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
