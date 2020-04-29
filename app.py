#----------------------------------------------------------------------------#
# Imports
#----------------------------------------------------------------------------#

import json
import dateutil.parser
import babel
from flask import Flask, render_template, request, Response, flash, redirect, url_for
from flask_moment import Moment
from flask_sqlalchemy import SQLAlchemy
import logging
from logging import Formatter, FileHandler
from flask_wtf import FlaskForm
from forms import *
from flask_migrate import Migrate
import sys
from sqlalchemy import func
#----------------------------------------------------------------------------#
# App Config.
#----------------------------------------------------------------------------#

app = Flask(__name__)
moment = Moment(app)
app.config.from_object('config')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS']=False
db = SQLAlchemy(app)

migrate = Migrate(app, db)

# TODO: connect to a local postgresql database

#----------------------------------------------------------------------------#
# Models.
#----------------------------------------------------------------------------#

class Shows(db.Model):
    __tablename__ = 'shows'
    id = db.Column(db.Integer, primary_key=True)
    venue_id = db.Column(db.Integer, db.ForeignKey('venue.id'), nullable=False)
    artist_id = db.Column(db.Integer, db.ForeignKey('artist.id'), nullable=False)
    start_time = db.Column(db.DateTime, nullable=False)
    end_time = db.Column(db.DateTime, nullable=False)

    def __repr__(self):
        return f'<Todo venue_id: {self.venue_id}, artist_id: {self.artist_id}, start_time: {self.start_time}>'

class Venue(db.Model):
    __tablename__ = 'venue'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    address = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    description = db.Column(db.String(500), default='')
    seeking_talent = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120))
    website = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    show_obj = db.relationship('Shows', cascade="all, delete", backref='venue_shows', lazy=True)

    def __repr__(self):
        return f'<Todo id: {self.id}, name: {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

class Artist(db.Model):
    __tablename__ = 'artist'

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String)
    city = db.Column(db.String(120))
    state = db.Column(db.String(120))
    phone = db.Column(db.String(120))
    genres = db.Column(db.String(120))
    image_link = db.Column(db.String(500))
    facebook_link = db.Column(db.String(120))
    seeking_venue = db.Column(db.Boolean, default=False)
    seeking_description = db.Column(db.String(120), default=' ')
    website = db.Column(db.String(120))
    show_obj = db.relationship('Shows', cascade="all, delete", backref='artist_shows', lazy=True)

    def __repr__(self):
        return f'<Todo id: {self.id}, name: {self.name}>'

    # TODO: implement any missing fields, as a database migration using Flask-Migrate

# TODO Implement Show and Artist models, and complete all model relationships and properties, as a database migration.

#----------------------------------------------------------------------------#
# Filters.
#----------------------------------------------------------------------------#

def format_datetime(value, format='medium'):
  date = dateutil.parser.parse(value)
  if format == 'full':
      format="EEEE MMMM, d, y 'at' h:mma"
  elif format == 'medium':
      format="dd, MM, y EE h:mma"
  return babel.dates.format_datetime(date, format)

app.jinja_env.filters['datetime'] = format_datetime

#----------------------------------------------------------------------------#
# Controllers.
#----------------------------------------------------------------------------#

@app.route('/')
def index():
  error = False
  current_time = datetime.now().strftime('%Y-%m-%d %H:%S:%M')
  data=[]
  recent_data={}
  venues=[]
  artists=[]
  try:
      # To list recently added Venues and artists on homepage.
      venue_list = Venue.query.order_by(db.desc(Venue.id)).limit(10).all()
      for venue in venue_list:
        venues.append({
          'id': venue.id,
          'name': venue.name
        })
      recent_data['venues'] = venues
      artist_list = Artist.query.order_by(db.desc(Artist.id)).limit(10).all()
      for artist in artist_list:
        artists.append({
          'id': artist.id,
          'name': artist.name
        })
      recent_data['artists'] = artists
      data.append(recent_data)
  except:
      error= True
      print(sys.exc_info())
  finally:
        if error:
            flash('An error occurred, Please try after sometime. ')
  return render_template('pages/home.html', details=data)


