# Import the dependencies.
from flask import Flask, jsonify, g
from sqlalchemy import create_engine, func
from sqlalchemy.orm import Session, sessionmaker, scoped_session
from sqlalchemy.ext.automap import automap_base
import datetime as dt

#################################################
# Database Setup
#################################################
engine = create_engine(f"sqlite:///C:/Users/cryst/Documents/UMN_Bootcamp/Coursework/Section_3_Databases/Module_10/Homework/sqlalchemy-challenge/SurfsUp/Resources/hawaii.sqlite", connect_args={"check_same_thread": False})

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(autoload_with=engine)

# Save references to each table
measurement = Base.classes.measurement
station = Base.classes.station

# Create our session factory
session_factory = sessionmaker(bind=engine)

# Create our scoped session
session = scoped_session(session_factory)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

# Define the homepage route
@app.route("/")
def home():
    """Homepage with available routes"""
    routes = {
        "routes": [
            "/",
            "/api/v1.0/precipitation",
            "/api/v1.0/stations",
            "/api/v1.0/tobs",
            "/api/v1.0/start_date",
            "/api/v1.0/start_date/end_date"
        ]
    }
    return jsonify(routes)

# Define the /api/v1.0/precipitation route
@app.route("/api/v1.0/precipitation")
def precipitation():
    """Return the last 12 months of precipitation data"""

    # Calculate the date one year ago from the most recent date in the dataset
    last_date = session.query(func.max(measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Perform the query to retrieve the last 12 months of precipitation data
    results = session.query(measurement.date, measurement.prcp).filter(measurement.date >= one_year_ago).all()

    # Convert the query results to a dictionary with date as the key and prcp as the value
    precipitation_data = {date: prcp for date, prcp in results}

    # Return the JSON representation of the dictionary
    return jsonify(precipitation_data)

# Define the /api/v1.0/stations route
@app.route("/api/v1.0/stations")
def stations():
    """Return a list of stations"""
    
    # Perform the query to retrieve all the stations
    results = session.query(station.station).all()

    # Convert the query results to a list
    station_list = [result[0] for result in results]

    # Return the JSON representation of the list
    return jsonify(station_list)

# Calculate the date one year ago from the most recent date in the dataset
last_date = session.query(func.max(measurement.date)).scalar()
one_year_ago = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)

# Query to find the station with the highest number of temperature observations in the past year
most_active_station = session.query(measurement.station, func.count(measurement.tobs)).\
    filter(measurement.date >= one_year_ago).\
    group_by(measurement.station).\
    order_by(func.count(measurement.tobs).desc()).first()[0]

# Define the /api/v1.0/tobs route
@app.route("/api/v1.0/tobs")
def tobs():
    """Return temperature observations for the previous year"""

    # Calculate the date one year ago from the most recent date in the dataset
    last_date = session.query(func.max(measurement.date)).scalar()
    one_year_ago = dt.datetime.strptime(last_date, '%Y-%m-%d') - dt.timedelta(days=365)

    # Perform the query to retrieve the temperature observations for the most active station
    results = session.query(measurement.date, measurement.tobs).\
        filter(measurement.station == most_active_station).\
        filter(measurement.date >= one_year_ago).all()

    # Create a list of dictionaries with date and tobs values
    tobs_list = [{"date": date, "tobs": tobs} for date, tobs in results]

    # Return the JSON representation of the list
    return jsonify(tobs_list)

# Define the /api/v1.0/<start> route
@app.route("/api/v1.0/<string:start>")
def calc_temps_start(start):
    """Calculate TMIN, TAVG, and TMAX for dates greater than or equal to the start date"""
    
    # Convert the start date string to a datetime object
    start_date = dt.datetime.strptime(start, "%Y-%m-%d").date()

    # Perform the query to calculate TMIN, TAVG, and TMAX for the specified start date
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).all()

    # Create a dictionary with the calculated temperature values
    temps_dict = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }

    # Return the JSON representation of the dictionary
    return jsonify(temps_dict)

# Define the /api/v1.0/<start>/<end> route
@app.route("/api/v1.0/<string:start>/<string:end>")
def calc_temps_start_end(start, end):
    """Calculate TMIN, TAVG, and TMAX for dates from the start date to the end date (inclusive)"""
    
    # Convert the start and end date strings to datetime objects
    start_date = dt.datetime.strptime(start, "%Y-%m-%d").date()
    end_date = dt.datetime.strptime(end, "%Y-%m-%d").date()

    # Perform the query to calculate TMIN, TAVG, and TMAX for the specified date range
    results = session.query(func.min(measurement.tobs), func.avg(measurement.tobs), func.max(measurement.tobs)).\
        filter(measurement.date >= start_date).filter(measurement.date <= end_date).all()

    # Create a dictionary with the calculated temperature values
    temps_dict = {
        "TMIN": results[0][0],
        "TAVG": results[0][1],
        "TMAX": results[0][2]
    }

    # Return the JSON representation of the dictionary
    return jsonify(temps_dict)

# Run the Flask app
if __name__ == '__main__':
    app.run(debug=True)