# GNSS-EGNOS-EDAS-public_copy
*This repository is designed to gather data form 3 gnss recievers at the same time and send them into database.*  <br>
*In this case one reciever gets corrections from egnos, one gets correction from edas and one stays autonomous.* <br><br>

**sqlcreate** - input into database to create tables <br>
**run.py** - runs read_filtered1.py, read_filtered2.py and read_filtered3.py at the same time <br>
**read_filtered1.py** - gets data from reciever set autonomous <br>
**read_filtered2.py** - gets data from reciever set to egnos <br>
**read_filtered3.py** - gets data from reciever set to edas <br>
