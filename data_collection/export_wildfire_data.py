from datetime import datetime, timedelta
import logging
import traceback
import ee
from ee.imagecollection import ImageCollection
from ee.image import Image
from ee.batch import Export


logging.basicConfig(
    filename='error_log.log',  # Log file name
    level=logging.ERROR,       # Log only errors and above
    format='%(levelname)s - %(message)s'  # Log format: level name and message
)



#Auth and Init
ee.Authenticate()
ee.Initialize()


fire_cltn = ImageCollection('MODIS/061/MOD14A1')
elevation_img = Image('CGIAR/SRTM90_V4')
weather_cltn: ImageCollection = ImageCollection('IDAHO_EPSCOR/GRIDMET')
drought_cltn = ImageCollection('GRIDMET/DROUGHT')
vegetation_cltn = ImageCollection('NOAA/VIIRS/001/VNP13A1')
population_density_img = ImageCollection('CIESIN/GPWv411/GPW_Population_Density')

colorado_polygon = ee.geometry.Geometry.Polygon([
    [-109.04785486659851,36.993281070894604],
    [-102.04212011725402,36.993281070894604],
    [-102.04212011725402,41.00143097730514],
    [-109.04785486659851,41.00143097730514],
    [-109.04785486659851,36.993281070894604]
])

crs = "EPSG:2232"

def export_single_day(input_date: datetime):

    date = ee.Date.fromYMD(input_date.year, input_date.month, input_date.day)


    fire_filtered = fire_cltn.filterDate(date).first().select('FireMask').reproject(**{
        'crs': crs,
        'scale': 1000
    })
    fire_filtered_next = fire_cltn.filterDate(date.advance(1, 'day')).first().select('FireMask').reproject(**{
        'crs': crs,
        'scale': 1000
    })

    fire_data = fire_filtered.gte(7).multiply(2).bitwiseOr(fire_filtered.lte(2).Or(fire_filtered.eq(4)).Or(fire_filtered.eq(6)))
    fire_data_next = fire_filtered_next.gte(7).multiply(2).bitwiseOr(fire_filtered_next.lte(2).Or(fire_filtered_next.eq(4)).Or(fire_filtered_next.eq(6)))

    fire_data = fire_data.addBands(fire_data_next).rename('fire_mask', 'fire_mask_next_day')


    elevation_data = elevation_img.select('elevation').reproject(**{
        'crs': crs,
        'scale': 1000
    })

    fire_data = fire_data.addBands(elevation_data)


    weather_data = weather_cltn.filterDate(date, date.advance(1, 'day')).filterBounds(colorado_polygon).first().select(['th', 'vs', 'erc', 'bi', 'pr', 'tmmn', 'tmmx']).resample('bicubic').reproject(**{
        'crs': crs,
        'scale': 1000
    }).rename('wind_direction', 'wind_speed', 'energy_release_component', 'burn_index', 'precipitation', 'tempature_min', 'tempature_max')

    fire_data = fire_data.addBands(weather_data)

    drought_data = drought_cltn.filterDate(date.advance(-30, 'day'), date).filterBounds(colorado_polygon).sort('system:time_start', False).first().select(['pdsi']).resample('bicubic').reproject(**{
        'crs': crs,
        'scale': 1000
    }).rename('drought_index')

    fire_data = fire_data.addBands(drought_data)
    vegetation_data = vegetation_cltn.filterDate(date.advance(-30, 'day'), date).filterBounds(colorado_polygon).sort('system:time_start', False).first().select(['NDVI']).reproject(**{
        'crs': crs,
        'scale': 1000
    }).rename('vegetation')

    fire_data = fire_data.addBands(vegetation_data)

    pop_density_data = population_density_img.filterBounds(colorado_polygon).sort('system:time_start', False).first().reproject(**{
        'crs': crs,
        'scale': 1000
    })

    fire_data = fire_data.addBands(pop_density_data)



    export_options = {
        'patchDimensions': [64, 64],
        'compressed': True
    }

    export = Export.image.toDrive(**{
        'image': fire_data.float(),
        'description': 'PatchesExport',
        'fileNamePrefix': f"FireData_{input_date.strftime('%Y%m%d')}",
        'scale': 1000,
        'folder': 'FireEyeExportActual',
        'fileFormat': 'TFRecord',
        'region': colorado_polygon,
        'crs': crs,
        'formatOptions': export_options,  
    })

    export.start()



def main():
    start_datetime = datetime(2020, 1, 1)
    end_datetime = datetime(2024, 6, 1)

    skip_months = [10, 11, 12, 1, 2, 3]


    while(start_datetime <= end_datetime):
        
        if(start_datetime.month not in skip_months):
            print("Queueing", start_datetime.strftime('%Y-%m-%d'))
            try:
                export_single_day(start_datetime)
            except Exception as e:
                logging.error(f"\n\n{start_datetime.strftime('%Y-%m-%d')} did not export correctly {e}")
                logging.error(traceback.format_exc())
        start_datetime += timedelta(days=1)



if __name__ == '__main__':
    main()