#  Venues
#  ----------------------------------------------------------------

@app.route('/venues')
def venues():
  # Shows all venues saved in database.
  error = False
  current_time = datetime.now().strftime('%Y-%m-%d %H:%S:%M')
  data=[]
  try:
    venues = Venue.query.with_entities(Venue.city, Venue.state).distinct().order_by(Venue.city, Venue.state)
    for venue in venues:
      cities={}
      cities['city'] = venue.city
      cities['state'] = venue.state
      venues=[]
      venue_list = Venue.query.filter_by(city=venue.city, state=venue.state).order_by('id')
      for venue_detail in venue_list:
        # shows_count is aggregated based on number of shows per venue.
        shows_count = Shows.query.with_entities(Shows.venue_id).filter(Shows.venue_id == venue_detail.id , Shows.start_time > current_time).group_by(Shows.venue_id).count()
        venues.append({
          'id': venue_detail.id,
          'name': venue_detail.name,
          'num_upcoming_shows': shows_count
        })
      cities['venues'] = venues
      data.append(cities)
  except:
      error= True
      print(sys.exc_info())
  finally:
        if error:
            flash('An error occurred, Please try after sometime. ')
  return render_template('pages/venues.html', areas=data);
  

@app.route('/venues/search', methods=['POST'])
def search_venues():
  # Case-insensitive search on artists with partial string search.
  error = False
  current_time = datetime.now().strftime('%Y-%m-%d %H:%S:%M')
  response={}
  venues=[]
  venue_search=request.form.get('search_term')
  try:
    venue_list = Venue.query.filter(Venue.name.ilike('%'+venue_search+'%')).all()
    match_count = len(venue_list)
    response['count'] = match_count
    for venue_detail in venue_list:
      # shows_count is aggregated based on number of shows per venue.
      shows_count = Shows.query.with_entities(Shows.venue_id).filter(Shows.venue_id == venue_detail.id , Shows.start_time > current_time).group_by(Shows.venue_id).count()
      venues.append({
        'id': venue_detail.id,
        'name': venue_detail.name,
        'num_upcoming_shows': shows_count
      })
    response['data'] = venues
  except:
      error= True
      print(sys.exc_info())
  finally:
        if error:
            flash('An error occurred, Please try after sometime. ')
  return render_template('pages/search_venues.html', results=response, search_term=venue_search)


@app.route('/venues/<int:venue_id>')
def show_venue(venue_id):
  # shows the venue page with the given venue_id
  error = False
  current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  response={}
  past_shows=[]
  upcoming_shows=[]
  try:
    venue_detail = Venue.query.filter_by(id = venue_id).first()
    response['id'] = venue_detail.id
    response['name'] = venue_detail.name
    response['genres'] =  venue_detail.genres.split(','), # convert string to list
    response['address'] =  venue_detail.address
    response['city'] =  venue_detail.city
    response['state'] =  venue_detail.state
    response['phone'] =  venue_detail.phone
    response['website'] = venue_detail.website
    response['facebook_link'] = venue_detail.facebook_link
    response['seeking_talent'] = venue_detail.seeking_talent
    response['seeking_description']= venue_detail.seeking_description
    response['image_link'] = venue_detail.image_link
    
    shows = Shows.query.filter_by(venue_id = venue_detail.id).order_by('venue_id', 'artist_id')
    for show in shows:
      if format_datetime(str(show.start_time)) > format_datetime(current_time) :
        upcoming_shows.append({
          'artist_id': show.artist_id,
          'artist_name': show.artist_shows.name,
          'artist_image_link': show.artist_shows.image_link,
          'start_time': str(show.start_time),
          'end_time': str(show.end_time)
        })
      else:
        past_shows.append({
            'artist_id': show.artist_id,
            'artist_name': show.artist_shows.name,
            'artist_image_link': show.artist_shows.image_link,
            'start_time': str(show.start_time)
        })
    response['past_shows'] = past_shows
    response['upcoming_shows'] = upcoming_shows
    response['past_shows_count'] = len(past_shows)
    response['upcoming_shows_count'] = len(upcoming_shows)
  except:
      error= True
      print(sys.exc_info())
  finally:
        if error:
            flash('An error occurred, Please try after sometime. ')
  #data = list(filter(lambda d: d['id'] == venue_id, [data1, data2, data3]))[0]
  return render_template('pages/show_venue.html', venue=response)

