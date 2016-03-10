from distutils.core import setup

setup(
    name='Pole',
    version='1.0.0',
    author='Junior Polegato',
    author_email='linux@juniorpolegato.com.br',
    packages=['pole', 'pole.test'],
    scripts=['bin/gladepy.py', 'bin/baixar_pole_github'],
    url='http://pypi.python.org/pypi/Pole/',
    license='LICENSE.txt',
    description='A micro framework for PyGtk, PDF, XML, Utils Functions and Brazilan NFe.',
    long_description=open('README.md').read(),
    install_requires=[
        #'cairo >= 1.1.0',
        #'cx_Oracle >= 5.1.0',
        #'dateutil >= 0.1.0',
        #'gtk2 >= 2.16.0',
        #'lxml >= 3.0.0',
        #'pytz >= 2008.0.0',
        #'reportlab >= 3.0.0',
        #'suds >= 0.7'
    ],
)
