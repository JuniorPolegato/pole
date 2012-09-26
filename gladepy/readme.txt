GladePy is a Python project to make easy the generation and interation of your code with the Pole module and Glade 3.6.7 for while.

The gladepy.py is a Python script wich read Glade XML and return a Python code file using Pole module and with callback functions and a minimal documentation.

Running gladepy.py again, it updates your code including new callback functions and updates the minimal documentation.

This script uses a configuration file, .gladepy.conf, reading it from your home directory and you can select to aggregate Glade XML or use it from one discrete file, the "join" option.

It also can open a editor and positioning the cursor in a function with options "editor", "line_option" and "column_option".

If you use Geany for your code edition, you can configure .gladepy.conf file like  one in this directory:
editor = "geany"
line_option = "--line"
column_option = "--column"
join = True

You can also modify Glade interface to call a external program and this program calls gladepy.py, see the patch_glade-3_3.6.7 directory for Glade patch.

With this patch, you need create a executable file with name glade-code-generator in bin directory in your home directory. You can rename your program or make a link to also. Glade patched will pass to ~/bin/glade-code-generator the parameters "XML file name" and "function name".

Enjoy.

Junior Polegato
