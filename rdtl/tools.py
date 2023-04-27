from pandas import DataFrame, Timestamp
from typing import Union
import matplotlib.pyplot as plt

def display_asset_count_in_each_zone(pixel_dataframe: DataFrame, current_time_est: Timestamp, site: str=None, map_filename: str=None, zone_coordinates_dataframe: DataFrame=None):
    """
    This function takes in a dataframe containing the pixel data (asset_id, zone, time_est) and a time and returns a bar chart that displays the number of assets in each zone.
    If a map_filename, zone_coordinates_dataframe, and site are provided, the function will also plot the zones on the map.

    Args:
        pixel_dataframe: a dataframe containing the pixel data (asset_id, zone, time_est)
        current_time_est: the estimated time of the event in eastern time
        site (optional): the site to display
        map_filename (optional): the filename of the map
        zone_coordinates_dataframe (optional): a dataframe containing the zone coordinates normalized from 0 to 100 (zone, x_coordinate, y_coordinate) ordered in the way that the zones should be plotted

    Returns:
        None
    """
    # throw error if there is a map_filename but no zone_coordinates_dataframe and vice versa
    if map_filename is not None and zone_coordinates_dataframe is None:
        raise ValueError('map_filename provided but no zone_coordinates_dataframe')
    if zone_coordinates_dataframe is not None and map_filename is None:
        raise ValueError('zone_coordinates_dataframe provided but no map_filename')
    if zone_coordinates_dataframe is not None and map_filename is not None and site is None:
        raise ValueError('zone_coordinates_dataframe and map_filename provided but no site')
    
    # check if pixel_dataframe has the correct columns (asset_id, zone, time_est) and throw error if not
    if 'asset_id' not in pixel_dataframe.columns:
        raise ValueError('pixel_dataframe does not contain the column "asset_id"')
    if 'zone' not in pixel_dataframe.columns:
        raise ValueError('pixel_dataframe does not contain the column "zone"')
    if 'time_est' not in pixel_dataframe.columns:
        raise ValueError('pixel_dataframe does not contain the column "time_est"')
    
    if site:
        # make sure site is valid
        if site not in pixel_dataframe['site'].unique():
            raise ValueError(f'site "{site}" is not a valid site')

    # assume that an asset is in the zone it was last seen in before the given time_est
    # filter the pixel_dataframe to only include the rows where the time_est is less than the time_est in the dataframe
    pixel_dataframe = pixel_dataframe[pixel_dataframe['time_est'] < current_time_est]

    # sort the dataframe by time_est and drop all duplicate asset_id rows, keeping only the last row for each asset_id
    # this will give us the last zone that each asset was in before the given time_est
    pixel_dataframe = pixel_dataframe.sort_values(by=['time_est']).drop_duplicates(subset=['asset_id'], keep='last')

    if site is not None:
       # filter the dataframe to only include the rows where the site is the given site
        pixel_dataframe = pixel_dataframe[pixel_dataframe['site'] == site]
        if pixel_dataframe.empty:
            print(f'pixel_dataframe does not contain any assets for site "{site}"')
            return

    # group the dataframe by zone and count the number of assets in each zone
    zone_counts = pixel_dataframe.groupby('zone').count()['asset_id']
    zone_counts = zone_counts.reset_index(name='asset_count')

    # plot the zone_counts as a bar chart
    formatted_time = current_time_est.strftime('%Y-%m-%d %X')
    zone_counts.plot(kind='bar', title=f'Number of Assets in Each Zone at {formatted_time} EST', xlabel='Zone', ylabel='Number of Assets', x='zone', y='asset_count', legend=False)

    # if map_filename, zone_coordinates_dataframe, and site are provided, plot the zones on the map
    if map_filename is not None and zone_coordinates_dataframe is not None and site is not None:
        # draw zone boundaries on the map using the zone_coordinates_dataframe
        # load map image
        map_image = plt.imread(map_filename)

        # create a figure and axes
        fig, ax = plt.subplots(figsize=(10, 10))

        # get image dimensions
        image_height = map_image.shape[0]
        image_width = map_image.shape[1]

        # plot the map image
        ax.imshow(map_image, extent = (0, image_width, 0, image_height))
        ax.axis('off')
        ax.set_title(f'Number of Assets in Each Zone at {formatted_time} EST')
        fig.tight_layout()

        # get a list of unique zones in the zone_coordinates_dataframe
        zones = zone_coordinates_dataframe['zone'].unique()

        # iterate through each zone and plot the zone boundary on the map using the zone_coordinates_dataframe
        for zone in zones:
            # filter the zone_coordinates_dataframe to only include the rows where the zone is the current zone
            zone_coordinates = zone_coordinates_dataframe[zone_coordinates_dataframe['zone'] == zone]

            # append the first x and y coordinates to the end of the list so that the zone boundary is closed
            zone_coordinates = zone_coordinates.reset_index(drop=True)
            zone_coordinates.loc[len(zone_coordinates)] = zone_coordinates.iloc[0]

            # get the x and y coordinates
            x_coordinates = zone_coordinates['x_coordinate']
            y_coordinates = zone_coordinates['y_coordinate']

            # normalize the x and y coordinates to the image dimensions
            x_coordinates = x_coordinates * image_width / 100
            y_coordinates = y_coordinates * image_height / 100

            # plot the zone boundary
            ax.plot(x_coordinates, y_coordinates)

            # label the zone if it is in the zone_counts dataframe
            if zone in zone_counts['zone'].values:
                # get the asset count for the current zone
                asset_count = zone_counts[zone_counts['zone'] == zone]['asset_count'].values[0]
                ax.text(x_coordinates.iloc[0], y_coordinates.iloc[0], s=asset_count, fontsize='xx-large', color='#000000', horizontalalignment='left', verticalalignment='bottom')

        plt.show()
        

