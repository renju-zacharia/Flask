# -*- coding: utf-8 -*-
"""
Created on Sun Apr 14 22:08:00 2019

@author: RZ0001
"""
    
from flask import Flask, jsonify
import numpy as np
import pandas as pd
import datetime as dt
from datetime import datetime
import sqlalchemy
from sqlalchemy.ext.automap import automap_base
from sqlalchemy.orm import Session
from sqlalchemy import create_engine, func, inspect, desc

engine = create_engine("sqlite:///Resources/hawaii.sqlite" , connect_args={'check_same_thread': False})

# reflect an existing database into a new model
Base = automap_base()
# reflect the tables
Base.prepare(engine, reflect=True)

# We can view all of the classes that automap found
Base.classes.keys()

# Save references to each table
Measurement = Base.classes.measurement
Station = Base.classes.station

# Create our session (link) from Python to the DB
session = Session(engine)

max_dt = session.query(Measurement.date).\
         group_by(Measurement.date).\
         order_by(desc(Measurement.date)).\
         first()

max_dt_v = datetime.strptime((str(np.ravel(max_dt)[0])), '%Y-%m-%d') 

one_year_b4 = max_dt_v - dt.timedelta(days=365)

print(one_year_b4)

#################################################
# Flask Setup
#################################################
app = Flask(__name__)

#################################################
# Flask Routes
#################################################

@app.route("/api/v1.0/precipitation")
def precipitation():
    """Convert the query results to a Dictionary using `date` as the key and `prcp` as the value"""

    data = session.query(Measurement.date , Measurement.prcp ).\
            filter(Measurement.date > one_year_b4).\
            order_by(Measurement.date).\
            all() 

    data_list = []
    
    for date, prec in data:
        data_dict = {}
        data_dict["date"] = date
        data_dict["prec"] = prec
        data_list.append(data_dict)
        
    return jsonify(data_list)

@app.route("/api/v1.0/station")
def station():
    """Return a JSON list of stations from the dataset"""

    st_data = session.query(Station.station, Station.name).all()

    st_data_list = []
    
    for station, name in st_data:
        st_data_dict = {}
        st_data_dict["station"] = station
        st_data_dict["name"] = name
        st_data_list.append(st_data_dict)
        
    return jsonify(st_data_list)

 
@app.route("/api/v1.0/tobs")
def tobs():
    """query for the dates and temperature observations from a year from the last data point"""
    """Return a JSON list of Temperature Observations (tobs) for the previous year"""

    t_data = session.query(Measurement.date , Measurement.station, Measurement.tobs ).\
                    filter(Measurement.date >= one_year_b4).\
                    order_by(Measurement.date).\
                    all() 

    t_data_list = []
    
    for date, station, tobs in t_data:
        t_data_dict = {}
        t_data_dict["date"] = date
        t_data_dict["station"] = station
        t_data_dict["tobs"] = tobs
        t_data_list.append(t_data_dict)
        
    return jsonify(t_data_list)
 
@app.route("/api/v1.0/<start>")
def start_date(start):
    """query for the dates and temperature observations from a year from the last data point"""
    """Return a JSON list of Temperature Observations (tobs) for the previous year"""

    stat_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
             filter(Measurement.date >= start).\
             all()

    stat_data_list = []
    
    for mini, aver, maxi in stat_data:
        stat_data_dict = {}
        stat_data_dict["minimum"] = mini
        stat_data_dict["average"] = aver
        stat_data_dict["maximum"] = maxi
        stat_data_list.append(stat_data_dict)
        
    return jsonify(stat_data_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end_date(start,end):
    """query for the dates and temperature observations from a year from the last data point"""
    """Return a JSON list of Temperature Observations (tobs) for the previous year"""

    stat_se_data = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).\
             filter(Measurement.date >= start).\
             filter(Measurement.date <= end).\
             all()

    stat_se_data_list = []
    
    for mini_se, aver_se, maxi_se in stat_se_data:
        stat_se_data_dict = {}
        stat_se_data_dict["minimum"] = mini_se
        stat_se_data_dict["average"] = aver_se
        stat_se_data_dict["maximum"] = maxi_se
        stat_se_data_list.append(stat_se_data_dict)
        
    return jsonify(stat_se_data_list)

@app.route("/")
def welcome():
    return (
        f"Welcome to the Hawaii Vacation Weather Analysis API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/station<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/start_date/<br/>"
        f"/api/v1.0/start_date/end_date/<br/>"
    )

if __name__ == "__main__":
    app.run(debug=True)