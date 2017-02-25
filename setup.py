from setuptools import setup

INSTALL_REQUIRES = [
    'geopy',
    'pandas',
    'Geohash',
    'matplotlib'
]

TESTS_REQUIRES = []

setup(name='wefacts',
      version='0.1.0',
      description='Weather Facts: historical weather data provider.',
      url='https://github.com/shawxiaozhang/wefacts',
      author='Xiao Zhang',
      author_email='shawxiaozhang@gmail.com',
      license='MIT',
      test_suite='nose.collector',
      tests_require=['nose'],
      packages=['wefacts'],
      zip_safe=False)