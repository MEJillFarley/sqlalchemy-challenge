%matplotlib inline
from matplotlib import style
style.use('fivethirtyeight')
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
from flask import Flask, jsonify

# Database Setup
engine = create_engine("sqlite:///Resources/hawaii.sqlite")

from sqlalchemy import inspect
inspector = inspect(engine)

# reflect an existing database into a new model
Base = automap_base()

# reflect the tables
Base.prepare(engine, reflect=True)

# Save reference to the table
Measurement = Base.classes.measurement
Station = Base.classes.station


# Flask Setup
app = Flask(__name__)

# Flask Routes
@app.route("/")
def welcome():
    """List available api routes."""
    return (
        f"Welcome to the Climate APP API!<br/>"
        f"Available Routes:<br/>"
        f"/api/v1.0/precipitation<br/>"
        f"/api/v1.0/stations<br/>"
        f"/api/v1.0/tobs<br/>"
        f"/api/v1.0/[start_date format:yyyy-mm-dd]<br/>"
        f"/api/v1.0/[start_date format:yyyy-mm-dd]/[end_date format:yyyy-mm-dd]<br/>"
    )

@app.route("/api/v1.0/precipitation")
def prcp_date():
    session = Session(engine)
    res=session.query(Measurement.date, Measurement.prcp)
    session.close()

    result=[]
    for date,prcp in res:
        prcp_dict={}
        prcp_dict["date"]=date
        prcp_dict["prcp"]=prcp
        result.append(prcp_dict)
    return jsonify(result)


@app.route("/api/v1.0/stations")
def station_list():
    session = Session(engine)
    res=session.query(Station.name).all()
    session.close()
    all_names = list(np.ravel(res))
    
    return jsonify(all_names)

@app.route("/api/v1.0/tobs")
def tob():
    session = Session(engine)
    most_recent_date=dt.datetime.strptime(session.query(Measurement.date).order_by(Measurement.date.desc()).first()[0], '%Y-%m-%d')
    last_12_months=most_recent_date - dt.timedelta(days=365)
    last_12_months=last_12_months.date()

    most_active_station = session.query(Measurement.station).filter(Measurement.date >= last_12_months)\
       .group_by(Measurement.station).order_by(func.count(Measurement.station).desc()).first()[0] 

    TOBS_ =session.query(Measurement.tobs).filter(Measurement.station == most_active_station).all()
    session.close()
    TOBS = list(np.ravel(TOBS_))
    return jsonify(TOBS)
    
    
@app.route("/api/v1.0/<start>")
def start_day(start):
    session = Session(engine)
    query_ = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start).all()
    start_list=list(np.ravel(query_))
    session.close()
    return jsonify(start_list)

@app.route("/api/v1.0/<start>/<end>")
def start_end_day(start,end):
    session = Session(engine)
    query_ = session.query(func.min(Measurement.tobs), func.avg(Measurement.tobs), func.max(Measurement.tobs)).filter(Measurement.date >= start,Measurement.date<= end).all()
    start_list=list(np.ravel(query_))
    session.close()
    return jsonify(start_list)        



if __name__ == '__main__':
    app.run(debug=True)