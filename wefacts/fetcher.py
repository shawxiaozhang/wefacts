"""
Fetch raw weather records from NOAA.
"""

import ftplib
import gzip
import os
import datetime


def fetch_raw_lite(year, station_id, retry=1):
    while retry > 0:
        try:
            ftp = ftplib.FTP('ftp.ncdc.noaa.gov')
            ftp.login()
            ftp.cwd('pub/data/noaa/isd-lite/%d' % year)
            ftp.retrbinary('RETR %s-%d.gz' % (station_id, year), open('../raw/%s-%d.gz' % (station_id, year), 'wb').write)
            ftp.quit()
            break
        except ftplib.all_errors as e:
            retry -= 1
            if os.path.isfile('../raw/%s-%d.gz' % (station_id, year)):
                os.remove('../raw/%s-%d.gz' % (station_id, year))
        finally:
            if retry <= 0:
                return None

    # unzip the file
    with gzip.open('../raw/%s-%d.gz' % (station_id, year), 'rb') as f:
        with open('../raw/%s-%d.txt' % (station_id, year), 'w') as f2:
            file_content = f.read()
            f2.write(file_content)
            f2.close()
        f.close()
    os.remove('../raw/%s-%d.gz' % (station_id, year))
    return ['%s-%d.txt' % (station_id, year)]


def fetch_raw_severe_weather(category, date_start, date_end):
    current_year, current_month = datetime.datetime.now().year, datetime.datetime.now().month
    for year in xrange(date_start.year, date_end.year+1):
        if year < current_year:
            if not os.path.isfile('../raw/%s-%4d.csv' % (category, year)):
                _fetch_raw_sw(category, year)
        elif year == current_year:
            m1 = 1 if date_start.year < current_year else date_start.month
            m2 = date_end.month
            for month in xrange(m1, m2+1):
                if month == m2 or not os.path.isfile('../raw/%s-%4d%2d.csv' % (category, year, month)):
                    _fetch_raw_sw(category, year, month)
    return 'OK'


def _fetch_raw_sw(category, year, month=None, retry=1):
    if year > datetime.datetime.now().year:
        return None
    elif year < datetime.datetime.now().year:
        file_names = ['%s-%4d.csv' % (category, year)]
    elif month is not None and isinstance(month, int) and 1 <= month <= 12:
        file_names = ['%s-%4d%02d.csv' % (category, year, month)]
    else:
        file_names = ['%s-%4d%02d.csv' % (category, year, m+1) for m in xrange(datetime.datetime.now().month)]

    fetched = set()
    while retry > 0 and len(file_names) > 0:
        try:
            ftp = ftplib.FTP('ftp.ncdc.noaa.gov')
            ftp.login()
            ftp.cwd('pub/data/swdi/database-csv/v2/')
            for file_name in file_names:
                ftp.retrbinary('RETR %s.gz' % file_name, open('../raw/%s.gz' % file_name, 'wb').write)
                fetched.add(file_name)
            ftp.quit()
            break
        except ftplib.all_errors as e:
            retry -= 1
        finally:
            file_names = [f for f in file_names if f not in fetched]
            for f in file_names:
                if os.path.isfile('../raw/%s.gz' % f):
                    os.remove('../raw/%s.gz' % f)

    # unzip the file
    for file_name in fetched:
        with gzip.open('../raw/%s.gz' % file_name, 'rb') as f:
            with open('../raw/%s' % file_name, 'w') as f2:
                file_content = f.read()
                f2.write(file_content)
                f2.close()
            f.close()
        os.remove('../raw/%s.gz' % file_name)
    return list(fetched)