#  Create Venue
#  ----------------------------------------------------------------

@app.route('/venues/create', methods=['GET'])
def create_venue_form():
  form = VenueForm()
  return render_template('forms/new_venue.html', form=form)

@app.route('/venues/create', methods=['POST'])
def create_venue_submission():
  # insert form data as a new Venue record in the db, instead
  error= False
  try:
    seeking_talent = False
    seeking_description = ''
    if 'seeking_talent' in request.form:
      seeking_talent = request.form['seeking_talent'] == 'y'
    if 'seeking_description' in request.form:
      seeking_description = request.form['seeking_description']
    name = request.form['name']
    genres = request.form.getlist('genres')
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    address = request.form['address']
    website = request.form['website']
    facebook_link = request.form['facebook_link']
    seeking_talent = seeking_talent
    seeking_description = seeking_description
    image_link = request.form['image_link']
    venue = Venue(name = name, genres = genres, city = city, state = state, phone = phone, address = address, website = website, facebook_link = facebook_link, seeking_talent = seeking_talent, seeking_description = seeking_description, image_link = image_link)
    db.session.add(venue)
    db.session.commit()
  except:
    error= True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
        # on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' + request.form['name'] + ' could not be listed.')
    else:
        # on successful db insert, flash success
        flash('Venue ' + name + ' was successfully listed!')
    return redirect(url_for('index'))

  

@app.route('/venues/<venue_id>', methods=['DELETE'])
def delete_venue(venue_id):
  # Implemented a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  error = False
  try:
    Shows.query.filter_by(venue_id = venue_id).delete()
    Venue.query.filter_by(id=venue_id).delete()
    db.session.commit()
  except:
    error= True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
        # on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue could not be deleted.')
    else:
        # on successful db insert, flash success
        flash('Venue was successfully deleted!')
  return redirect(url_for('index'))

#  Artists
#  ----------------------------------------------------------------
@app.route('/artists')
def artists():
  # All artist details stored in the database
  error = False
  data=[]
  artist_list = Artist.query.order_by(Artist.id).all()
  for artist in artist_list:
    data.append({
      'id': artist.id,
      'name': artist.name
    })
  return render_template('pages/artists.html', artists=data)

@app.route('/artists/search', methods=['POST'])
def search_artists():
  # TODO: implement search on artists with partial string search. Ensure it is case-insensitive.
  # seach for "A" should return "Guns N Petals", "Matt Quevado", and "The Wild Sax Band".
  # search for "band" should return "The Wild Sax Band".
  error = False
  current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  response={}
  artists=[]
  artist_search=request.form.get('search_term')
  try:
    artist_list = Artist.query.filter(Artist.name.ilike('%'+artist_search+'%')).all()
    match_count = len(artist_list)
    response['count'] = match_count
    for artist_detail in artist_list:
      # shows_count is aggregated based on number of shows per venue.
      shows_count = Shows.query.with_entities(Shows.artist_id).filter(Shows.artist_id == artist_detail.id , Shows.start_time > current_time).group_by(Shows.artist_id).count()
      artists.append({
        'id': artist_detail.id,
        'name': artist_detail.name,
        'num_upcoming_shows': shows_count
      })
    response['data'] = artists
  except:
      error= True
      print(sys.exc_info())
  finally:
        if error:
            flash('An error occurred, Please try after sometime. ')
  return render_template('pages/search_artists.html', results=response, search_term=artist_search)

