from setuptools import setup, Extension
from setuptools.command.install import install
import os
import ConfigParser

config = ConfigParser.ConfigParser()
config.read('setup.cfg')
locale_dir = config.get("compile_catalog", "directory")
domain = config.get("compile_catalog", "domain")

locale_files = [(os.path.join('share', 'locale', locale, 'LC_MESSAGES'),
                 [os.path.join(locale_dir, locale, 'LC_MESSAGES',
                               domain + ".mo")])
                for locale in os.listdir(locale_dir)]

gladepy_files = [(os.path.join('share', 'pole', 'gladepy'),
                 [os.path.join('gladepy', '.gladepy.conf'),
                  os.path.join('gladepy', 'glade-code-generator')])]

glade_files = [(os.path.join('share', 'pole', 'glade'),
               reduce(lambda x, y: x + y,
                      [[os.path.join(top, f) for f in files
                        if f.rsplit('.', 1)[-1] in ("deb", "patch", "txt")]
                       for top, dirs, files
                       in os.walk('gladepy/patch_glade-3_3.6.7')]))]

nfe_files = [(os.path.join('share', 'pole', top),
              [os.path.join(top, f) for f in files])
             for top, dirs, files in os.walk('NFe') if files]


class xinstall(install):
    def run(self):
        from babel.messages.frontend import compile_catalog
        po_compiler = compile_catalog(self.distribution)
        po_compiler.initialize_options()
        po_compiler.domain = domain
        po_compiler.directory = locale_dir
        po_compiler.finalize_options()
        po_compiler.run()
        install.run(self)


setup(
    name=domain,
    version='1.0.0',
    author='Junior Polegato',
    author_email='linux@juniorpolegato.com.br',
    packages=[domain],
    package_dir={domain: 'src/' + domain},
    scripts=['gladepy/gladepy.py'],
    message_extractors={'src/' + domain: [('**.py', 'python', None)]},
    data_files=locale_files + gladepy_files + glade_files + nfe_files,
    url='http://pypi.python.org/pypi/pole/',
    license='LICENSE.txt',
    description=('A micro framework for PyGtk, PDF, XML, Utilities'
                 ' and Brazilan NFe.'),
    long_description=open('README.md').read(),
    keywords=['pole', 'pygtk', 'gtk', 'gtk+', 'nfe', 'xml', 'pdf', 'util'],
    # install_requires=['cairo >= 1.1.0', 'cx_Oracle >= 5.1.0',
    #                   'dateutil >= 0.1.0', 'gtk2 >= 2.16.0',
    #                   'lxml >= 3.0.0', 'pytz >= 2008.0.0',
    #                   'reportlab >= 3.0.0', 'suds >= 0.7],
    ext_modules=[
        Extension(
            'pole.PoleXmlSec',
            sources=['src/pole/PoleXmlSec.c'],
            extra_compile_args=["-I/usr/include/libxml2",
                                "-I/usr/include/xmlsec1"],
            extra_link_args=["-lxml2", "-lxmlsec1", "-lxmlsec1-openssl"])],
    cmdclass={'install': xinstall},
    classifiers=[
        'Development Status :: 5 - Production/Stable',
        'Environment :: X11 Applications',
        'Environment :: X11 Applications :: GTK',
        'Environment :: Console',
        'Environment :: Win32 (MS Windows)',
        'Intended Audience :: Developers',
        'License :: OSI Approved :: GNU Lesser General Public License v3 (LGPLv3)',
        'Operating System :: MacOS :: MacOS X',
        'Operating System :: Microsoft :: Windows :: Windows NT/2000',
        'Operating System :: Microsoft',
        'Operating System :: OS Independent',
        'Operating System :: POSIX :: Linux',
        'Programming Language :: C',
        'Programming Language :: Python :: 2.7',
        'Programming Language :: Python :: Implementation :: CPython',
        'Programming Language :: Python :: Implementation :: PyPy',
        'Programming Language :: Python',
        'Topic :: Software Development :: Libraries :: Python Modules',
        'Topic :: Software Development :: Libraries',
        'Topic :: Utilities',
        ],
)
