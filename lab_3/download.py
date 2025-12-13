import cdsapi
import xarray as xr

client = cdsapi.Client()

dataset = 'cams-europe-air-quality-reanalyses'
request = {
    "variable": ["particulate_matter_2.5um"],
    "model": ["ensemble"],
    "level": ["0"],
    "type": ["interim_reanalysis"],
    "year": ["2023"],
    "month": ["01"]
}
target = 'cams_data.nc'

client.retrieve(dataset, request, target)

# Încărcarea datelor NetCDF
ds = xr.open_dataset('cams_data.nc')

# Medie zilnică peste Europa
pm25_daily = ds['pm2p5'].resample(time='1D').mean().mean(dim=['latitude', 'longitude'])
df = pm25_daily.to_dataframe().reset_index()
df.rename(columns={'time': 'date', 'pm2p5': 'pm25'}, inplace=True)
df['latitude'] = ds.latitude.mean().values
df['longitude'] = ds.longitude.mean().values

# Salvează ca CSV pentru app
df.to_csv('cams_data.csv', index=False)
print(df.head())