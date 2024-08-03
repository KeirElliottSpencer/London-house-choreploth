import pandas as pd
import plotly.express as px
import json

london_dataset = pd.read_csv('house_price_index.csv')
london_dataset.head()
london_dataset.info()

london_dataset = london_dataset.drop(columns=['Unnamed: 47'])
london_dataset = london_dataset.rename(columns={'Unnamed: 0': 'date'})

london_dataset['year'] = pd.to_datetime(london_dataset['date'], format='%b-%y').dt.year
london_dataset['month'] = pd.to_datetime(london_dataset['date'], format='%b-%y').dt.month_name()

london_dataset = london_dataset.drop(columns=['date'])
codes = london_dataset.iloc[0]
london_dataset = london_dataset.melt(id_vars=['year', 'month'], var_name='name', value_name='average_price')

london_dataset = london_dataset.dropna()
codes_dict = codes.to_dict()
london_dataset['place_code'] = london_dataset['name'].map(codes_dict)
london_dataset['average_price'] = london_dataset['average_price'].str.replace(',', '').astype(float).round(0).astype(int)
london_dataset['year'] = london_dataset['year'].astype(int).astype(str)

#london_dataset.isnull().values.any()
#london_dataset.isnull().sum()

london_dataset = london_dataset.groupby(['year', 'place_code', 'name'])['average_price'].mean().reset_index()
london_dataset['average_price'] = london_dataset['average_price'].round(0).astype(int)
london_dataset['formatted_price'] = london_dataset['average_price'].apply(lambda x: f"£{x:,.0f}")
london_dataset = london_dataset[london_dataset['place_code'].str.startswith('E09')]

london_dataset.info()
london_dataset.head()

with open('/Users/elysia/Downloads/lad.json') as f:
    geojson = json.load(f)

a = london_dataset['place_code'].unique()

filtered_features = [
    feature for feature in geojson['features']
    if feature['properties'].get('LAD13CD') in a
]
filtered_geojson = {
    'type': 'FeatureCollection',
    'features': filtered_features
}
with open('filtered_geojson.geojson', 'w') as f:
    json.dump(filtered_geojson, f)
with open('/Users/elysia/Coding Projects Repos/London-house-choreploth/filtered_geojson.geojson') as f:
    geojson = json.load(f)

global_min_price = london_dataset['average_price'].min()
global_max_price = london_dataset['average_price'].max()

fig = px.choropleth(london_dataset,
                    geojson=geojson,
                    locations='place_code',
                    color='average_price',
                    featureidkey="properties.LAD13CD",
                    hover_name='name',
                    hover_data={'average_price': False, 'formatted_price': True},
                    animation_frame='year',
                    title="Average House Prices in London Boroughs",
                    labels={'formatted_price':'Average Price'},
                    color_continuous_scale=px.colors.sequential.Plasma,
                    range_color=[global_min_price, global_max_price]
                    )

fig.update_geos(fitbounds="locations", visible=False)
fig.update_layout(
    margin=dict(l=20, r=20, t=40, b=20),
    paper_bgcolor='rgba(243, 243, 243, 0.8)',
    font=dict(family="Arial, sans-serif", size=18, color="#000000"),
    title_font=dict(size=18, color="#000000"),
    title_x=0.5
)
fig.update_geos(projection_type="orthographic")
fig.update_coloraxes(colorscale="Viridis", colorbar_title="Average Price (£)")
fig.show(renderer="browser")