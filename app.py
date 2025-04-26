from flask import Flask, render_template, request, redirect, url_for, flash
from werkzeug.utils import secure_filename
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import plotly.io as pio


from flask_sqlalchemy import SQLAlchemy
from flask_bcrypt import bcrypt

app = Flask(__name__)

app.config['SECRET_KEY'] = 'your_secret_key'
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///site.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db = SQLAlchemy(app)

class User(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(150), nullable=False)
    username = db.Column(db.String(150), unique=True, nullable=False)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(60), nullable=False)

    def __repr__(self):
        return f"User('{self.username}', '{self.email}')"

    def __init__(self, name, username, email, password):
        self.name = name
        self.username = username
        self.email = email
        self.password = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode('utf-8')

    def check_password(self, password):
        return bcrypt.checkpw(password.encode('utf-8'), self.password.encode('utf-8'))
    

with app.app_context():
    db.create_all()


df = pd.read_csv('ev_charging_patterns dataset.csv')

@app.route('/')
def index():
    return render_template('index.html')


@app.route('/login',methods=['GET', 'POST'])
def login():
    if request.method == 'POST':
        username = request.form['email or username']
        password = request.form['password']
        user = User.query.filter_by(username=username).first() or User.query.filter_by(email=username).first()
        if not user:
            flash('User not found. Please register.', 'danger')
            return redirect(url_for('register'))
        if user and user.check_password(password):
            flash('Login successful!', 'success')
            return redirect(url_for('dashboard'))
        else:
            flash('Login failed. Check your username and password.', 'danger')
    return render_template('login.html')
    
 


@app.route('/register', methods=['GET', 'POST'])
def register():
    if request.method == 'POST':
        name = request.form['name']
        username = request.form['username']
        email = request.form['email']
        password = request.form['password']

        if User.query.filter_by(username=username).first() or User.query.filter_by(email=email).first():
            flash('Username or email already exists!', 'danger')
            return redirect(url_for('register'))

        new_user = User(name=name, username=username, email=email, password=password)
        db.session.add(new_user)
        db.session.commit()
        flash('Registration successful! You can now log in.', 'success')
        return redirect(url_for('login'))
    return render_template('register.html')
    
    
@app.route('/about')
def about():
    return render_template('about.html')


@app.route('/contact')
def contact():
    return render_template('contact.html')


@app.route('/dashboard')
def dashboard():
    return render_template('dashboard.html')


#Graphs functions
def avg_chargingRate():
    fig=go.Figure()
    avg_charging_rate_by_charger = df.groupby('Charger Type')['Charging Rate (kW)'].mean().reset_index()

    fig = px.bar(avg_charging_rate_by_charger, 
                x='Charger Type', 
                y='Charging Rate (kW)', 
                title='Average Charging Rate by Charger Type',
                labels={'Charging Rate (kW)': 'Average Charging Rate (kW)', 'Charger Type': 'Charger Type'},
                text='Charging Rate (kW)')

    fig.update_traces(texttemplate='%{text:.2f}', textposition='outside')
    fig.update_layout(xaxis_title='Charger Type', yaxis_title='Average Charging Rate (kW)', showlegend=False)

    fig.update_layout(
        plot_bgcolor='black',
        paper_bgcolor='black',
        font_color='white'
    )
    fig.update_traces(marker_color='#F6B8D0')
    graph1_html = pio.to_html(fig, full_html=False)
    return graph1_html

def avg_charging_duration_by_charger_type():
    fig=go.Figure()
    df['Charging Duration (minutes)'] = df['Charging Duration (hours)'] * 60

    fig = px.box(df, 
                x='Charger Type', 
                y='Charging Duration (minutes)', 
                title='Charging Duration by Charger Type',
                labels={'Charging Duration (minutes)': 'Charging Duration (minutes)', 'Charger Type': 'Charger Type'},
                color='Charger Type')

    fig.update_layout(
        xaxis_title='Charger Type',
        yaxis_title='Charging Duration (minutes)',
        plot_bgcolor='black',
        paper_bgcolor='black',
        font_color='white'
    )
    graph2_html = pio.to_html(fig, full_html=False)
    return graph2_html

