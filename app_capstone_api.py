import sqlite3
from flask import Flask, request 
import pandas as pd 
app = Flask(__name__) 


# 1. MAIN PAGE
@app.route('/home') #end root
def home(): 
    return (f''' <h1> - Welcome to API Capstone Project by Dwi Susiyanto - </h1> 
    
    <h3> 1. Create Virtual Environmet with "conda create -n capstone-api python=3.8" </h3>    
    <h3> 2. Install with conda or pip : </h3> 
    <p>      - conda or pip install flask     </p> 
    <p>      - conda or pip install requests  </p> 
    <p>      - conda or pip install gunicorn  </p> 
    <p>      - conda or pip install sqlite3  </p>     
    <p>      - conda or pip install pandas  :-) </p>
    <h3> 3. Export virtual environment using pip freeze </h3>    
    <h1> </h1>    
    <h1> ------------------------------------------------------------------------------- </h1>        
    <h1>API Capstone Project: API MENU </h1>    
    <p> 1. MAIN PAGE--> http://localhost:5000/     </p> 
    <p> 2. API for invoice data, with detail date and day name --> http://localhost:5000/invoice      </p> 
    <p> 3. API to Get invoice and fitering by Country and Day name --> http://localhost:5000/invoice/(Country)/(Day)     </p> 
    <p>                     Link ---> http://localhost:5000/invoice/(Country)/(Day)    -> Please select Country: (USA,Canada,France,Brazil,Germany) and Day name:(Monday,Tuesday,Wednesday,Thursday, Friday, Saturday,Sunday)    </p>     
    <p> 4. API to calculate the Sales Weekdays in top 5 Countries --> http://localhost:5000/WeekdaysSalesinTop5Countries/      </p> 
    <p> 5. API to calculate the top Genre in Country (USA,Canada,France,Brazil,Germany) --> http://localhost:5000/genre/      </p> 
    <p> 6. API to calculate and select the Genre music  --> http://localhost:5000/genre/(Music)      </p> 
    <p>                     Link ---> http://localhost:5000/genre/(Music) -> Please select Music: (Rock, Jazz, Metal, Latin, Rock And Roll, Alternative & Punk)    </p>     
    
    <p>       </p> 
    
    <h1>THANK YOU </h1>
    
  ''')

# 2. API for invoice data, with detail date and day name

@app.route('/invoice/')
def invoice():
    conn = sqlite3.connect("data_input/chinook.db")
    data = pd.read_sql_query("SELECT * FROM invoices", conn)
    data['InvoiceDate'] = pd.to_datetime(data['InvoiceDate'])
    data['InvoiceDOW'] = data['InvoiceDate'].dt.day_name() 
    return (data.to_json())


# 3. to Get invoice and fitering by Country and Day name
@app.route('/invoice/<Country>/<Day>', methods=['GET'])
def get_data_equal(Country, Day): 
    conn = sqlite3.connect("data_input/chinook.db")
    data = pd.read_sql_query("SELECT * FROM invoices", conn)
    data['InvoiceDate'] = pd.to_datetime(data['InvoiceDate'])
    data['InvoiceDOW'] = data['InvoiceDate'].dt.day_name() 
    data1 = data[(data['BillingCountry'] == str(Country)) & (data['InvoiceDOW'] == str(Day))]  
    return (data1.to_json())

# 4. API to calculate the Sales Weekdays in top 5 Countries

@app.route('/WeekdaysSalesinTop5Countries/')
def WeekdaysSalesinTop5Countries():
    conn = sqlite3.connect("data_input/chinook.db")
    data = pd.read_sql_query(
    '''
    SELECT Customers.Country ,invoices.Total,invoices.InvoiceDate
    FROM invoices
    LEFT JOIN customers
    ON invoices.customerId = Customers.customerId
    ''', conn,parse_dates='InvoiceDate')
    data['InvoiceDOW'] = data['InvoiceDate'].dt.day_name()
    data.groupby(['Country']).sum().sort_values(by='Total',ascending=False).head(5)
    top5 = data.groupby('Country').Total.sum().sort_values(ascending=False).head().index.to_list()
    top5_data = data[data['Country'].isin(top5)].copy()
    dayorder = ['Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday', 'Sunday']
    top5_data['InvoiceDOW'] = pd.Categorical(top5_data['InvoiceDOW'],
                                         categories=dayorder,
                                         ordered=True)
    top5_data[(top5_data['InvoiceDOW'] != 'Saturday') & (top5_data['InvoiceDOW'] != 'Sunday')].\
    pivot_table(index='InvoiceDOW',
               columns='Country',
              values='Total',
              aggfunc='sum')
    return (top5_data.to_json())


# 5. API to calculate the top Genre in Country ('USA', 'Canada', 'France', 'Brazil', 'Germany')

@app.route('/genre/')
def genre():
    conn = sqlite3.connect("data_input/chinook.db")
    genre = pd.read_sql_query('''SELECT BillingCountry AS Country, genres.Name AS Genre,tracks.Unitprice, invoices.Total 
    FROM invoices
    LEFT JOIN invoice_items ON invoices.InvoiceId = invoice_items.InvoiceId
    LEFT JOIN tracks ON invoice_items.TrackId = tracks.TrackId
    LEFT JOIN genres ON tracks.genreId = genres.genreId
    WHERE BillingCountry IN ('USA', 'Canada', 'France', 'Brazil', 'Germany')
    ''',conn)
    return (genre.to_json())

# 6. API to calculate and select the Genre music 
@app.route('/genre/<Music>' , methods=['GET'])
def Country_genre(Music):
    conn = sqlite3.connect("data_input/chinook.db")
    genre = pd.read_sql_query(
        '''SELECT BillingCountry AS Country, genres.Name AS Genre,tracks.Unitprice, invoices.Total 
        FROM invoices
        LEFT JOIN invoice_items ON invoices.InvoiceId = invoice_items.InvoiceId
        LEFT JOIN tracks ON invoice_items.TrackId = tracks.TrackId 
        LEFT JOIN genres ON tracks.genreId = genres.genreId
        WHERE BillingCountry IN ('USA', 'Canada', 'France', 'Brazil', 'Germany')
        ''',conn)
    genre = genre[(genre['Genre'] == str(Music))]
    return (genre.to_json())

@app.route('/form', methods=['GET', 'POST']) #allow both GET and POST requests
def form():
    if request.method == 'POST':  # Hanya akan tampil setelah melakukan POST (submit) form
        key1 = 'name'
        key2 = 'age'
        name = request.form.get(key1)
        age = request.form[key2]
        return (f'''<h1>Your Name  is: {name}</h1>
                   <h1>Your Age is: {age}</h1> 
                   <h1>Ini adalah hasil method POST</h1> 
                ''')
    return '''<form method="POST">
                  Name: <input type="text" name="name"><br>
                  Age: <input type="text" name="age"><br>
                  <input type="submit" value="Submit"><br>
              </form>'''



if __name__ == '__main__':
    app.run(debug=True, port=5000) 