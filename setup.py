from setuptools import setup, Extension
from setuptools.command.install import install
import os
import ConfigParser

try:
    import pkgconfig
    cflags = pkgconfig.cflags('xmlsec1').replace('\\', '')
    if not cflags:
        raise
    libs = pkgconfig.libs('xmlsec1')
except Exception:
    import traceback
    print '-' * 100
    traceback.print_exc()
    print '-' * 100
    import platform
    cflags = ("-DXMLSEC_CRYPTO=\"openssl\" -D__XMLSEC_FUNCTION__=__FUNCTION__"
              " -DXMLSEC_NO_GOST=1 -DXMLSEC_NO_XKMS=1"
              " -DXMLSEC_NO_CRYPTO_DYNAMIC_LOADING=1 -DXMLSEC_OPENSSL_100=1"
              " -DXMLSEC_CRYPTO_OPENSSL=1"
              " -I/usr/include/libxml2 -I/usr/include/xmlsec1")

    if platform.uname()[4] == 'x86_64':
        cflags = "-DXMLSEC_NO_SIZE_T " + cflags
    libs = "-lxmlsec1-openssl -lxmlsec1 -lssl -lcrypto -lxslt -lxml2"

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
    version='1.1.2',
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
            extra_compile_args=cflags.split(),
            extra_link_args=libs.split())],
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
