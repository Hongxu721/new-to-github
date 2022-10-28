from flask import Flask,flash
from flask import session
from flask import render_template
from flask import request
from flask import redirect
from flask import url_for
import mysql.connector
import connect
import datetime

dbconn = None

app = Flask(__name__)
app.secret_key = 'comp636'

def getCursor():
    global dbconn
    global connection
    if dbconn == None:
        connection = mysql.connector.connect(user=connect.dbuser, \
        password=connect.dbpass, host=connect.dbhost, \
        database=connect.dbname, autocommit=True)
        dbconn = connection.cursor()
        return dbconn
    else:
        return dbconn


@app.route("/")
@app.route("/customer/Home")
def customerHome():
    return render_template("customerHome.html")

@app.route("/customer/ArrDepForm", methods=['GET','POST'])
def customerArrDepForm():
    cur = getCursor()
    cur.execute("select AirportName from airport ")
    select_result = cur.fetchall()  
    return render_template("customerArrDepForm.html", airportName=select_result )

@app.route("/customer/ArrDep", methods=['GET','POST'])
def customerArrDep():
    if request.method == "POST":
        departures = request.form.get("depAirport")
        cur = getCursor()
        cur.execute("SELECT f.FlightID as 'Flight ID',a.AirportCode AS 'Airport Code', a.AirportName AS 'Airport Name',f.FlightNum AS 'Flight Number',\
             addtime(FlightDate,DepTime) AS 'Departure Date Time', \
                f.DepEstAct AS 'Departure Estimate/Actual Time',\
                    f.FlightStatus AS 'Flight Status' FROM route r \
                    INNER JOIN airport a ON a.AirPortCode = r.ArrCode \
                        INNER JOIN flight f ON r.FlightNum = f.FlightNum\
                            WHERE addtime(FlightDate,DepTime) >= '2022-10-26 17:00:00' AND\
                                addtime(FlightDate,DepTime) <= '2022-11-02 17:00:00' \
                                    and a.AirportName = %s ORDER BY addtime(FlightDate,DepTime)",(departures,))
        select_result_Dep = cur.fetchall()
        column_names_Dep=[desc[0] for desc in cur.description]
        
        arrivals = request.form.get("arrAirport")
        cur = getCursor()
        cur.execute("SELECT f.FlightID as 'Flight ID',a.AirportCode AS 'Airport Code', \
            a.AirportName AS 'Airport Name',f.FlightNum AS 'Flight Number',\
             addtime(FlightDate,ArrTime) AS 'Arrival Date Time',\
                f.ArrEstAct AS 'Arrival Estimate/Actual Time',f.FlightStatus AS 'Flight Status'\
                    FROM route r \
                    INNER JOIN airport a ON a.AirPortCode = r.ArrCode \
                        INNER JOIN flight f ON r.FlightNum = f.FlightNum\
                            WHERE addtime(FlightDate,ArrTime) >= '2022-10-26 17:00:00' AND\
                                addtime(FlightDate,ArrTime) <= '2022-11-02 17:00:00' \
                                    and a.AirportName = %s ORDER BY addtime(FlightDate,ArrTime)",(arrivals,))
                
        select_result_Arr = cur.fetchall()
        column_names_Arr = [desc[0] for desc in cur.description]
        return render_template("customerArrDep.html", dbresult_Dep=select_result_Dep,\
            dbcols_Dep=column_names_Dep, dbresult_Arr=select_result_Arr, dbcols_Arr=column_names_Arr)   # Use for GET method example
    else:
        return render_template("customerHome.html")


@app.route("/customer/AvailableFlightsForm", methods=["GET","POST"])
def customerAvailableFlightsForm():
    cur = getCursor()
    cur.execute("select AirportName from airport ")
    select_result = cur.fetchall()  
    return render_template("customerAvailableFlightsForm.html", airportName=select_result )
    