@app.route('/artists/<int:artist_id>')
def show_artist(artist_id):
  # shows the venue page with the given venue_id
  # TODO: replace with real venue data from the venues table, using venue_id
  error = False
  current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  response={}
  past_shows=[]
  upcoming_shows=[]
  try:
    artist_detail = Artist.query.filter_by(id = artist_id).first()
    response['id'] = artist_detail.id
    response['name'] = artist_detail.name
    response['genres'] =  artist_detail.genres.split(','), # convert string to list
    response['city'] =  artist_detail.city
    response['state'] =  artist_detail.state
    response['phone'] =  artist_detail.phone
    response['website'] = artist_detail.website
    response['facebook_link'] = artist_detail.facebook_link
    response['seeking_venue'] = artist_detail.seeking_venue
    response['seeking_description']= artist_detail.seeking_description
    response['image_link'] = artist_detail.image_link
    
    shows = Shows.query.filter_by(artist_id = artist_detail.id).order_by('artist_id', 'venue_id')
    for show in shows:
      if format_datetime(str(show.start_time)) > format_datetime(current_time) :
        upcoming_shows.append({
          'venue_id': show.venue_id,
          'venue_name': show.venue_shows.name,
          'venue_image_link': show.venue_shows.image_link,
          'start_time': str(show.start_time),
          'end_time': str(show.end_time)
        })
      else:
        past_shows.append({
          'venue_id': show.venue_id,
          'venue_name': show.venue_shows.name,
          'venue_image_link': show.venue_shows.image_link,
          'start_time': str(show.start_time),
          'end_time': str(show.end_time)
        })
    response['past_shows'] = past_shows
    response['upcoming_shows'] = upcoming_shows
    response['past_shows_count'] = len(past_shows)
    response['upcoming_shows_count'] = len(upcoming_shows)
  except:
      error= True
      print(sys.exc_info())
  finally:
        if error:
            flash('An error occurred, Please try after sometime. ')
  #data = list(filter(lambda d: d['id'] == artist_id, [data1, data2, data3]))[0]
  return render_template('pages/show_artist.html', artist=response)

#  Update
#  ----------------------------------------------------------------
@app.route('/artists/<int:artist_id>/edit', methods=['GET'])
def edit_artist(artist_id):
  form = ArtistForm()
  artist_list = Artist.query.get(artist_id)
  artist={
    "id": artist_id,
    "name": artist_list.name,
    "genres": artist_list.genres,
    "city": artist_list.city,
    "state": artist_list.state,
    "phone": artist_list.phone,
    "website": artist_list.website,
    "facebook_link": artist_list.facebook_link,
    "seeking_venue": artist_list.seeking_venue,
    "seeking_description": artist_list.seeking_description,
    "image_link": artist_list.image_link
  }
  
  # populate form with fields from artist with ID <artist_id>
  form.name.data = artist["name"]
  form.genres.data = artist["genres"]
  form.city.data = artist["city"]
  form.state.data = artist["state"]
  form.phone.data = artist["phone"]
  form.website.data = artist["website"]
  form.facebook_link.data = artist["facebook_link"]
  form.seeking_venue.data = artist["seeking_venue"]
  form.seeking_description.data = artist["seeking_description"]
  form.image_link.data = artist["image_link"]
  return render_template('forms/edit_artist.html', form=form, artist=artist)

@app.route('/artists/<int:artist_id>/edit', methods=['POST'])
def edit_artist_submission(artist_id):
  # TODO: take values from the form submitted, and update existing
  # artist record with ID <artist_id> using the new attributes
  error = False
  form = VenueForm(request.form)
  try:
    if form.validate():
      seeking_venue = False
      seeking_description = ''
      if 'seeking_venue' in request.form:
        seeking_venue = request.form['seeking_venue'] == 'y'
      if 'seeking_description' in request.form:
        seeking_description = request.form['seeking_description']
    artist = Artist.query.get(artist_id)
    artist.name = request.form.get('name')
    artist.genres = request.form.getlist('genres')
    artist.city = request.form.get('city')
    artist.state = request.form.get('state')
    artist.phone = request.form.get('phone')
    artist.website = request.form.get('website')
    artist.facebook_link = request.form.get('facebook_link')
    artist.seeking_venue = request.form['seeking_talent'] == 'y'
    artist.seeking_description = request.form['seeking_description']
    artist.image_link = request.form.get('image_link')
    db.session.commit()
  except:
    error= True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
        # on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Artist ' + request.form.get('name') + ' could not be updated.')
    else:
        # on successful db insert, flash success
        flash('Artist ' + request.form.get('name') + ' was successfully updated!')
  return redirect(url_for('show_artist', artist_id=artist_id))

