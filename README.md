# GNSS-EGNOS-EDAS-public_copy

*This repository is designed to gather data from 3 GNSS receivers at the same time and send them into a database.*  

*In this case, one receiver gets corrections from EGNOS, one gets correction from EDAS, and one stays autonomous.*


## File Descriptions:

- **sqlcreate.txt**: Input into the database to create tables.
- **run.py**: Runs `read_filtered1.py`, `read_filtered2.py`, and `read_filtered3.py` at the same time.
- **read_filtered1.py**: Retrieves data from the receiver set to autonomous.
- **read_filtered2.py**: Retrieves data from the receiver set to EGNOS.
- **read_filtered3.py**: Retrieves data from the receiver set to EDAS.


## Data visualization examples:

Comparison of 1 autonomous receiver and 2 EGNOS receivers:

[Dashboard Link - click here](https://snapshots.raintank.io/dashboard/snapshot/9vRxlHoB1VrEqLvYHcUIohfBoKkNbfC7?orgId=2)


## Serial ports settings on Linux:

For the proper functioning of the scripts, it is necessary to set the correct symbolic links to physical USB ports.

- Symbolic link for the EGNOS receiver is: "downblue"
- Symbolic link for the autonomous receiver is: "topblue"
- Symbolic link for the EDAS receiver is: "downblack"

To do that, you need to input the following into `/etc/udev/rules.d/10-local.rules`:

```
SUBSYSTEM=="tty", ATTRS{devpath}=="1.1", SYMLINK+="topblue" 
SUBSYSTEM=="tty", ATTRS{devpath}=="1.2", SYMLINK+="downblue"
SUBSYSTEM=="tty", ATTRS{devpath}=="1.4", SYMLINK+="downblack"
```

Where 1.1, 1.2 and 1.4 first number represents usb controller and second number represents  usb hub.<br>
After saving the `10-local.rules file`, you need to load these rules with the command:
```
sudo udevadm control --reload-rules
```
To obtain the USB controller and USB hub, use the command:
```
udevadm info -a /dev/ttyACM0
```
You will find these numbers in the following lines at the top:
```
looking at device '/devices/platform/scb/fd500000.pcie/pci0000:00/0000:00:00.0/0000:01:00.0/usb1/1-1/1-1.1/1-1.1:1.0/tty/ttyACM0'
looking at device '/devices/platform/scb/fd500000.pcie/pci0000:00/0000:00:00.0/0000:01:00.0/usb1/1-1/1-1.2/1-1.2:1.0/tty/ttyACM1':
```
To obtain the correct device file (/dev/ttyACM0), use:
```
dmesg
```
To test if everything works correctly, use:
```
ls -l /dev/topblue
ls -l /dev/downblue
```