CHART_TYPES = {'line', 'scatter', 'bar'}

def display_temperature_changes_over_time(pixel_dataframe: DataFrame, asset_id: str, chart_type: str=None, zone_subplots: Union[list, bool, str]=False):
    """
    This function takes in a dataframe containing the pixel data (asset_id, zone, time_est, temperature_c, temperature_f) and plots the temperature changes over time for a given asset_id.
    If a zone_subplot is provided, the function will also create sub-plots showing the temperature changes over time for the given asset_id in each listed zone.
        - The zone_subplots can be a list of zone names, a boolean value, or an individual zone name as a string.
        - If 'True' is supplied, the function will create subplots for all zones.

    Args:
        pixel_dataframe: a dataframe containing the pixel data (asset_id, zone, time_est, temperature_c, temperature_f)
        asset_id: the asset_id to plot
        chart_type (optional): the type of chart to plot (line, scatter, bar)
        subplots (optional): a list of zone names, a boolean value, or an individual zone name as a string

    Returns:
        None
    """
    # function body here
    pass

def display_time_in_zones(pixel_dataframe: DataFrame, asset_id: str, site: str=None):
    """
    This function takes in a dataframe containing the pixel data (asset_id, zone, site, time_est) and and asset ID and prints a spreadsheet showing how long the asset was in each zone.
    If a site is provided, the function will only display the zones for that site.

    Args:
        pixel_dataframe: a dataframe containing the pixel data (asset_id, zone, site, time_est)
        asset_id: the asset_id to plot
        site (optional): the site to display

    Returns:
        None
    """
    # function body here
    pass

def display_time_outliers_in_zones(pixel_dataframe: DataFrame, outlier_dataframe: DataFrame, asset_id: str=None, site: str=None):
    """
    This function takes in a dataframe containing the pixel data (asset_id, zone, site, time_est) and an outlier dataframe (zone, expected_time, acceptable_time_difference) and prints a spreadsheet displaying all the outliers.
    If an asset_id is provided, the function will only display the outliers for that asset.
    If a site is provided, the function will only display the outliers for that site.

    Args:
        pixel_dataframe: a dataframe containing the pixel data (asset_id, zone, site, time_est)
        outlier_dataframe: a dataframe containing the outlier data (zone, expected_time, acceptable_time_difference)
        asset_id (optional): the asset_id to plot
        site (optional): the site to display

    Returns:
        None
    """
    # function body here
    pass

def display_asset_journey(pixel_dataframe: DataFrame, asset_id: str, site: Union[list, str]=None):
    """
    This function takes in a dataframe containing the pixel data (asset_id, latitude, longitude, time_est, site) and plots the journey of the asset over time.
    If a site is provided, the function will only display location data for that site.
        - The sites can be a list of site names or an individual site name as a string.
        - If left empty, the function will display the journey for all sites.

    Args:
        pixel_dataframe: a dataframe containing the pixel data (asset_id, latitude, longitude, time_est, site)
        asset_id: the asset_id to plot
        site (optional): a list of site names or an individual site name as a string
    """
    # function body here
    pass