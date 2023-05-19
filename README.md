# GNSS-EGNOS-EDAS-public_copy
*This repository is designed to gather data from 3 gnss recievers at the same time and send them into database.*  <br>
*In this case one reciever gets corrections from egnos, one gets correction from edas and one stays autonomous.* <br><br>

**sqlcreate** - input into database to create tables <br>
**run.py** - runs read_filtered1.py, read_filtered2.py and read_filtered3.py at the same time <br>
**read_filtered1.py** - gets data from reciever set autonomous <br>
**read_filtered2.py** - gets data from reciever set to egnos <br>
**read_filtered3.py** - gets data from reciever set to edas <br>

## Data visualization examples:
Comparison of 1 autonomous reciever and 2 EGNOS recievers: <br>
https://jehlijos.grafana.net/d/da64739a-d2fe-411f-948b-3039347e8972/gnss-egnos-and-edas-solution-comparison?orgId=1&theme=dark



## Serial ports settings on linux
For righ function of the skripts is nessesary to set right symbolic links to physical usb ports <br>
Symbolic link for egnos reciver is: "downblue" <br>
Symbolic link for autonomous reciver is: "topblue" <br>
Symbolic link for edas reciver is: "downblack" <br><br>
To do that u need to input this into /etc/udev/rules.d/10-local.rules
``` 10-local.rules
SUBSYSTEM=="tty", ATTRS{devpath}=="1.1", SYMLINK+="topblue" 
SUBSYSTEM=="tty", ATTRS{devpath}=="1.2", SYMLINK+="downblue"
SUBSYSTEM=="tty", ATTRS{devpath}=="1.4", SYMLINK+="downblack"
```
<br> where 1.1, 1.2 first number is usb controller and second number is usb hub.<br>
After saving 10-local.rules file u need to load these rules with command:
```
sudo udevadm control --reload-rules
```
To get  usb controller and usb hub use command:
```
udevadm info -a /dev/ttyACM0
```
You will find these numbers in theese lines at the top:
```
looking at device '/devices/platform/scb/fd500000.pcie/pci0000:00/0000:00:00.0/0000:01:00.0/usb1/1-1/1-1.1/1-1.1:1.0/tty/ttyACM0'
looking at device '/devices/platform/scb/fd500000.pcie/pci0000:00/0000:00:00.0/0000:01:00.0/usb1/1-1/1-1.2/1-1.2:1.0/tty/ttyACM1':
```
to obtain right device file  (/dev/ttyACM0) use:
```
dmesg
```
To test if everything works right use:
```
ls -l /dev/topblue
ls -l /dev/downblue
```
