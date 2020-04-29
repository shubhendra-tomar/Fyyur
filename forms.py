from datetime import datetime
from flask_wtf import FlaskForm
from wtforms import StringField, SelectField, SelectMultipleField, DateTimeField, BooleanField, ValidationError
from wtforms.validators import DataRequired, AnyOf, URL, Length
import re
from enum import Enum, auto

def anyof_for_multiple_field(values):
  message = 'Invalid value, must be one of: {0}.'.format( ','.join(values) )

  def _validate(form, field):
    error = False
    for value in field.data:
      if value not in values:
        error = True

    if error:
      raise ValidationError(message)

  return _validate


class State(Enum):
  AL = 'AL'
  AK = 'AK'
  AZ = 'AZ'
  AR = 'AR'
  CA = 'CA'
  CO = 'CO'
  CT = 'CT'
  DE = 'DE'
  DC = 'DC'
  FL = 'FL'
  GA = 'GA'
  HI = 'HI'
  ID = 'ID'
  IL = 'IL'
  IN = 'IN'
  IA = 'IA'
  KS = 'KS'
  KY = 'KY'
  LA = 'LA'
  ME = 'ME'
  MT = 'MT'
  NE = 'NE'
  NV = 'NV'
  NH = 'NH'
  NJ = 'NJ'
  NM = 'NM'
  NY = 'NY'
  NC = 'NC'
  ND = 'ND'
  OH = 'OH'
  OK = 'OK'
  OR = 'OR'
  MD = 'MD'
  MA = 'MA'
  MI = 'MI'
  MN = 'MN'
  MS = 'MS'
  MO = 'MO'
  PA = 'PA'
  RI = 'RI'
  SC = 'SC'
  SD = 'SD'
  TN = 'TN'
  TX = 'TX'
  UT = 'UT'
  VT = 'VT'
  VA = 'VA'
  WA = 'WA'
  WV = 'WV'
  WI = 'WI'
  WY = 'WY'

  @classmethod
  def choices(cls):
    return [ (choice.value, choice.value) for choice in cls ]

class Genre(Enum):
  Alternative = 'Alternative'
  Blues = 'Blues'
  Classical = 'Classical'
  Country = 'Country'
  Electronic = 'Electronic'
  Folk = 'Folk'
  Funk = 'Funk'
  Hip_Hop = 'Hip-Hop'
  Heavy_Metal = 'Heavy Metal'
  Instrumental = 'Instrumental'
  Jazz = 'Jazz'
  Musical_Theatre = 'Musical Theatre'
  Pop = 'Pop'
  Punk = 'Punk'
  R_AND_B = 'R&B'
  Reggae = 'Reggae'
  Rock_n_Roll = 'Rock n Roll'
  Soul = 'Soul'
  Other = 'Other'

  @classmethod
  def choices(cls):
    return [ (choice.value, choice.value) for choice in cls ]

class ShowForm(FlaskForm):
    artist_id = StringField(
        'artist_id'
    )
    venue_id = StringField(
        'venue_id'
    )
    start_time = DateTimeField(
        'start_time',
        validators=[DataRequired()],
        default= datetime.today()
    )
    end_time = DateTimeField(
        'end_time',
        validators=[DataRequired()],
        default= datetime.today()
    )

class VenueForm(FlaskForm):

    name = StringField(
        'name', validators=[DataRequired()]
    )
    city = StringField(
        'city', validators=[DataRequired(), Length(max=120)]
    )
    state = SelectField(
        'state', validators=[DataRequired(), AnyOf( [ choice.value for choice in State ] )],
        choices=State.choices()
    )
    address = StringField(
        'address', validators=[DataRequired(), Length(max=120)]
    )
    phone = StringField(
        'phone'
    )
    website = StringField(
        'website', validators=[DataRequired(), URL(), Length(max=120)]
    )
    genres = SelectMultipleField(
        'genres', validators=[DataRequired(), anyof_for_multiple_field( [ choice.value for choice in Genre ] )],
        choices=Genre.choices()
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )
    seeking_talent = BooleanField(
        'seeking_talent'
    )
    seeking_description = StringField(
        'seeking_description', validators=[Length(max=500)]
    )
    image_link = StringField(
        'image_link', validators=[DataRequired(), URL(), Length(max=500)]
    )

# IMPLEMENT NEW ARTIST FORM AND NEW SHOW FORM

class ArtistForm(FlaskForm):
    name = StringField(
        'name', validators=[DataRequired(), Length(max=120)]
    )
    city = StringField(
        'city', validators=[DataRequired(), Length(max=120)]
    )
    state = SelectField(
        # implement validation logic for state
        'state', validators=[DataRequired(), AnyOf( [ choice.value for choice in State ] )],
        choices=State.choices()
    )
    phone = StringField(
        'phone'
    )
    genres = SelectMultipleField(
        # implement enum restriction
        'genres', validators=[DataRequired(), anyof_for_multiple_field( [ choice.value for choice in Genre ] )],
        choices=Genre.choices()
    )
    seeking_venue = BooleanField(
        'seeking_venue'
    )
    seeking_description = StringField(
        'seeking_description', validators=[Length(max=500)]
    )
    website = StringField(
        'website', validators=[DataRequired(), URL(), Length(max=120)]
    )
    image_link = StringField(
        'image_link', validators=[DataRequired(), URL(), Length(max=500)]
    )
    facebook_link = StringField(
        'facebook_link', validators=[URL()]
    )