@app.route('/venues/<int:venue_id>/edit', methods=['GET'])
def edit_venue(venue_id):
  form = VenueForm()
  # populate form with fields from venue with ID <venue_id>
  venue_details = Venue.query.get(venue_id)
  form.name.data = venue_details.name
  form.genres.data = venue_details.genres
  form.address.data = venue_details.address
  form.city.data = venue_details.city
  form.state.data = venue_details.state
  form.phone.data = venue_details.phone
  form.website.data = venue_details.website
  form.facebook_link.data = venue_details.facebook_link
  form.seeking_talent.data = venue_details.seeking_talent
  form.seeking_description.data = venue_details.seeking_description
  form.image_link.data = venue_details.image_link
  venue={
    "id": venue_id,
    "name": venue_details.name,
    "genres": venue_details.genres,
    "address": venue_details.address,
    "city": venue_details.city,
    "state": venue_details.state,
    "phone": venue_details.phone,
    "website": venue_details.website,
    "facebook_link": venue_details.facebook_link,
    "seeking_talent": venue_details.seeking_talent,
    "seeking_description": venue_details.seeking_description,
    "image_link": venue_details.image_link
  }
  # TODO: populate form with values from venue with ID <venue_id>
  return render_template('forms/edit_venue.html', form=form, venue=venue)

@app.route('/venues/<int:venue_id>/edit', methods=['POST'])
def edit_venue_submission(venue_id):
  # TODO: take values from the form submitted, and update existing
  # venue record with ID <venue_id> using the new attributes
  error = False
  form = VenueForm(request.form)
  try:
    venue = Venue.query.get(venue_id)
    venue.name = request.form.get('name')
    venue.genres = request.form.getlist('genres')
    venue.address = request.form.get('address')
    venue.city = request.form.get('city')
    venue.state = request.form.get('state')
    venue.phone = request.form.get('phone')
    venue.website = request.form.get('website')
    venue.facebook_link = request.form.get('facebook_link')
    venue.seeking_talent = request.form['seeking_talent'] == 'y'
    venue.seeking_description = request.form['seeking_description']
    venue.image_link = request.form.get('image_link')
    db.session.commit()
  except:
    error= True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
        # on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Venue ' + request.form.get('name') + ' could not be updated.')
    else:
        # on successful db insert, flash success
        flash('Venue ' + request.form.get('name') + ' was successfully updated!')
  return redirect(url_for('show_venue', venue_id=venue_id))

#  Create Artist
#  ----------------------------------------------------------------

@app.route('/artists/create', methods=['GET'])
def create_artist_form():
  form = ArtistForm()
  return render_template('forms/new_artist.html', form=form)

@app.route('/artists/create', methods=['POST'])
def create_artist_submission():
  # called upon submitting the new artist listing form
  # insert form data as a new Artist record in the db, instead
  error= False
  try:
    seeking_venue = False
    seeking_description = ''
    if 'seeking_venue' in request.form:
      seeking_venue = request.form['seeking_venue'] == 'y'
    if 'seeking_description' in request.form:
      seeking_description = request.form['seeking_description']
    name = request.form['name']
    city = request.form['city']
    state = request.form['state']
    phone = request.form['phone']
    genres = request.form.getlist('genres')
    website = request.form['website']
    facebook_link = request.form['facebook_link']
    seeking_venue = seeking_venue
    seeking_description = seeking_description
    image_link = request.form['image_link']
    # Modify data to be the data object returned from db insertion
    artist = Artist(name = name, city = city, state = state, phone = phone, genres = genres, website = website, facebook_link = facebook_link, seeking_venue = seeking_venue, seeking_description = seeking_description , image_link = image_link)
    db.session.add(artist)
    db.session.commit()
  except:
    error= True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
        # on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Artist ' + request.form['name'] + ' could not be listed.')
    else:
        # on successful db insert, flash success
        flash('Artist ' + name + ' was successfully listed!')
    return redirect(url_for('index'))

