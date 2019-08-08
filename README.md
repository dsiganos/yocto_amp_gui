# yocto_amp_gui
A python GUI for the yocto amp ammeter 
http://www.lfd.uci.edu/~gohlke/pythonlibs/#pyqt4

sudo apt-get install python-qt4 python-tk
pip install matplotlib

To access the USB device without root credentials, you need to install this udev rule:
`SUBSYSTEM=="usb", ATTRS{idVendor}=="24e0", ATTRS{idProduct}=="001f", MODE="0666"`

You can achieve that by copying "99-yocto_amp.rules" to /etc/udev/rules.d
cp 99-yocto_amp.rules /etc/udev/rules.d/
