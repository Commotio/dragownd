from flask import Flask, render_template, request, redirect
from flask_sqlalchemy import SQLAlchemy
from flask_table import Table, Col
from flask_mysqldb import MySQL
import pandas
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from matplotlib.figure import Figure
import datetime
import matplotlib.dates as mdates
import sys

days =  mdates.DayLocator() # every day
years = mdates.YearLocator()   # every year
months = mdates.MonthLocator()  # every month
years_fmt = mdates.DateFormatter('%Y')
time=datetime.datetime.now().strftime("%Y%m%d-%H%M%S")

app = Flask(__name__)

app.config['MYSQL_HOST'] = '{{ hostvars['db'].ansible_host }}'
app.config['MYSQL_USER'] = 'dragownd'
app.config['MYSQL_PASSWORD'] = '{{ password }}' #CHANGE
app.config['MYSQL_DB'] = 'dragownd'

mysql = MySQL(app)

def line_plot(title,x_title,y_title, x, y, filename, x_date):
    fig, ax = plt.subplots()
    plt.suptitle(title, fontsize=12)
    plt.ylabel(y_title, fontsize=12)
    plt.xlabel(x_title, fontsize=12)
    plt.xticks(rotation=45)
    if x_date == True:
        ax.xaxis.set_major_locator(months)
        ax.xaxis.set_major_formatter(mdates.DateFormatter('%m/%Y'))
        #fit the x axis
        plt.tight_layout()
        #make the plot
        plt.plot(x,y)
        #save the image
        data = "static/images/"+filename
        plt.savefig(data)
    else:
        ax.xaxis.set_major_locator(days)
        ax.xaxis.set_major_formatter(mdates.DateFormatter("%Y-%m-%d"))
        #fit the x axis
        plt.tight_layout()
        #make the plot
        plt.plot(x,y)
        #save the image
        data = "static/images/"+filename
        plt.savefig(data)

def bar_chart(title,x_title,y_title, x, y, x_range, filename):
    fig, ax = plt.subplots()
    plt.suptitle(title, fontsize=12)
    plt.ylabel(y_title, fontsize=12)
    plt.xlabel(x_title, fontsize=12)
    plt.xticks(rotation=45)
    plt.xticks(x_range, x)
    ax.yaxis.get_major_locator().set_params(integer=True)
    #fit the x axis
    plt.tight_layout()
    #make the plot
    plt.bar(x_range,y)
    #save the image
    data = "static/images/"+filename
    plt.savefig(data)

def check_user_input(input):
    try:
        # Convert it into integer
    	val = int(input)
    except ValueError:
        print("Input is not an integer!")

@app.route('/ip')
def ips():
    sql = 'SELECT COUNT(DISTINCT (ip)) FROM host;'
    table = pandas.read_sql(sql, mysql.connection)
    return render_template("table.html", tables=[table.to_html(header="true")])

@app.route('/new_services', methods=['GET','POST'])
def new_services():
    if request.method == "POST":
        val = int(request.form['options'])
    else:
        val = 1

    sql = 'call Recently_Found_Services_Stored_Procedure(' + str(val) + ');'
    sql_table = 'call Recently_Found_Services_Table_Stored_Procedure(' + str(val) + ');'
    df = pandas.read_sql(sql, mysql.connection)
    table = pandas.read_sql(sql_table, mysql.connection)
    title='New Services in Last %s Days' % str(val)
    y_title='Number of Services'
    x_title='Port'
    x=df.port.to_list()
    y=df.portCount.to_list()
    x_date = False
    x_range=range(len(x))
    #save the image
    filename = 'new_port.png'
    #run the visualization
    bar_chart(title,x_title,y_title, x, y, x_range, filename)

    return render_template("radio_buttons.html", graph='/static/images/'+filename, days=[1,3,7], selected=val, tables=[table.to_html(header="true")])

@app.route('/new_hosts', methods=['GET','POST'])
def new_hosts():
    if request.method == "POST":
        val = int(request.form['options'])
    else:
        val = 3

    sql = 'call Recently_Found_Hosts_Stored_Procedure(' + str(val) + ');'
    sql_table = 'call Recently_Found_Hosts_Table_Stored_Procedure(' + str(val) + ');'
    df = pandas.read_sql(sql, mysql.connection)
    table = pandas.read_sql(sql_table, mysql.connection)
    title='Recently Found Hosts in Last %s Days' % str(val)
    y_title='Number of Hosts Found'
    x_title='Date'
    x=df.date.to_list()
    y=df.hostCount.to_list()
    x_date = False
    x_range=range(len(x))
    #save the image
    filename = 'found_hosts.png'
    #run the visualization
    bar_chart(title,x_title,y_title, x, y, x_range, filename)

    return render_template("radio_buttons.html", graph='/static/images/'+filename, days=[3,7,14], selected=val, tables=[table.to_html(header="true")])