def avg_charging_cost():
        fig=go.Figure()
        avg_charging_cost_by_charger = df.groupby('Charger Type')['Charging Cost (USD)'].mean().reset_index()

        fig = px.line(avg_charging_cost_by_charger, 
                    x='Charger Type', 
                    y='Charging Cost (USD)', 
                    title='Average Charging Cost by Charger Type',
                    labels={'Charging Cost (USD)': 'Average Charging Cost (USD)', 'Charger Type': 'Charger Type'},
                    markers=True)

        fig.update_layout(
            xaxis_title='Charger Type',
            yaxis_title='Average Charging Cost (USD)',
            plot_bgcolor='black',
            paper_bgcolor='black',
            font_color='white'
        )

        fig.update_traces(line_color='#F6B8D0', marker=dict(color='#F6B8D0'))
        graph3_html = pio.to_html(fig, full_html=False)
        return graph3_html

def charger_usage_frequency():
        fig=go.Figure()
        charger_usage_frequency = df['Charger Type'].value_counts().reset_index()
        charger_usage_frequency.columns = ['Charger Type', 'Frequency']

        fig = px.bar(charger_usage_frequency, 
                x='Charger Type', 
                y='Frequency', 
                title='Charger Usage Frequency',
                labels={'Frequency': 'Usage Frequency', 'Charger Type': 'Charger Type'},
                text='Frequency')

        fig.update_traces(texttemplate='%{text}', textposition='outside')
        fig.update_layout(
        xaxis_title='Charger Type',
        yaxis_title='Usage Frequency',
        plot_bgcolor='black',
        paper_bgcolor='black',
        font_color='white'
    )

        fig.update_traces(marker_color='#DC143C')
        graph4_html = pio.to_html(fig, full_html=False)
        return graph4_html

def charging_duration():
        fig=go.Figure()
        fig = px.histogram(df, x='Charging Duration (hours)', title='Histogram of Charging Duration', nbins=30)
        fig.update_layout(
        xaxis_title='Charging Duration (hours)',
        yaxis_title='Count',
        plot_bgcolor='black',
        paper_bgcolor='black',
        font_color='white'
    )
        fig.update_traces(marker_color='#F6B8D0')
        graph5_html = pio.to_html(fig, full_html=False)
        return graph5_html

def energy_consumed():
    fig=go.Figure()
    df['Charging Start Time'] = pd.to_datetime(df['Charging Start Time'])  # Ensure the column is in datetime format
    fig = px.line(df.sort_values('Charging Start Time'), x='Charging Start Time', y='Energy Consumed (kWh)', title='Line Chart of Energy Consumed Over Time')
    fig.update_layout(
        xaxis_title='Charging Start Time',
        yaxis_title='Energy Consumed (kWh)',
        plot_bgcolor='black',
        paper_bgcolor='black',
        font_color='white'
    )
    graph6_html = pio.to_html(fig, full_html=False)
    return graph6_html

def charging_hour():
    fig=go.Figure()
    df['Charging Hour'] = df['Charging Start Time'].dt.hour  # Extract the hour from the charging start time

    fig = px.density_heatmap(
    df,
    x='Charging Hour',
    y='Day of Week',
    title='Heatmap of Charging Hour vs Day of Week',
    color_continuous_scale='Viridis'
)

    fig.update_layout(
    xaxis_title='Charging Hour',
    yaxis_title='Day of Week',
    plot_bgcolor='black',
    paper_bgcolor='black',
    font_color='white'
)
    graph7_html = pio.to_html(fig, full_html=False)
    return graph7_html

