from ftplib import FTP
import gzip
import os


def fetch_isd_lite(year, sid):
    ftp = FTP('ftp.ncdc.noaa.gov')
    ftp.login()
    ftp.cwd('pub/data/noaa/isd-lite/%d' % year)
    ftp.retrbinary('RETR %s-%d.gz' % (sid, year), open('raw/%s-%d.gz' % (sid, year), 'wb').write)
    ftp.quit()
    # unzip the file
    with gzip.open('raw/%s-%d.gz' % (sid, year), 'rb') as f:
        with open('raw/%s-%d.txt' % (sid, year), 'w') as f2:
            file_content = f.read()
            f2.write(file_content)
            f2.close()
        f.close()
    os.remove('raw/%s-%d.gz' % (sid, year))


def test_ftp():
    fetch_isd_lite(2017, '724940-23234')


if __name__ == '__main__':
    test_ftp()
