"""
Fetch raw weather records from NOAA.
"""

import ftplib
import gzip
import os


def fetch_raw_lite(year, station_id, retry=1, delete=False):
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
                return False

    # unzip the file
    with gzip.open('../raw/%s-%d.gz' % (station_id, year), 'rb') as f:
        with open('../raw/%s-%d.txt' % (station_id, year), 'w') as f2:
            file_content = f.read()
            f2.write(file_content)
            f2.close()
        f.close()
    os.remove('../raw/%s-%d.gz' % (station_id, year))
    if delete:
        os.remove('../raw/%s-%d.txt' % (station_id, year))
    return True
