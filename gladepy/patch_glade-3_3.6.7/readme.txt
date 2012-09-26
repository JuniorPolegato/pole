Patches for Glade-3 to call external program from grid of signals/events.

This bash script will patch and repackage Glade-3 3.6.7 on Debian 6.0 Squeeze version.

It will add a column with toggle control on grid of signals/events and its click will call
a function which will save the project and call the external program
${HOME}/bin/glade-code-generator with 2 (two) parameters: the path of saved
project and the name of function beside of toggle.

cd /tmp
rm -rf glade-* *.patch
wget http://www.juniorpolegato.com.br/gladepy-0.3/glade-code-generator.patch
wget http://www.juniorpolegato.com.br/gladepy-0.3/changelog.patch
wget http://www.juniorpolegato.com.br/gladepy-0.3/rules.patch
# Glade 3 is version 3.6.7 in current stable Debian 6.0 Squeeze
apt-get -t squeeze source glade
patch -p0 < glade-code-generator.patch
patch -p0 < changelog.patch
patch -p0 < rules.patch
su -c 'apt-get build-dep glade'
cd glade-3-3.6.7
dpkg-buildpackage -d
cd ..
su -c 'dpkg -i glade_3.6.7-1.1_i386.deb libgladeui-1-9_3.6.7-1.1_i386.deb'

After dpkgbuildpackage runs configure script, you will need verify if the configuration result is "yes" for everyone, like this:


Configuration:

    Source code location:    .
    Compiler:                gcc
    GTK+ UNIX Print Widgets: yes
    GNOME UI Widgets:        yes
    PYTHON Widgets support:  yes

    Build Reference Manual:  yes
    Build User Manual:       yes


With this patch finished, now you need create a executable file with name glade-code-generator in bin directory in your home directory.

You can rename your program or make a link to also.

Glade patched will pass to ~/bin/glade-code-generator the parameters "XML file name" and "function name".

Enjoy.

Junior Polegato