def charging_rate():
    fig=go.Figure()
    if 'Charger Type' in df.columns and 'Charging Rate (kW)' in df.columns:
        fig = px.box(
            df,
            x='Charger Type',
            y='Charging Rate (kW)',
            title='Box Plot of Charging Rate by Charger Type',
            color='Charger Type'
        )

        fig.update_layout(
            xaxis_title='Charger Type',
            yaxis_title='Charging Rate (kW)',
            plot_bgcolor='black',
            paper_bgcolor='black',
            font_color='white'
        )   

        graph8_html = pio.to_html(fig, full_html=False)
        return graph8_html
    
def energy_consumed_vs_charging_duration():
    fig=go.Figure()
    df['Charging Duration (minutes)'] = df['Charging Duration (hours)'] * 60

    # Plot the scatter plot
    fig = px.scatter(df, x='Charging Duration (minutes)', y='Energy Consumed (kWh)', 
                    title='Energy Consumed vs. Charging Duration',
                    labels={'Charging Duration (minutes)': 'Charging Duration (minutes)', 
                            'Energy Consumed (kWh)': 'Energy Consumed (kWh)'},template='plotly_dark')
    
        
    graph9_html = pio.to_html(fig, full_html=False)
    return graph9_html

def avg_energy_consumption_per_model():
    fig=go.Figure()
    avg_energy_per_model = df.groupby('Vehicle Model')['Energy Consumed (kWh)'].mean().reset_index()

    # Plot the line chart
    fig = px.line(avg_energy_per_model, x='Vehicle Model', y='Energy Consumed (kWh)', 
                title='Average Energy Consumption per Vehicle Model',
                labels={'Vehicle Model': 'Vehicle Model', 'Energy Consumed (kWh)': 'Average Energy Consumed (kWh)'},template='plotly_dark')     
    graph10_html = pio.to_html(fig, full_html=False)
    return graph10_html   

def charging_cost():
    fig=go.Figure()
    fig = px.histogram(df, x='Charging Cost (USD)', 
                   title='Charging Cost Distribution',
                   labels={'Charging Cost (USD)': 'Charging Cost (USD)'},template='plotly_dark',
                   nbins=30)  # Adjust the number of bins as needed
    graph11=pio.to_html(fig, full_html=False)
    return graph11

def energy_consumed_by_user_type():
    fig=go.Figure()
    fig = px.box(df, x='User Type', y='Energy Consumed (kWh)', 
             title='Energy Consumed by User Type',
             labels={'User Type': 'User Type', 'Energy Consumed (kWh)': 'Energy Consumed (kWh)'},template='plotly_dark',)
    graph12=pio.to_html(fig, full_html=False)
    return graph12 

def charging_sessions():
    fig=go.Figure()
    city_data = df.groupby('Charging Station Location')['User ID'].count().reset_index()
    city_data.rename(columns={'User ID': 'Charging Sessions'}, inplace=True)
    city_data = df.groupby('Charging Station Location')['User ID'].count().reset_index()
    city_data.rename(columns={'User ID': 'Charging Sessions'}, inplace=True)

    # Create a Plotly Geo heatmap
    fig = px.scatter_geo(city_data,
                        locations="Charging Station Location",
                        locationmode="USA-states",
                        size="Charging Sessions",
                        title="Charging Sessions by Location",
                        projection="albers usa",
                        width=600,
                        height=400)

    # Add markers for the charging station locations
    fig.add_scattergeo(
        locations=["charging station 1"],
        locationmode="USA-states",
        mode="markers",
        marker=dict(size=10, color="blue"),
        name="Charging Stations"
    )

    fig.update_layout(geo=dict(bgcolor='lightblue'),template='plotly_dark')
    graph13_html = pio.to_html(fig, full_html=False)
    return graph13_html

def avg_charging_cost_per_station():
    fig=go.Figure()
    avg_cost_per_station = df.groupby('Charging Station Location')['Charging Cost (USD)'].mean().reset_index()

    # Create a bar chart using Plotly
    fig = px.bar(avg_cost_per_station,
                x='Charging Station Location',
                y='Charging Cost (USD)',
                title='Average Charging Cost per Station',
                labels={'Charging Cost (USD)': 'Average Charging Cost (USD)', 'Charging Station Location': 'Station Location'},
                text='Charging Cost (USD)',template='plotly_dark')
    graph14=pio.to_html(fig, full_html=False)
    return graph14