@app.route('/artists/<int:artist_id>', methods=['DELETE'])
def delete_artist(artist_id):
  # Implemented a button to delete a Venue on a Venue Page, have it so that
  # clicking that button delete it from the db then redirect the user to the homepage
  error = False
  try:
    Shows.query.filter_by(artist_id = artist_id).delete()
    Artist.query.filter_by(id=artist_id).delete()
    db.session.commit()
  except:
    error= True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if error:
        # on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Artist could not be deleted.')
    else:
        # on successful db insert, flash success
        flash('Artist was successfully deleted!')
  return redirect(url_for('index'))

#  Shows
#  ----------------------------------------------------------------

@app.route('/shows')
def shows():
  # displays list of shows at /shows
  error = False
  data=[]
  try:
    show_list = Shows.query.order_by('venue_id', 'artist_id').all()
    for show in show_list:
      data.append({
        'venue_id': show.venue_id,
        'venue_name': show.venue_shows.name,
        'artist_id': show.artist_id,
        'artist_name': show.artist_shows.name,
        "artist_image_link": show.artist_shows.image_link,
        'start_time': str(show.start_time),
        'end_time': str(show.end_time)
    })
  except:
    error= True
    print(sys.exc_info())
  finally:
    if error:
      flash('An error occurred, Please try after sometime. ')
  return render_template('pages/shows.html', shows=data)

@app.route('/shows/create')
def create_shows():
  # renders form. do not touch.
  form = ShowForm()
  return render_template('forms/new_show.html', form=form)

@app.route('/shows/create', methods=['POST'])
def create_show_submission():
  # called to create new shows in the db, upon submitting new show listing form
  # insert form data as a new Show record in the db, instead
  error= False
  success = False
  current_time = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
  try:
    artist_id = request.form['artist_id']
    venue_id = request.form['venue_id']
    start_time = request.form['start_time']
    end_time = request.form['end_time']
    if (format_datetime(str(end_time)) > format_datetime(str(start_time))):
      if (format_datetime(str(start_time)) >= format_datetime(str(current_time))):
        venue = Venue.query.get(venue_id)
        artist = Artist.query.get(artist_id)
        #Data validation for Venue and artist presence in Database 
        validate = show_validation(venue.id , artist.id , start_time , end_time)
        if validate:
          shows = Shows(venue_id = venue_id, artist_id = artist_id , start_time = start_time , end_time= end_time)
          db.session.add(shows)
          db.session.commit()
          success = True
  except:
    error= True
    db.session.rollback()
    print(sys.exc_info())
  finally:
    db.session.close()
    if not success or error:
        # on unsuccessful db insert, flash an error instead.
        flash('An error occurred. Show could not be listed.')
    else:
        # on successful db insert, flash success
        flash('Show was successfully listed!')
    return redirect(url_for('index'))


# function to validate show creation data  
def show_validation(artist_id , venue_id , start_time , end_time):
    validated = False
    if venue_id is not None and artist_id is not None:
      shows = Shows.query.filter_by(artist_id = artist_id).all()
      if len(shows) > 0:
        for show in shows:
          if (format_datetime(str(show.start_time)) < format_datetime(str(start_time)) 
            and format_datetime(str(show.end_time)) < format_datetime(str(start_time))) or (format_datetime(str(show.start_time)) > format_datetime(str(end_time)) and format_datetime(str(show.end_time)) > format_datetime(str(end_time))):
            validated = True
      else:
        validated = True
    return validated

@app.errorhandler(404)
def not_found_error(error):
    return render_template('errors/404.html'), 404

@app.errorhandler(500)
def server_error(error):
    return render_template('errors/500.html'), 500


if not app.debug:
    file_handler = FileHandler('error.log')
    file_handler.setFormatter(
        Formatter('%(asctime)s %(levelname)s: %(message)s [in %(pathname)s:%(lineno)d]')
    )
    app.logger.setLevel(logging.INFO)
    file_handler.setLevel(logging.INFO)
    app.logger.addHandler(file_handler)
    app.logger.info('errors')

#----------------------------------------------------------------------------#
# Launch.
#----------------------------------------------------------------------------#

# Default port:
if __name__ == '__main__':
    app.run()

# Or specify port manually:
'''
if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
'''