@app.route("/customer/AvailableFlights", methods=["GET","POST"])
def customerAvailableFlights():
    if request.method == "POST": 
        depAirport = request.form.get("depAirport")
        cur = getCursor()
        cur.execute("SELECT f.FlightID as 'Flight ID',a.AirportCode AS 'Airport Code',\
         ac.Seating AS 'Full Seating' ,AvailableSeating.AvailableSeating AS 'Available Seating', \
            a.AirportName AS 'Airport Name',f.FlightNum AS 'Flight Number',\
             addtime(FlightDate,ArrTime) AS 'Arrival Date Time',\
                f.ArrEstAct AS 'Arrival Estimate/Actual Time',f.FlightStatus AS 'Flight Status'\
                    FROM route r INNER JOIN airport a ON a.AirPortCode = r.ArrCode\
                        INNER JOIN flight f ON r.FlightNum = f.FlightNum\
							INNER JOIN aircraft ac ON f.Aircraft = ac.RegMark\
				INNER JOIN (SELECT f.flightID, (ac.Seating -COUNT(p.passengerID))\
                    AS AvailableSeating FROM passenger p\
                        INNER JOIN passengerflight pf ON p.PassengerID=pf.PassengerID\
					INNER JOIN flight f ON pf.FlightID = f.FlightID\
					INNER JOIN aircraft ac ON f.Aircraft = ac.RegMark\
					WHERE pf.FlightID = f.FlightID\
					GROUP BY f.flightID) AvailableSeating\
					ON AvailableSeating.FlightID=f.FlightID\
                        WHERE addtime(FlightDate,ArrTime) >= '2022-10-28 17:00:00' \
                            AND addtime(FlightDate,ArrTime) <= '2022-11-04 17:00:00' \
                                AND a.AirportName = %s ORDER BY addtime(FlightDate,ArrTime)", (depAirport,))
        select_result = cur.fetchall()
        column_names=[desc[0] for desc in cur.description]
    return render_template("customerAvailableFlights.html", dbresult=select_result,\
            dbcols=column_names)
   
        
@app.route("/customer/customerBooking", methods=["GET","POST"])
def customerBooking():
       
        return render_template("customerBooking.html")

@app.route("/customer/Login", methods=["GET","POST"])
def customerLogin():
    if request.method == "POST":
        email = request.form.get("email")
        cur = getCursor()
        cur.execute("SELECT EmailAddress FROM passenger WHERE EmailAddress = %s",(email,))
        select_result = cur.fetchall()
# login failed, go to register page
        if len(select_result) > 0:
            session["email"]=select_result[0]
            return render_template("customerBookingsList.html")
# Login succeeded
        else: 
            return render_template("customerRegister.html")        
    else:
        return render_template("customerLogin.html")
    
@app.route("/customer/Logout", methods=["GET","POST"])
def customerLogout():
    session.clear()
    return render_template("customerHome.html")
    
@app.route("/customer/Register", methods=["GET","POST"])
def customerRegister():
    if request.method == "POST":
        firstName = request.form.get("firstName")
        lastName = request.form.get("lastName")
        email = request.form.get("email")
        phone = request.form.get("phone")
        passportNumber = request.form.get("passportNumber")
        dateOfBirth = request.form.get("dateOfBirth")
        cur = getCursor()
        cur.execute("INSERT INTO passenger(FirstName, LastName, EmailAddress, PhoneNumber, PassportNumber, DateOfBirth)\
             VALUES (%s, %s, %s, %s, %s, %s);",(firstName,lastName,email,phone,passportNumber,str(dateOfBirth)))
        return render_template("customerRegister.html")
    else:
        return render_template("customerRegister.html")

@app.route("/customer/BookingsList", methods=["GET","POST"])
def customerBookingsList():
    try: 
        cur = getCursor()
        cur.execute("SELECT * from passenger WHERE EmailAddress = %s;",(session["email"]))
        select_result = cur.fetchall()
        column_names=[desc[0] for desc in cur.description]
        return render_template("customerBookingsList.html", dbresult = select_result, dbcols=column_names)
    except: 
        flash("Please Login to book Flights")
        return render_template("customerBookingErrorPage.html")
    


@app.route("/admin")
def staffHome():
    return render_template("staffHome.html")

@app.route("/admin/staff/BookingEdit")
def staffBookingEdit():
    return render_template("staffBookingEdit.html")

@app.route("/admin/staff/FlightEdit")
def staffFlightEdit():
    return render_template("staffFlightEdit.html")

@app.route("/admin/staff/FlightList")
def staffFlightList():
    cur = getCursor()
    cur.execute("select * from flight ")
    select_result = cur.fetchall()
    column_names = [desc[0] for desc in cur.description]
    return render_template ("staffFlightList.html", dbresult=select_result, dbcols=column_names )

@app.route("/admin/staff/FlightManifest")
def staffFlightManifest():
    return render_template("staffFlightManifest.html")

@app.route("/admin/staff/Login")
def staffLogin():
    return render_template("staffLogin.html")

@app.route("/admin/staff/ManagerPage")
def staffManagerPage():
    return render_template("staffManagerPage.html")

@app.route("/admin/staff/PassengerList")
def staffPassengerList():
    return render_template("staffPassengerList.html")