def energy_consumed_by_location():
    fig=go.Figure()
    fig = px.box(df, 
                x='Charging Station Location', 
                y='Energy Consumed (kWh)', 
                title='Energy Consumed by Location',
                labels={'Energy Consumed (kWh)': 'Energy Consumed (kWh)', 'Charging Station Location': 'Station Location'},
                color='Charging Station Location',template='plotly_dark')
    graph15=pio.to_html(fig, full_html=False)
    return graph15

def charging_trends_by_city():
    fig=go.Figure()
    df['Charging Start Time'] = pd.to_datetime(df['Charging Start Time'])

    # Group data by city and time, counting charging sessions
    time_series_data = df.groupby([df['Charging Start Time'].dt.date, 'Charging Station Location'])['User ID'].count().reset_index()
    time_series_data.rename(columns={'Charging Start Time': 'Date', 'User ID': 'Charging Sessions'}, inplace=True)

    # Create a time series plot using Plotly
    fig = px.line(time_series_data,
                x='Date',
                y='Charging Sessions',
                color='Charging Station Location',
                title='Charging Trends by City',
                labels={'Date': 'Date', 'Charging Sessions': 'Number of Charging Sessions', 'Charging Station Location': 'City'},template='plotly_dark')
    graph16=pio.to_html(fig, full_html=False)
    return graph16

def charging_session_by_location():
    fig=go.Figure()
    city_data = df.groupby('Charging Station Location')['User ID'].count().reset_index()
    city_data.rename(columns={'User ID': 'Charging Sessions'}, inplace=True)

    # Use a valid projection type
    fig = px.scatter_geo(city_data,
                        locations="Charging Station Location",
                        locationmode="USA-states",
                        size="Charging Sessions",
                        title="Charging Sessions by Location",
                        projection="stereographic",
                        width=800,
                        height=500,template='plotly_dark')
    graph17=pio.to_html(fig, full_html=False)
    return graph17

def energy_consumed_by_hour():
    fig=go.Figure()
    if 'Hour of Day' not in df.columns:
        df['Hour of Day'] = pd.to_datetime(df['Charging Start Time']).dt.hour  # Using 'Charging Start Time' as the datetime column

    # Group by 'Hour of Day' and calculate the average energy consumption
    avg_energy_by_hour = df.groupby('Hour of Day')['Energy Consumed (kWh)'].mean().reset_index()

    # Create a Plotly line chart
    fig = px.line(avg_energy_by_hour, x='Hour of Day', y='Energy Consumed (kWh)', 
                title='Average Energy Consumption by Hour of Day',
                labels={'Energy Consumed (kWh)': 'Average Energy Consumed (kWh)', 'Hour of Day': 'Hour of Day'},template='plotly_dark')
    graph18=pio.to_html(fig, full_html=False)
    return graph18

def charging_session_per_day():
    fig=go.Figure()
    charging_sessions_per_day = df['Day of Week'].value_counts().reset_index()
    charging_sessions_per_day.columns = ['Day of Week', 'Charging Sessions']

    # Create a Plotly bar chart
    fig_bar = px.bar(charging_sessions_per_day, x='Day of Week', y='Charging Sessions',
                    title='Charging Sessions per Day of Week',
                    labels={'Day of Week': 'Day of Week', 'Charging Sessions': 'Number of Charging Sessions'},
                    text='Charging Sessions',template='plotly_dark')

    fig_bar.update_traces(textposition='outside')
    graph19_html = pio.to_html(fig_bar, full_html=False)
    return graph19_html

def temperature_distributon():
    fig=go.Figure()
    fig_violin = px.violin(df, x='Time of Day', y='Temperature (°C)', 
                       title='Temperature Distribution by Time of Day',
                       labels={'Temperature (°C)': 'Temperature (°C)', 'Time of Day': 'Time of Day'},template='plotly_dark',
                       box=True, points='all')
    graph20_html = pio.to_html(fig_violin, full_html=False)
    return graph20_html 

