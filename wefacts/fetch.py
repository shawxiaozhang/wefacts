import ftplib
import gzip
import os
import logging

logging.basicConfig(level=logging.DEBUG, format='%(pathname)s:%(lineno)d %(message)s',)
logger = logging.getLogger(__name__)


def fetch_isd_lite(year, sid, retry_count=1):
    while retry_count > 0:
        try:
            ftp = ftplib.FTP('ftp.ncdc.noaa.gov')
            ftp.login()
            ftp.cwd('pub/data/noaa/isd-lite/%d' % year)
            ftp.retrbinary('RETR %s-%d.gz' % (sid, year), open('raw/%s-%d.gz' % (sid, year), 'wb').write)
            ftp.quit()
            break
        except ftplib.all_errors as e:
            retry_count -= 1
            if os.path.isfile('raw/%s-%d.gz' % (sid, year)):
                os.remove('raw/%s-%d.gz' % (sid, year))
        finally:
            if retry_count <= 0:
                return False

    # unzip the file
    with gzip.open('raw/%s-%d.gz' % (sid, year), 'rb') as f:
        with open('raw/%s-%d.txt' % (sid, year), 'w') as f2:
            file_content = f.read()
            f2.write(file_content)
            f2.close()
        f.close()
    os.remove('raw/%s-%d.gz' % (sid, year))
    return True


def test_ftp():
    fetch_isd_lite(2017, '724940-23234')


if __name__ == '__main__':
    test_ftp()
