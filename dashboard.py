import pandas as pd
import plotly.express as px
from dash import Dash, dcc, html, Input, Output

# Step 1: Load your CSV file
df = pd.read_csv("GlobalWeatherRepository.csv")

# Step 2: Create Dash app
app = Dash(__name__)

# Step 3: App layout
app.layout = html.Div([
    html.H1("🌍 Climate Data Dashboard", style={'textAlign': 'center'}),

    html.Label("Select Country:"),
    dcc.Dropdown(
        id='country-dropdown',
        options=[{'label': c, 'value': c} for c in df['country'].unique()],
        value=df['country'].unique()[0],
        clearable=False
    ),

    html.Label("Select Location:"),
    dcc.Dropdown(
        id='city-dropdown',
        clearable=False
    ),

    # Graphs
    dcc.Graph(id='temp-wind-graph'),
    dcc.Graph(id='temp-humidity-graph'),
    dcc.Graph(id='avg-temp-graph')  # New bar chart
])

# Step 4: Update city dropdown when country changes
@app.callback(
    Output('city-dropdown', 'options'),
    Output('city-dropdown', 'value'),
    Input('country-dropdown', 'value')
)
def update_city_dropdown(selected_country):
    filtered_df = df[df['country'] == selected_country]
    city_options = [{'label': loc, 'value': loc} for loc in filtered_df['location_name'].unique()]
    first_city = filtered_df['location_name'].unique()[0]
    return city_options, first_city

# Step 5: Update all graphs when selections change
@app.callback(
    [Output('temp-wind-graph', 'figure'),
     Output('temp-humidity-graph', 'figure'),
     Output('avg-temp-graph', 'figure')],
    [Input('country-dropdown', 'value'),
     Input('city-dropdown', 'value')]
)
def update_graphs(selected_country, selected_city):
    filtered_df = df[(df['country'] == selected_country) & (df['location_name'] == selected_city)]

    # Scatter 1: Temperature vs Wind
    fig1 = px.scatter(filtered_df, x='wind_kph', y='temperature_celsius',
                      title=f"Temperature vs Wind Speed ({selected_city}, {selected_country})",
                      color='condition_text')

    # Scatter 2: Temperature vs Humidity
    fig2 = px.scatter(filtered_df, x='humidity', y='temperature_celsius',
                      title=f"Temperature vs Humidity ({selected_city}, {selected_country})",
                      color='condition_text')

    # Bar chart: Average temperature by city in that country
    avg_temp_df = df[df['country'] == selected_country].groupby('location_name', as_index=False)['temperature_celsius'].mean()
    fig3 = px.bar(avg_temp_df, x='location_name', y='temperature_celsius',
                  title=f"Average Temperature per City ({selected_country})",
                  color='temperature_celsius')

    return fig1, fig2, fig3

# Step 6: Run the app
if __name__ == "__main__":
    app.run(debug=True)
    