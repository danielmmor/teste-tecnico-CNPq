import os
import folium
import numpy as np
import pandas as pd
import seaborn as sns
import branca as bc

print('Begin all')

coords_BR_NE = [-8.6468, -41.7742]

icons_url = [
    'https://imgur.com/rH8q9BT.png',
    'https://imgur.com/Brb5bwZ.png',
    'https://imgur.com/AMpmPbw.png',
    'https://imgur.com/Vk0lHwm.png',
    'https://imgur.com/xX9c6Ri.png',
    'https://imgur.com/cGOsp9I.png',
    'https://imgur.com/iuvZgej.png',
    'https://imgur.com/aFD6iW0.png',
    'https://imgur.com/0ZSCBts.png',
    'https://imgur.com/kGmIp7h.png'
]

icons = np.array([
    icons_url[0],
    icons_url[1],
    icons_url[2],
    icons_url[3],
    icons_url[4],
    icons_url[5],
    icons_url[6],
    icons_url[7],
    icons_url[8],
    icons_url[9]
])

print('icon ok')

pollutants = {
    1: {
        'notation': 'PO4',
        'name': 'Fósforo',
        'bin_edges': np.array([0.3, 0.6, 0.9, 1.2, 1.5, 1.8, 2.1, 2.4, 2.7])
    }
}

def load_data(pollutant_id):
    print('>> Loading data...')
    agg_data = pd.read_csv('agua_teste.csv', sep=',')
    print(agg_data)
    return agg_data

print('load data ok')

def icon_coding(poll, bin_edges):
    idx = np.digitize(poll, bin_edges, right=True)
    return icons[idx]

print('icon coding ok')

def prepare_data(df, pollutant_ID):
    print('>> Preparing data...')
    df = df.loc[:, ['CORPO_DAGU', 'LATITUDE', 'LONGITUDE', 'MA1FOSFORO']]
    df['icon'] = df.MA1FOSFORO.apply(icon_coding, bin_edges=pollutants[pollutant_ID]['bin_edges'])
    print(df)
    return df

print('prepare data ok')

def MyPoint(name, x, y, icon, phosph):
    return {
        'type': 'Feature',
        'geometry': {
            'type': 'Point',
            'coordinates': [x, y]
        },
        'properties': {
            'icon': icon,
            'popupcontent': (f'Corpo d\'água: {name}<br>'
                             f'Fósforo (ua): {phosph}')
        }
    }

print('class MyPoint ok')

def create_geojson_features(df):
    print('>> Creating GeoJSON features...')
    features = []
    for _, row in df.iterrows():
        feature = MyPoint(row['CORPO_DAGU'], row['LONGITUDE'], row['LATITUDE'], row['icon'], row['MA1FOSFORO'])
        features.append(feature)
    return features

print('create geojson ok')

def make_map(features):
    print('>> Creating map...')
    m = folium.Map(coords_BR_NE, control_scale=True, zoom_start=6)

    icon_size = (15, 15)
    for feature in features:
        lat, lon = feature['geometry']['coordinates']
        icon_url = feature['properties']['icon']
        raw_pp = feature['properties']['popupcontent']
        
        icon = folium.features.CustomIcon(icon_url, icon_size=icon_size)
        pp = folium.Html(raw_pp, script=True)
        marker = folium.map.Marker([lon, lat], icon=icon, popup=folium.Popup(pp, max_width=2650))
        m.add_child(marker)

    colormap = folium.LinearColormap(['#053061','#2166ac','#4393c3','#92c5de','#d1e5f0','#fddbc7','#f4a582','#d6604d','#b2182b','#67001f'])
    colormap = colormap.to_step(index=[0, 0.3, 0.6, 0.9, 1.2, 1.5, 1.8, 2.1, 2.4, 2.7, 3.0])
    colormap.caption = 'Fósforo (ua)'
    colormap.add_to(m)
    return m

print('make map ok')

def plot_pollutant(pollutant_ID):
    print('Begin')
    df = load_data(pollutant_ID)
    df = prepare_data(df, pollutant_ID)
    features = create_geojson_features(df)
    return make_map(features), df

print('plot pollutant ok')

print('Begin function')

m, df = plot_pollutant(1)
m.save('map.html')