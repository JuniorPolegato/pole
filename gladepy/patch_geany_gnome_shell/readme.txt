When using Geany on Gnome Shell, this doesn't present to user when run gladepy because Geany opens the prompt dialog to reload changed file, so I did a patch to call this dialog one milisecond after Geany present itself to user.

Do this to apply this patch (replace "su -c" by "sudo" if you on Ubuntu or if you have already configured sudo):

mkdir /tmp/geany
cp 20_timeout_for_prompt_dialog.patch /tmp/geany
cd /tmp/geany
apt-get source geany
su -c 'apt-get build-dep geany'
su -c 'apt-get install devscripts'
echo 20_timeout_for_prompt_dialog.patch >> geany-*/debian/patches/series
mv 20_timeout_for_prompt_dialog.patch geany-*/debian/patches/
cd geany-*/
dch -i "Timeout to show prompt dialog for reload changed file to show main window before."
dpkg-buildpackage -d -us -uc
cd ..
su -c 'dpkg -i *.deb'
