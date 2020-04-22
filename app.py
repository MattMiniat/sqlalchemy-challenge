import datetime as dt
import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
from flask import Flask, jsonify


# Database Setup
engine = create_engine("sqlite:///hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# Attempted to save references to table, however I keep recieving attribute errors for some reason.
#   Measurements = Base.classes.measurement
#   Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)


# Flask Setup
app = Flask(__name__)

# Flask Routes

@app.route("/")
def welcome():
    return (
        f"Hawaii Climate Analysis API<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/temp/start/end"
    )


@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the precipitation data for the last year"""
    # Calculate the date 1 year ago from last date in database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query for the date and precipitation of last year
    measurements = session.query(Base.classes.measurement.date, Base.classes.measurement.prcp).filter(Base.classes.measurement.date >= prev_year).all()

    # Dict with date as the key and prcp as the value
    precipitation = {date: prcp for date, prcp in measurements}
    return jsonify(precipitation)


@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations."""
    station_list = session.query(Base.classes.station.station).all()

    # convert to a list
    stations = list(np.ravel(station_list))
    return jsonify(stations)


@app.route("/api/v1.0/tobs")
def temp_monthly():
    """Return the temperature observations (tobs) for previous year."""
    # Calculate the date 1 year ago from last date in database
    prev_year = dt.date(2017, 8, 23) - dt.timedelta(days=365)

    # Query the primary station for all tobs from the last year
    temperatures = session.query(Base.classes.measurement.tobs).filter(Base.classes.measurement.station == 'USC00519281').filter(Base.classes.measurement.date >= prev_year).all()

    # convert to a list and return temperatures
    temps = list(np.ravel(temperatures))
    return jsonify(temps)


@app.route("/api/v1.0/temp/<start>")
@app.route("/api/v1.0/temp/<start>/<end>")
def stats(start=None, end=None):
    """Return TMIN, TAVG, TMAX."""

    # Select statement
    sel = [func.min(Base.classes.measurement.tobs), func.avg(Base.classes.measurement.tobs), func.max(Base.classes.measurement.tobs)]

    if not end:
        # calculate TMIN, TAVG, TMAX for dates greater than start
        results = session.query(*sel).filter(Base.classes.measurement.date >= start).all()
        # convert to list
        temps = list(np.ravel(results))
        return jsonify(temps)

    # calculate TMIN, TAVG, TMAX with start and stop
    results = session.query(*sel).filter(Base.classes.measurement.date >= start).filter(Base.classes.measurement.date <= end).all()
    # convert to list
    temps = list(np.ravel(results))
    return jsonify(temps)


if __name__ == '__main__':
    app.run()
