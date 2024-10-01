import json
from flask import Flask, render_template, request, redirect, flash, url_for
from datetime import datetime

app = Flask(__name__)
app.secret_key = 'something_special'

# Charger les clubs et compétitions
def loadClubs():
    with open('clubs.json') as c:
        return json.load(c)['clubs']

def loadCompetitions():
    with open('competitions.json') as comps:
        return json.load(comps)['competitions']

competitions = loadCompetitions()
clubs = loadClubs()

# Page d'accueil
@app.route('/')
def index():
    return render_template('index.html', clubs=clubs)

# Afficher le résumé après la connexion
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

# Réserver des places pour une compétition
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

# Pré-commander des places (pré-validation)
@app.route('/prePurchasePlaces', methods=['POST'])
def prePurchasePlaces():
    competition_name = request.form['competition']
    club_name = request.form['club']
    placesRequired = request.form['places']

    # Recherche du club et de la compétition
    competition = next((c for c in competitions if c['name'] == competition_name), None)
    club = next((c for c in clubs if c['name'] == club_name), None)

    # Validation du nombre de places
    if not placesRequired.isdigit() or int(placesRequired) <= 0:
        flash("Le nombre de places doit être un entier positif.")
        return render_template('booking.html', club=club, competition=competition)

    placesRequired = int(placesRequired)

    # Vérification de la limite de 12 places maximum par club
    if placesRequired > 12:
        flash("Vous ne pouvez pas réserver plus de 12 places.")
        return render_template('booking.html', club=club, competition=competition)

    if not competition or not club:
        flash('Erreur lors de la réservation. Compétition ou club introuvable.')
        return render_template('booking.html', club=club, competition=competition)

    # Vérification du nombre de places disponibles
    if placesRequired > int(competition['numberOfPlaces']):
        flash("Il n'y a pas assez de places disponibles pour cette compétition.")
        return render_template('booking.html', club=club, competition=competition)

    # Pré-validation avant réservation
    return render_template('precommit.html', club=club, competition=competition, placesRequired=placesRequired)

# Confirmer l'achat de places
@app.route('/purchasePlaces', methods=['POST'])
def purchasePlaces():
    competition_name = request.form['competition']
    club_name = request.form['club']
    placesRequired = int(request.form['places'])

    competition = next((c for c in competitions if c['name'] == competition_name), None)
    club = next((c for c in clubs if c['name'] == club_name), None)

    # Vérification des points disponibles pour le club
    total_points_needed = placesRequired

    # Vérification de la limite de 12 places maximum par club
    if placesRequired > 12:
        flash("Vous ne pouvez pas réserver plus de 12 places.")
        return render_template('booking.html', club=club, competition=competition)

    if int(club['points']) >= total_points_needed:
        club['points'] = int(club['points']) - total_points_needed
        competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - placesRequired
        flash(f"Réservation réussie ! Vous avez réservé {placesRequired} places.")
    else:
        flash("Vous n'avez pas assez de points pour réserver ces places.")
        return render_template('booking.html', club=club, competition=competition)

    # Mise à jour des compétitions futures après la réservation
    current_date = datetime.now()
    future_competitions = [comp for comp in competitions if datetime.strptime(comp['date'], '%Y-%m-%d %H:%M:%S') > current_date]

    return render_template('welcome.html', club=club, competitions=future_competitions)

# Déconnexion
@app.route('/logout')
def logout():
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
