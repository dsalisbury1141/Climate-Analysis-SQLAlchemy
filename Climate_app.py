import numpy as np
import pandas as pd
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func
import datetime as dt
from flask import Flask, jsonify


#################################################
# Database Setup
#################################################
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

#Set up Keys to reflect tables

Measurement = Base.classes.measurement
Station = Base.classes.station



#################################################
# Flask Setup
#################################################
app = Flask(__name__)


#################################################
# Flask Routes
#################################################

@app.route("/")

def welcome():
    """List all available api routes."""
    return (
        f"/Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start<br/>"
        f"/api/v1.0/start/end"
    )
# Query to retrieve the last 12 months of precipitation data and plot the results
# Calculate the date 1 year ago from the last data point in the database

@app.route("/api/v1.0/precipitation")
def precipitation():
    session = Session(engine)

    last_yearDT= dt.date(2017,8, 23) - dt.timedelta(days=365)
    date_query = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_yearDT).all()
  
    session.close()

    P_Date=[]
    for date, prcp in date_query:
        P_Date_dict ={}
        P_Date_dict[date]= prcp
        P_Date.append(P_Date_dict)

        
    #date_query_list = dict(date_query)
    return jsonify(P_Date)
    



@app.route("/api/v1.0/stations")
def stations():
    session = Session(engine)
    stat_query = session.query(Station.station, Station.name).all()
    session.close()

    Stat_name=[]
    for station, name in stat_query:
        Stat_name_dict ={}
        Stat_name_dict[station]= name
        Stat_name.append(Stat_name_dict)                  

    #station_list= list(stations)
    return jsonify(Stat_name)

@app.route("/api/v1.0/tobs")
def tobs():

    session = Session(engine)
    meas_act=session.query(Measurement.station, func.count(Measurement.tobs)).group_by(Measurement.station).\
    order_by(func.count(Measurement.station).desc()).all()
    
    last_yearDT= dt.date(2017,8, 23) - dt.timedelta(days=365)
    date_query = session.query(Measurement.date, Measurement.prcp).filter(Measurement.date >= last_yearDT).all()
    session.close()
    
    most_active = "USC00519281"
    most_act_year = session.query(Measurement.station, Measurement.tobs, Measurement.date).\
    filter(Measurement.station == most_active).\
    filter(Measurement.date >= last_yearDT).all()
    
    
    all_names = list(np.ravel(most_act_year))


    return jsonify(all_names)


@app.route("/api/v1.0/<start>")
def date_start(start):
    session = Session(engine)
    sum_stats = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= start).all()
    session.close()
   
    summary = list(np.ravel(sum_stats))
    return jsonify(summary)
 

@app.route("/api/v1.0/<start>/<end>")
def start_end(start, end):
    print(start)
    print(end)
    session = Session(engine)
    sum_stats2 = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
    filter(Measurement.date >= (start), Measurement.date <= (end)).all()
    session.close()
    

    summary2 = list(np.ravel(sum_stats2))
    return jsonify(summary2)

if __name__ == '__main__':
    app.run(debug=True)