def charging_sessions_by_time():
    fig=go.Figure()
    charging_sessions_by_time = df['Time of Day'].value_counts().reset_index()
    charging_sessions_by_time.columns = ['Time of Day', 'Charging Sessions']

    # Create a Plotly bar chart
    fig_time_of_day = px.bar(charging_sessions_by_time, x='Time of Day', y='Charging Sessions',
                            title='Charging Sessions by Time of Day',
                            labels={'Time of Day': 'Time of Day', 'Charging Sessions': 'Number of Charging Sessions'},
                            text='Charging Sessions',template='plotly_dark')

    fig_time_of_day.update_traces(textposition='outside')
    graph21_html = pio.to_html(fig_time_of_day, full_html=False)
    return graph21_html

def battery_capacity():
    fig=go.Figure()
    fig = px.bar(df, x='Vehicle Model', y='Battery Capacity (kWh)', 
             title='Battery Capacity by Vehicle Model', 
             labels={'Battery Capacity (kWh)': 'Battery Capacity (kWh)', 'Vehicle Model': 'Vehicle Model'},
             color='Vehicle Model',template='plotly_dark')
    graph22_html = pio.to_html(fig, full_html=False)
    return graph22_html

def soc_change_per_session():
    fig=go.Figure()
    df['State of Charge (Start %)'] = df['State of Charge (Start %)'].astype(float)
    df['State of Charge (End %)'] = df['State of Charge (End %)'].astype(float)

        # Calculate SoC change
    df['SoC Change (%)'] = df['State of Charge (End %)'] - df['State of Charge (Start %)']

        # Create a line chart for SoC change
    fig_soc_change = px.line(df, x=df.index, y='SoC Change (%)', 
                                title='SoC Change per Session (End - Start %)', 
                                labels={'x': 'Session Index', 'SoC Change (%)': 'SoC Change (%)'})
    df['SoC Change (%)'] = df['State of Charge (End %)'] - df['State of Charge (Start %)']

    fig_soc_change = px.line(df, x=df.index, y='SoC Change (%)', 
                            title='SoC Change per Session (End - Start %)', 
                            labels={'x': 'Session Index', 'SoC Change (%)': 'SoC Change (%)'},template='plotly_dark')
    graph23_html = pio.to_html(fig_soc_change, full_html=False)
    return graph23_html

def distance_vs_battery_size():
    fig=go.Figure()
    fig_histogram = px.histogram(df, x='Distance Driven (since last charge) (km)', color='Battery Capacity (kWh)',
                             title='Histogram: Distance Driven vs. Battery Size',
                             labels={'Distance Driven (since last charge) (km)': 'Distance Driven (km)', 
                                     'Battery Capacity (kWh)': 'Battery Size (kWh)'},template='plotly_dark',
                             nbins=50)
    graph24_html = pio.to_html(fig_histogram, full_html=False)
    return graph24_html      

def avg_charging_duration_by_user_type():
    fig=go.Figure()
    avg_charging_duration = df.groupby('User Type')['Charging Duration (hours)'].mean().reset_index()

    # Create a Plotly bar chart
    fig = px.bar(avg_charging_duration, 
                x='User Type', 
                y='Charging Duration (hours)', 
                title='Avg. Charging Duration by User Type',
                labels={'Charging Duration (hours)': 'Avg. Charging Duration (hours)', 'User Type': 'User Type'},
                color='User Type',template='plotly_dark')
    graph25_html = pio.to_html(fig, full_html=False)
    return graph25_html

def energy_consumed_by_user_type():
    fig=go.Figure()
    fig = px.box(df, 
             x='User Type', 
             y='Energy Consumed (kWh)', 
             title='Energy Consumption by User Type',
             labels={'Energy Consumed (kWh)': 'Energy Consumed (kWh)', 'User Type': 'User Type'},
             color='User Type',template='plotly_dark')
    graph26=pio.to_html(fig, full_html=False)
    return graph26

