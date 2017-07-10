# from setuptools import setup
from distutils.core import setup

INSTALL_REQUIRES = [
    'geopy',
    'pandas',
    'Geohash',
    'matplotlib'
]

TESTS_REQUIRES = []

setup(name='wefacts',
      version='0.1.10',
      description='Weather Facts: get historical weather data.',
      url='https://github.com/shawxiaozhang/wefacts',
      author='Xiao Zhang',
      author_email='shawxiaozhang@gmail.com',
      license='MIT',
      test_suite='nose.collector',
      tests_require=['nose'],
      packages=['wefacts'],
      install_requires=[
          'geopy==1.11.0',
          'Geohash==1.0',
          'pandas==0.19.2',
          'numpy==1.12.0',
          'python-dateutil==2.6.0',
      ],
      zip_safe=False)