import pandas as pd
import geojson
from geojson import Feature, Point, FeatureCollection


def _get_longlat(df, longlat):
    """
    Extracts longitude and latitude from the given DataFrame.
    
    Parameters
    ----------
    df : DataFrame
    longlat : string or list of two strings
        List of two column names is used when longitude and latitude are stored in
        two separat columns. String is used if longitude and latitude are stored
        in a single column separated by a comma.
    
    Returns
    -------
    DataFrame
        DataFrame containing exactly two columns: longitude ('Long') and latitude ('Lat').
    """
    # longlat = ['name1', 'name2']
    # name1 and name2 refer to columns of longitude and latitude, respectively
    if isinstance(longlat, list):
        assert len(longlat) == 2, \
            'Exactly two column names expected. Found: %r' % longlat
        assert isinstance(longlat[0], str) and isinstance(longlat[1], str), \
            'Expected "longlat" to be a list of two strings. Found: %r' % longlat
        return pd.DataFrame({'Long':df[longlat[0]], 'Lat':df[longlat[1]]})
    
    # longlat = 'name1'
    # name1 refers to column containing longitude and latitude, separated by a comma
    if isinstance(longlat, str):
        return df[longlat].str.split(',', expand=True).rename(columns={0:'Long', 1:'Lat'})
    
    raise TypeError('Parameter "longlat" is neither a string nor a list of strings')


def read_excel(io, longlat, properties=None, sheet_name=0, header=0):
    """
    Reads an Excel table containing geolocatiin data into a pandas DataFrame.
    
    Parameters
    ----------
    io : string, path object, file-like object, pandas ExcelFile, or xlrd workbook
    longlat : string or list of two strings
        List of two column names is used when longitude and latitude are stored in
        two separat columns. String is used if longitude and latitude are stored
        in a single column separated by a comma.
    properties : List of strings or None, default None
        Determines the columns to be stored in the GeoJSON's properties field.
        None if all columns are stored or a list of column names for a subset.
    sheet_name : string or int, default 0
        Strings are used for sheet names, Integers are used in 0-indexed sheet positions.
    header : int, default 0
        Row (0-indexed) to use for the column labels of the parsed DataFrame.
    
    Returns
    -------
    DataFrame
        DataFrame from the passed in Excel file.
    """
    df = pd.read_excel(io, sheet_name=sheet_name, header=header)

    df_longlat = _get_longlat(df, longlat)

    assert properties is None or isinstance(properties, list), \
        'Expected "properties" to be either a list of strings or None. Found: %' % properties
    if properties is None:
        properties = df.columns.difference(longlat if isinstance(longlat, list) else [longlat])
    df_properties = df[properties]

    return pd.concat([df_longlat, df_properties], axis=1)


def _create_feature_collection(df):
    """
    Creates a FeatureCollection for a given DataFrame.
    
    Parameters
    ----------
    df : DataFrame
        The DataFrame is expected to have columns named 'Long' and 'Lat' and
        optionally any other property columns.
    
    Returns
    -------
    FeatureCollection
        A collection of Features containing Point geometries.
    """
    fcollection = []
    properties = df.columns.difference(['Long', 'Lat'])
    for _, row in df.iterrows():
        fcollection.append(Feature(geometry=Point((row['Long'], row['Lat'])),
                                   properties={x:row[x] for x in properties}))
    return FeatureCollection(fcollection)


def write_geojson(df, path_out):
    """
    Writes the given DataFrame into a GeoJSON file.
    
    Parameters
    ----------
    df : DataFrame
        The DataFrame is expected to have columns named 'Long' and 'Lat' and
        optionally any other property columns.
    path_out : string or file-like object
    """
    fcollection = _create_feature_collection(df)
    if not path_out.endswith('.geojson'):
        path_out += '.geojson'
    geojson.dump(fcollection, path_out)

