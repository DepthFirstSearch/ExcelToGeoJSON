import pandas as pd


def _get_longlat(df, longlat):
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
    df = pd.read_excel(io, sheet_name=sheet_name, header=header)
    df_longlat = _get_longlat(df, longlat)
    return df_longlat
