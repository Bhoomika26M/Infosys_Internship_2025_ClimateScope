import pandas as pd
import numpy as np
from datetime import datetime, timedelta

def generate_climate_data():
    np.random.seed(42)
    
    countries = [
        'United States', 'China', 'India', 'Brazil', 'Russia', 'Canada', 'Australia', 'Germany', 'France', 'United Kingdom',
        'Japan', 'South Korea', 'Mexico', 'Indonesia', 'Turkey', 'Saudi Arabia', 'Argentina', 'South Africa', 'Egypt', 'Nigeria',
        'Kenya', 'Thailand', 'Vietnam', 'Philippines', 'Malaysia', 'Singapore', 'New Zealand', 'Norway', 'Sweden', 'Finland',
        'Denmark', 'Netherlands', 'Belgium', 'Switzerland', 'Austria', 'Poland', 'Ukraine', 'Spain', 'Italy', 'Greece',
        'Portugal', 'Ireland', 'Iceland', 'Chile', 'Peru', 'Colombia', 'Venezuela', 'Ecuador', 'Bolivia', 'Paraguay',
        'Uruguay', 'Bangladesh', 'Pakistan', 'Afghanistan', 'Iran', 'Iraq', 'Israel', 'Jordan', 'Lebanon', 'Syria',
        'Yemen', 'Oman', 'UAE', 'Qatar', 'Kuwait', 'Bahrain', 'Kazakhstan', 'Uzbekistan', 'Turkmenistan', 'Kyrgyzstan',
        'Tajikistan', 'Mongolia', 'Nepal', 'Bhutan', 'Sri Lanka', 'Myanmar', 'Cambodia', 'Laos', 'Ethiopia', 'Somalia',
        'Sudan', 'South Sudan', 'Chad', 'Niger', 'Mali', 'Mauritania', 'Senegal', 'Guinea', 'Sierra Leone', 'Liberia',
        'Ivory Coast', 'Ghana', 'Togo', 'Benin', 'Burkina Faso', 'Cameroon', 'Central African Republic', 'Congo', 'DR Congo', 'Gabon',
        'Angola', 'Zambia', 'Zimbabwe', 'Mozambique', 'Madagascar', 'Malawi', 'Tanzania', 'Uganda', 'Rwanda', 'Burundi',
        'Botswana', 'Namibia', 'Lesotho', 'Eswatini', 'Mauritius', 'Seychelles', 'Comoros', 'Djibouti', 'Eritrea', 'Tunisia',
        'Algeria', 'Morocco', 'Libya', 'Western Sahara', 'Cuba', 'Haiti', 'Dominican Republic', 'Jamaica', 'Trinidad and Tobago', 'Barbados',
        'Bahamas', 'Belize', 'Costa Rica', 'El Salvador', 'Guatemala', 'Honduras', 'Nicaragua', 'Panama', 'Albania', 'Bosnia and Herzegovina',
        'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic', 'Estonia', 'Hungary', 'Latvia', 'Lithuania', 'Luxembourg', 'Malta',
        'Moldova', 'Montenegro', 'North Macedonia', 'Romania', 'Serbia', 'Slovakia', 'Slovenia', 'Armenia', 'Azerbaijan', 'Belarus',
        'Georgia', 'Greenland', 'Papua New Guinea', 'Fiji', 'Solomon Islands', 'Vanuatu', 'Samoa', 'Tonga', 'Kiribati', 'Marshall Islands',
        'Micronesia', 'Palau', 'Nauru', 'Tuvalu', 'East Timor', 'Brunei', 'Maldives', 'Cape Verde', 'Sao Tome and Principe', 'Guinea-Bissau',
        'Equatorial Guinea', 'Gambia', 'Kosovo', 'Andorra', 'Monaco', 'Liechtenstein', 'San Marino', 'Vatican City', 'Suriname', 'Guyana',
        'French Guiana', 'Réunion', 'Mayotte', 'New Caledonia', 'French Polynesia', 'Guam', 'Puerto Rico', 'U.S. Virgin Islands', 'Aruba', 'Curaçao',
        'Sint Maarten', 'Anguilla', 'Bermuda', 'Cayman Islands', 'Turks and Caicos', 'British Virgin Islands', 'Montserrat', 'Saint Kitts and Nevis', 'Antigua and Barbuda', 'Dominica',
        'Saint Lucia', 'Saint Vincent and the Grenadines', 'Grenada'
    ]
    
    regions = {
        'North America': ['United States', 'Canada', 'Mexico', 'Greenland', 'Cuba', 'Haiti', 'Dominican Republic', 'Jamaica', 'Trinidad and Tobago', 'Barbados', 'Bahamas', 'Belize', 'Costa Rica', 'El Salvador', 'Guatemala', 'Honduras', 'Nicaragua', 'Panama'],
        'South America': ['Brazil', 'Argentina', 'Chile', 'Peru', 'Colombia', 'Venezuela', 'Ecuador', 'Bolivia', 'Paraguay', 'Uruguay', 'Suriname', 'Guyana', 'French Guiana'],
        'Europe': ['Germany', 'France', 'United Kingdom', 'Norway', 'Sweden', 'Finland', 'Denmark', 'Netherlands', 'Belgium', 'Switzerland', 'Austria', 'Poland', 'Ukraine', 'Spain', 'Italy', 'Greece', 'Portugal', 'Ireland', 'Iceland', 'Albania', 'Bosnia and Herzegovina', 'Bulgaria', 'Croatia', 'Cyprus', 'Czech Republic', 'Estonia', 'Hungary', 'Latvia', 'Lithuania', 'Luxembourg', 'Malta', 'Moldova', 'Montenegro', 'North Macedonia', 'Romania', 'Serbia', 'Slovakia', 'Slovenia', 'Kosovo', 'Andorra', 'Monaco', 'Liechtenstein', 'San Marino', 'Vatican City'],
        'Asia': ['China', 'India', 'Japan', 'South Korea', 'Indonesia', 'Thailand', 'Vietnam', 'Philippines', 'Malaysia', 'Singapore', 'Bangladesh', 'Pakistan', 'Afghanistan', 'Iran', 'Iraq', 'Israel', 'Jordan', 'Lebanon', 'Syria', 'Yemen', 'Oman', 'UAE', 'Qatar', 'Kuwait', 'Bahrain', 'Kazakhstan', 'Uzbekistan', 'Turkmenistan', 'Kyrgyzstan', 'Tajikistan', 'Mongolia', 'Nepal', 'Bhutan', 'Sri Lanka', 'Myanmar', 'Cambodia', 'Laos', 'Armenia', 'Azerbaijan', 'Georgia', 'East Timor', 'Brunei', 'Maldives'],
        'Africa': ['South Africa', 'Egypt', 'Nigeria', 'Kenya', 'Ethiopia', 'Somalia', 'Sudan', 'South Sudan', 'Chad', 'Niger', 'Mali', 'Mauritania', 'Senegal', 'Guinea', 'Sierra Leone', 'Liberia', 'Ivory Coast', 'Ghana', 'Togo', 'Benin', 'Burkina Faso', 'Cameroon', 'Central African Republic', 'Congo', 'DR Congo', 'Gabon', 'Angola', 'Zambia', 'Zimbabwe', 'Mozambique', 'Madagascar', 'Malawi', 'Tanzania', 'Uganda', 'Rwanda', 'Burundi', 'Botswana', 'Namibia', 'Lesotho', 'Eswatini', 'Mauritius', 'Seychelles', 'Comoros', 'Djibouti', 'Eritrea', 'Tunisia', 'Algeria', 'Morocco', 'Libya', 'Western Sahara', 'Cape Verde', 'Sao Tome and Principe', 'Guinea-Bissau', 'Equatorial Guinea', 'Gambia'],
        'Oceania': ['Australia', 'New Zealand', 'Papua New Guinea', 'Fiji', 'Solomon Islands', 'Vanuatu', 'Samoa', 'Tonga', 'Kiribati', 'Marshall Islands', 'Micronesia', 'Palau', 'Nauru', 'Tuvalu'],
        'Caribbean': ['Anguilla', 'Bermuda', 'Cayman Islands', 'Turks and Caicos', 'British Virgin Islands', 'Montserrat', 'Saint Kitts and Nevis', 'Antigua and Barbuda', 'Dominica', 'Saint Lucia', 'Saint Vincent and the Grenadines', 'Grenada', 'Aruba', 'Curaçao', 'Sint Maarten'],
        'Territories': ['Réunion', 'Mayotte', 'New Caledonia', 'French Polynesia', 'Guam', 'Puerto Rico', 'U.S. Virgin Islands']
    }
    
    country_region_map = {}
    for region, country_list in regions.items():
        for country in country_list:
            country_region_map[country] = region
    
    start_date = datetime(2023, 1, 1)
    end_date = datetime(2023, 12, 31)
    date_range = pd.date_range(start=start_date, end=end_date, freq='D')
    
    data = []
    
    for country in countries:
        region = country_region_map.get(country, 'Other')
        
        lat = np.random.uniform(-60, 70)
        lon = np.random.uniform(-180, 180)
        
        if region in ['Europe', 'North America']:
            base_temp = np.random.uniform(-5, 20)
        elif region in ['Africa', 'South America', 'Asia']:
            base_temp = np.random.uniform(15, 30)
        elif region == 'Oceania':
            base_temp = np.random.uniform(10, 25)
        else:
            base_temp = np.random.uniform(0, 25)
        
        for date in date_range:
            day_of_year = date.timetuple().tm_yday
            seasonal_variation = 15 * np.sin(2 * np.pi * (day_of_year - 80) / 365)
            temperature = base_temp + seasonal_variation + np.random.normal(0, 3)
            
            humidity = np.random.uniform(30, 90)
            
            wind_speed = np.random.gamma(2, 2)
            
            precipitation = np.random.exponential(2) if np.random.random() > 0.7 else 0
            
            data.append({
                'Date': date,
                'Country': country,
                'Region': region,
                'Latitude': lat,
                'Longitude': lon,
                'Temperature': round(temperature, 2),
                'Humidity': round(humidity, 2),
                'Wind Speed': round(wind_speed, 2),
                'Precipitation': round(precipitation, 2)
            })
    
    df = pd.DataFrame(data)
    return df

def get_country_coordinates(df):
    coords = df.groupby('Country').agg({
        'Latitude': 'first',
        'Longitude': 'first'
    }).reset_index()
    return coords
