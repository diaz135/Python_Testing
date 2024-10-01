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

# Un dictionnaire pour suivre les réservations par club pour chaque compétition
reservations_by_club = {club['name']: {comp['name']: 0 for comp in competitions} for club in clubs}

@app.route('/')
def index():
    return render_template('index.html')

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

        if competition_date > current_date:  # Vérification si la date de compétition est future
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
    placesRequired = int(request.form['places'])
    
    competition = next((c for c in competitions if c['name'] == competition_name), None)
    club = next((c for c in clubs if c['name'] == club_name), None)
    
    if not competition or not club:
        flash('Erreur lors de la réservation. Compétition ou club introuvable.')
        return redirect(url_for('index'))

    # Vérification du nombre de points du club
    total_points_needed = placesRequired
    if int(club['points']) >= total_points_needed:
        # Mettre à jour les points et les places disponibles
        club['points'] = int(club['points']) - total_points_needed
        competition['numberOfPlaces'] = int(competition['numberOfPlaces']) - placesRequired

        # Mettre à jour le nombre total de places réservées par le club
        reservations_by_club[club['name']][competition['name']] += placesRequired

        flash(f"Réservation réussie ! Vous avez réservé {placesRequired} places.")
    else:
        flash("Vous n'avez pas assez de points pour réserver ces places.")
        return redirect(url_for('index'))

    # Filtrer les compétitions futures après la réservation
    current_date = datetime.now()
    future_competitions = [comp for comp in competitions if datetime.strptime(comp['date'], '%Y-%m-%d %H:%M:%S') > current_date]

    return render_template('welcome.html', club=club, competitions=future_competitions)

@app.route('/logout')
def logout():
    return redirect(url_for('index'))

if __name__ == "__main__":
    app.run(debug=True)