def charging_frequency_over_time():
    fig=go.Figure()
    df['Charging Start Time'] = pd.to_datetime(df['Charging Start Time'])

    # Group by User Type and Charging Start Time (aggregated by day)
    charging_frequency = df.groupby([df['Charging Start Time'].dt.date, 'User Type']).size().reset_index(name='Frequency')

    # Create a Plotly line chart
    fig = px.line(charging_frequency, 
                x='Charging Start Time', 
                y='Frequency', 
                color='User Type', 
                title='Charging Frequency over Time by User Type',
                labels={'Charging Start Time': 'Date', 'Frequency': 'Charging Frequency', 'User Type': 'User Type'},template='plotly_dark')
    graph27=pio.to_html(fig, full_html=False)
    return graph27

def distance_driven_per_charge():
    fig=go.Figure()
    fig = px.histogram(df, 
                    x='Distance Driven (since last charge) (km)', 
                    color='User Type', 
                    title='Distance Driven per Charge by User Type',
                    labels={'Distance Driven (since last charge) (km)': 'Distance Driven (km)', 'User Type': 'User Type'},template='plotly_dark',
                    nbins=30)
    graph28=pio.to_html(fig, full_html=False)
    return graph28

#Analysis page connectivity
@app.route('/charger_type_performance')
def chargerType():
    graph1 = avg_chargingRate()
    graph2 = avg_charging_duration_by_user_type()
    graph3 = avg_charging_cost()
    graph4 = charger_usage_frequency()
    return render_template('charger_type_performance.html', graph1=graph1, graph2=graph2, graph3=graph3, graph4=graph4)

@app.route('/charging_behaviour_analysis')
def chargingDuration():
    graph5 = charging_duration()
    graph6 = energy_consumed()
    graph7 = charging_hour()
    graph8 = charging_rate()
    return render_template('charging_behaviour_analysis.html', graph5=graph5, graph6=graph6, graph7=graph7, graph8=graph8)

@app.route('/energy_consumption_and_efficiency')
def energyVsDuration():
    graph9 = energy_consumed_vs_charging_duration()
    graph10 = avg_energy_consumption_per_model()
    graph11 = charging_cost()
    graph12 = energy_consumed_by_user_type()
    return render_template('energy_consumption_and_efficiency.html', graph9=graph9,graph10=graph10, graph11=graph11, graph12=graph12)

@app.route('/geographic_and_station_level_insights')
def geographic():
    graph13 = charging_sessions()
    graph14 = avg_charging_cost_per_station()
    graph15= energy_consumed_by_location()
    graph16 = charging_trends_by_city()
    graph17 = charging_session_by_location()
   

    return render_template('geographic_and_station_level_insights.html', graph13=graph13, graph14=graph14, graph15=graph15,graph16=graph16, graph17=graph17)

@app.route('/time_based_patterns')
def timeBased():
    graph18 = energy_consumed_by_hour()
    graph19 = charging_session_per_day()
    graph20= temperature_distributon()
    graph21 = charging_sessions_by_time()
    return render_template('time_based_patterns.html', graph18=graph18,graph19=graph19, graph20=graph20, graph21=graph21)


@app.route('/vehicle_and_battery_analysis')
def vehicleBattery():
    graph22 = battery_capacity()
    graph23 = soc_change_per_session()
    graph24 = distance_vs_battery_size()
   
    return render_template('vehicle_and_battery_analysis.html', graph22=graph22, graph23=graph23, graph24=graph24, )

@app.route('/user_type_and_behaviour_segmentation')
def userType():
    graph25 = avg_charging_duration_by_user_type()
    graph26 = energy_consumed_by_user_type()
    graph27 = charging_frequency_over_time()
    graph28 = distance_driven_per_charge()
    return render_template('user_type_and_behaviour_segmentation.html', graph25=graph25, graph26=graph26,graph27=graph27, graph28=graph28)

if __name__ == '__main__':
    app.run(debug=True)       
            
            
       
            
        

