# yocto_amp_gui
A python GUI for the yocto amp ammeter 
http://www.lfd.uci.edu/~gohlke/pythonlibs/#pyqt4

`sudo apt-get install python-qt4 python-tk`  
`pip install matplotlib`

To access the USB device without root credentials, you need to install this udev rule:  
`SUBSYSTEM=="usb", ATTRS{idVendor}=="24e0", ATTRS{idProduct}=="001f", MODE="0666"`

You can achieve that by copying "99-yocto_amp.rules" to /etc/udev/rules.d:  
`cp 99-yocto_amp.rules /etc/udev/rules.d/`

When you start the program you will be meet with 4 buttons, to start the data capture press start.

Once it has been started the program will give out time and amps seprated by a comma, the amount the amps are checked per second and length of the reading is determined by the two editable dropdown menus in the bottom right conner of the gui.

to stop the test press stop and the data will be saved in a csv file in the data folder.

display will show a graph of the data so far while live will show a live graph of the data updating as new data comes in.