@app.route('/lost_hosts', methods=['GET','POST'])
def lost_hosts():
    if request.method == "POST":
        val = int(request.form['options'])
    else:
        val = 3

    sql = 'call Recently_Lost_Hosts_Stored_Procedure(' + str(val) + ');'
    df = pandas.read_sql(sql, mysql.connection)
    title='Recently Lost Hosts in Last %s Days' % str(val)
    y_title='Number of Hosts Lost'
    x_title='Date'
    x=df.date.to_list()
    y=df.hostCount.to_list()
    x_date = False
    x_range=range(len(x))
    #save the image
    filename = 'lost_hosts.png'
    #run the visualization
    bar_chart(title,x_title,y_title, x, y, x_range, filename)

    return render_template("radio_buttons.html", graph='/static/images/'+filename, days=[3,7,14], selected=val)

@app.route('/total_hosts', methods=['GET','POST'])
def total_hosts():

    # Get user input date range
    if request.method == "POST":
        val = int(request.form['options'])
    else:
        val = 3

    # Query data. Stored procedure takes a date and returns the number of hosts on that date.
    # For multiple days, query each data and merge results
    today = datetime.datetime.today()
    frames = []
    for x in range(int(val)):
        date = today - datetime.timedelta(days=x)
        sql = 'call Environment_Total_Hosts_Stored_Procedure("' + date.strftime("%Y-%m-%d") + '");'
        df = pandas.read_sql(sql, mysql.connection)
        frames.append(df)

    # Merge results
    result = pandas.concat(frames)

    # Prepare data for graph
    title='Number of Hosts in Environment over Last %s Days' % str(val)
    y_title='Number of Hosts'
    x_title='Date'
    x=result.date.to_list()
    y=result.hostCount.to_list()
    x_date = False
    x_range=range(len(x))
    #save the image
    filename = 'total_hosts.png'

    #run the visualization
    line_plot(title,x_title,y_title, x, y, filename, x_date)

    return render_template("radio_buttons.html", graph='/static/images/'+filename, days=[3,7,14], selected=val)

@app.route('/', methods=['GET','POST'])
def index_total():

    # Get user input date range
    if request.method == "POST":
        val = int(request.form['options'])
    else:
        val = 3

    # Query data. Stored procedure takes a date and returns the number of hosts on that date.
    # For multiple days, query each data and merge results
    today = datetime.datetime.today()
    frames = []
    for x in range(int(val)):
        date = today - datetime.timedelta(days=x)
        sql = 'call Environment_Total_Hosts_Stored_Procedure("' + date.strftime("%Y-%m-%d") + '");'
        df = pandas.read_sql(sql, mysql.connection)
        frames.append(df)

    # Merge results
    result = pandas.concat(frames)

    # Prepare data for graph
    title='Number of Hosts in Environment over Last %s Days' % str(val)
    y_title='Number of Hosts'
    x_title='Date'
    x=result.date.to_list()
    y=result.hostCount.to_list()
    x_date = False
    x_range=range(len(x))
    #save the image
    filename = 'total_hosts.png'

    #run the visualization
    line_plot(title,x_title,y_title, x, y, filename, x_date)

    return render_template("radio_buttons.html", graph='/static/images/'+filename, days=[3,7,14], selected=val)

@app.route('/total_services', methods=['GET','POST'])
def total_services():

    # Get user input date range
    if request.method == "POST":
        val = int(request.form['options'])
    else:
        val = 3

    # Query data. Stored procedure takes a date and returns the number of hosts on that date.
    # For multiple days, query each data and merge results
    today = datetime.datetime.today()
    frames = []
    for x in range(int(val)):
        date = today - datetime.timedelta(days=x)
        sql = 'call Environment_Total_Services_Stored_Procedure("' + date.strftime("%Y-%m-%d") + '");'
        df = pandas.read_sql(sql, mysql.connection)
        frames.append(df)

    # Merge results
    result = pandas.concat(frames)

    # Prepare data for graph
    title='Number of Services in Environment over Last %s Days' % str(val)
    y_title='Number of Services'
    x_title='Date'
    x=result.date.to_list()
    y=result.serviceCount.to_list()
    x_date = False
    x_range=range(len(x))
    #save the image
    filename = 'total_services.png'

    #run the visualization
    line_plot(title,x_title,y_title, x, y, filename, x_date)

    return render_template("radio_buttons.html", graph='/static/images/'+filename, days=[3,7,14], selected=val)

@app.route('/total')
def ipport():
    sql = 'SELECT COUNT(ip) FROM host;'
    table = pandas.read_sql(sql, mysql.connection)
    return render_template("table.html", tables=[table.to_html(header="true")])

@app.after_request
def add_header(response):
    """
    Add headers to both force latest IE rendering engine or Chrome Frame,
    and also to cache the rendered page for 0 minutes.
    """
    response.headers['X-UA-Compatible'] = 'IE=Edge,chrome=1'
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

if __name__ == '__main__':
    app.run()
