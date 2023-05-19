# GGA
# GSA
# GSV
# GST
# EDAS GNSS RECIEVER, PORT SYMBOLIC LINK: downblack, RECIEVER =3 

#  port - ttyACM0
import serial
import pynmea2
import mysql.connector
from mysql.connector import Error
import time
import math
import sys
from datetime import datetime

# conection paramates for database
login = {
    'user': 'gnssegnosedas',
    'password': '',
    'host': '',
    'database': 'gnssegnosedas',
   # 'charset': 'utf8mb3'
    }


try:
    connection = mysql.connector.connect(**login)
    if connection.is_connected():
        db_Info = connection.get_server_info()  # connection to database
        print("Connected to MySQL Server version ", db_Info)
        cursor = connection.cursor(prepared=True)  # prepared = True - means that query is parameterized, increases speed
        cursor.execute("select database();")
        record = cursor.fetchone()
        print("You're connected to database: ", record)

except Error as e:
    print("Error while connecting to MySQL", e)
    sys.exit()
print(" ______________CONNECTED________________")
reciever = 3  # ID by type of reciever (EGNOSxEDAS)
i = 0
i_gsa = 0
i_gsv = 0
egnos = 0
tracked_count = 0
lat_list =[]
lon_list =[]
altitude_list = []
geosep_list = []
numsats_list = []
fixqual_list = []
pdop_list = []
hdop_list = []
vdop_list = []
rms_list = []
siglat_list = [] 
siglong_list = []
sigalt_list = []
trckd_sat_list = []

def egnos_check(): #function that checks for egnos nmeaID in gsv nmea msg
    global gsv
    global egnos
    # diferrent checking for length of the message
    if  len(gsv.data) == 7 and 33 < int(gsv.data[3]) > 52 :
        egnos = 1
    elif  len(gsv.data) == 11 and 33 < int(gsv.data[3]) > 52 or 33 < int(gsv.data[8]) > 52 :
        egnos = 1
    elif  len(gsv.data) == 15 and 33 < int(gsv.data[3]) > 52 or 33 < int(gsv.data[8]) > 52 or 33 < int(gsv.data[12]) > 52:
        egnos = 1
    elif  len(gsv.data) == 19 and 33 < int(gsv.data[3]) > 52 or 33 < int(gsv.data[8]) > 52 or 33 < int(gsv.data[12]) > 52 or 33 < int(gsv.data[16]) > 52:
        egnos = 1
    else: egnos = 0

def exclude_non_numbers(lst):
    return [value for value in lst if isinstance(value, (float,int))]

def endcycle():  # functions that runs at the end of one loop
    global i
    global gga
    global i_gsa
    global timestamp
    global reciever
    global gsa
    global gst
    global egnos
    global now_time
    global tracked_count
    global main_write_time
    global lat_list
    global lon_list
    global altitude_list
    global geosep_list
    global numsats_list
    global fixqual_list
    global pdop_list
    global hdop_list
    global vdop_list
    global rms_list
    global siglat_list 
    global siglong_list
    global sigalt_list
    global trckd_sat_list
    
    main_write_time = main_write_time + 15 # sets time of next database input 15 secs from now
    
    
    for x in range(len(lat_list)):   
        if gga.lat_dir == "S":  # negative coordinates check
            try:lat_list[x] = float(lat_list[x]) * (-1)
            except: pass
        else:
            try: lat_list[x] = float(lat_list[x])
            except: pass
    for x in range(len(lon_list)): 
        if gga.lon_dir == "W":
            try: lon_list[x] = float(lon_list[x] ) * (-1)
            except: pass
        else:
            try: lon_list[x]  = float(lon_list[x] )
            except: pass
    # using previous function to exclude empty strings, that comes from nmea when value is missing  
    lat_list = exclude_non_numbers(lat_list)
    lon_list = exclude_non_numbers(lon_list)
    altitude_list = exclude_non_numbers(altitude_list)
    geosep_list = exclude_non_numbers(geosep_list)
    numsats_list = exclude_non_numbers(numsats_list)
    fixqual_list = exclude_non_numbers(fixqual_list)
    pdop_list = exclude_non_numbers(pdop_list)
    hdop_list = exclude_non_numbers(hdop_list )
    vdop_list = exclude_non_numbers(vdop_list)
    rms_list = exclude_non_numbers(rms_list)
    siglat_list = exclude_non_numbers(siglat_list )
    siglong_list = exclude_non_numbers(siglong_list)
    sigalt_list = exclude_non_numbers(sigalt_list)
    trckd_sat_list = exclude_non_numbers(trckd_sat_list)
    
    # making mean values from 15sec measurement
    lat = (sum(lat_list) / len(lat_list) ) /100 # lat and long comes 100 times larger from nmea
    lon =  (sum(lon_list) / len(lon_list) ) /100
    altitude = sum(altitude_list) / len(altitude_list) 
    geosep = sum(geosep_list) / len(geosep_list) 
    numsats = sum(numsats_list) / len(numsats_list) 
    fixqual = sum(fixqual_list) / len(fixqual_list) 
    pdop = sum(pdop_list) / len(pdop_list) 
    hdop= sum(hdop_list) / len(hdop_list) 
    vdop= sum(vdop_list) / len(vdop_list) 
    rms= sum(rms_list) / len(rms_list) 
    siglat= sum(siglat_list) / len(siglat_list) 
    siglong = sum(siglong_list) / len(siglong_list) 
    sigalt = sum(sigalt_list) / len(sigalt_list) 
    meansatcout = sum(trckd_sat_list) / len(trckd_sat_list)
    # rounding values
    lat = round(lat,7)
    lon = round(lon,7)
    pdop = round(pdop,3)
    hdop = round(hdop,3)
    vdop = round(vdop,3)
    siglat = round(siglat,3)
    siglong = round(siglong,3)
    sigalt = round(sigalt,3)

    


    alt = altitude - geosep # elevation above geoid
 
        #DATABASE INPUT
        # all values are %s because query is parameterized
    main_table = ("INSERT INTO gnssegnosedas ""(time, reciever, lat, lon, fix_quality, tracked_sat_count, el_alt, pdop, hdop, vdop, visible_sat_count, rms, sig_lat, sig_long, sig_alt, is_egnos) ""VALUES (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s) ")
    main_tuple = (dateTime, reciever, lat, lon, fixqual, numsats, alt, pdop, hdop, vdop, meansatcout , rms, siglat, siglong, sigalt, egnos)
    cursor.execute(main_table, main_tuple)
    connection.commit()
    print("reciever:"+str(reciever)+" DATABASE INPUT SUCCESFUL - mean of " +str(len(lat_list))+ " values" ) #displaying number of values that comes into mean value
    lat_list =[]
    lon_list =[]
    altitude_list = []
    geosep_list = []
    numsats_list = []
    fixqual_list = []
    pdop_list = []
    hdop_list = []
    vdop_list = []
    rms_list = []
    siglat_list = [] 
    siglong_list = []
    sigalt_list = []
    trckd_sat_list = []
    
    egnos = 0
    tracked_count = 0
    now_time = time.time() #getting new time for loop condition


now_time = time.time()
main_write_time = now_time +15 # every 15 sec mean data to table gnssegnosedas
gsa_write_time = now_time + 3600
gsv_write_time = now_time + 60

TIMER_IN_SECS = int(sys.argv[1]) # time of measurement in seconds
end_time = now_time + TIMER_IN_SECS
# STARTS READING FROM SERIAL PORT (set right symbolic ports for your recievers!!)
with serial.Serial("/dev/downblack", 38400, timeout=1) as ser:
    while now_time < end_time:
        line = ser.readline()
        try: line = line.decode()
        except: print("undecodable")
        line = line[:-2]
        timestamp = math.floor(time.time()) # geting time, rounding to whole seconds
        dateTime = datetime.fromtimestamp(timestamp)
        # IF CONDITION THAT CHECKS NMEA MESSAGE THAT COMES TROUGH
        if len(line) < 6:  # short line skiped
            print(line , "--empty line")
        
        elif line[3] == "T":  # GNTXT - just info about reciever
            pass
        elif line[4] == "G":  # GGA
           
            
            if main_write_time <= timestamp:      # second gga ends line in database and starts new one
                endcycle()
                try :gga = pynmea2.parse(line)
                except: pass
            else:
               
                try :gga = pynmea2.parse(line)
                except: pass# appending values to lists to make mean value in endcycle function
            try: lat_list.append(gga.lat)
            except: print("no lat")
            try:lon_list.append(gga.lon)
            except: print("no lon")
            try: altitude_list.append(gga.altitude)
            except: print("no alt")
            try: geosep_list.append(float(gga.geo_sep))
            except: print("no geosep")
            try: numsats_list.append(int(gga.num_sats))
            except: print("no numsats")
            try: fixqual_list.append(gga.gps_qual)
            except: print("no qual")
        elif line[:6] == "$GNGSA":  # GSA
           # print(line)
            try :gsa = pynmea2.parse(line)
            except: pass
            if egnos == 0:  # no egnos yet
                if 33 < all(gsa.data[3:14]) < 52:  # check for egnos PRN nums , EGNOS PRN = 120-139, EGNOS NMEA ID = 33 - 52
                    egnos = 1  # egnos PRN is in gsa message
                else:
                    pass
                
            if gsa_write_time <= timestamp:
                gsa_write_time2 = datetime.fromtimestamp(math.floor(gsa_write_time) )
                gsa_write_time = gsa_write_time + 3600 #gsa only in 1 hour so we can check all recievers have same conditions
                gsa_table = ("INSERT INTO gnssegnosedasgsa ""(time,reciever,trackedID_1,trackedID_2,trackedID_3,trackedID_4,trackedID_5,trackedID_6,trackedID_7,trackedID_8,trackedID_9,trackedID_10,trackedID_11,trackedID_12) ""VALUES (%s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s, %s )")
                gsa_tuple = (gsa_write_time2 , reciever, gsa.data[2], gsa.data[3], gsa.data[4], gsa.data[5], gsa.data[6], gsa.data[7], gsa.data[8], gsa.data[9], gsa.data[10], gsa.data[11], gsa.data[12], gsa.data[13])
               
                gsa_tuple2 = ()
                for element in gsa_tuple[1:]: # converts everything else than int into int, except for datetime
                    if str(element).isdigit():
                        gsa_tuple2 += (int(element),)
                    else:
                        gsa_tuple2 += (0,)
                gsa_tuple = (gsa_tuple[0],) + gsa_tuple2
            
            
                cursor.execute(gsa_table, gsa_tuple)
                connection.commit()
            else: pass  
            try: pdop_list.append(float(gsa.data[14]))
            except: print("no pdop")
            try: hdop_list.append(float(gsa.data[15]))
            except: print("no hdop")
            try: vdop_list.append(float(gsa.data[16]))
            except: print("no vdop")
        elif line[5] == "V":  # GSV 
            # print(line)
            try: gsv = pynmea2.parse(line)
            except: pass
            if len(gsv.data) <= 4:  # empty message like : $GLGSV,1,1,00*65
                    pass            
            
            
            
            if int (gsv.data[0]) == int(gsv.data[1]):  # if last gsv of system = adds to total count of tracked sats, deleted in end function
                tracked_count = tracked_count + int(gsv.data[2])
                
                
                
            else:
                pass
            
            
            if egnos == 0:
                try: egnos_check()
                except: pass
            else: pass
            
            
            
            
            
            
            if   gsv_write_time <=timestamp:
                gsv_write_time2 = datetime.fromtimestamp(math.floor( gsv_write_time))
                gsv_write_time = gsv_write_time + 60
                # gsv only once per minute

                if len(gsv.data) == 7:
                    gsv_table = "INSERT INTO gnssegnosedasgsv ""(time, reciever, visible_ID, visible_AZ, visible_EL, visible_SNR) ""VALUES (%s, %s, %s, %s, %s, %s )"
                    gsv_tuple = (gsv_write_time2, reciever, gsv.data[3], gsv.data[4], gsv.data[5], gsv.data[6]) #creates database input
                    
                    gsv_tuple2 = () # converts everything else than int into int, except for datetime
                    for element in gsv_tuple[1:]:
                        if str(element).isdigit():
                            gsv_tuple2 += (int(element),)
                        else:
                            gsv_tuple2 += (0,)
                    gsv_tuple = (gsv_tuple[0],) + gsv_tuple2
                    
                    cursor.execute(gsv_table, gsv_tuple) # sends database input
                    connection.commit()

                elif len(gsv.data) == 11:
                    gsv_table = "INSERT INTO gnssegnosedasgsv ""(time, reciever, visible_ID, visible_AZ, visible_EL, visible_SNR) ""VALUES (%s, %s, %s, %s, %s, %s )"
                    gsv_tuple = (gsv_write_time2, reciever, gsv.data[3], gsv.data[4], gsv.data[5], gsv.data[6])
                    
                    gsv_tuple2 = ()
                    for element in gsv_tuple[1:]:
                        if str(element).isdigit():# converts everything else than int into int, except for datetime
                            gsv_tuple2 += (int(element),)
                        else:
                            gsv_tuple2 += (0,)
                    gsv_tuple = (gsv_tuple[0],) + gsv_tuple2
                    
                    cursor.execute(gsv_table, gsv_tuple)
                    connection.commit()

                    gsv_table = "INSERT INTO gnssegnosedasgsv ""(time, reciever, visible_ID, visible_AZ, visible_EL, visible_SNR) ""VALUES (%s, %s, %s, %s, %s, %s )"
                    gsv_tuple = (gsv_write_time2, reciever, gsv.data[7], gsv.data[8], gsv.data[9], gsv.data[10])
                    
                    gsv_tuple2 = ()
                    for element in gsv_tuple[1:]:
                        if str(element).isdigit(): # converts everything else than int into int, except for datetime
                            gsv_tuple2 += (int(element),)
                        else:
                            gsv_tuple2 += (0,)
                    gsv_tuple = (gsv_tuple[0],) + gsv_tuple2
                    
                    cursor.execute(gsv_table, gsv_tuple)
                    connection.commit()

                elif len(gsv.data) == 15:
                    gsv_table = "INSERT INTO gnssegnosedasgsv ""(time, reciever, visible_ID, visible_AZ, visible_EL, visible_SNR) ""VALUES (%s, %s, %s, %s, %s, %s )"
                    gsv_tuple = (gsv_write_time2, reciever, gsv.data[3], gsv.data[4], gsv.data[5], gsv.data[6])
                    
                    gsv_tuple2 = ()
                    for element in gsv_tuple[1:]: # converts everything else than int into int, except for datetime
                        if str(element).isdigit():
                            gsv_tuple2 += (int(element),)
                        else:
                            gsv_tuple2 += (0,)
                    gsv_tuple = (gsv_tuple[0],) + gsv_tuple2
                    
                    cursor.execute(gsv_table, gsv_tuple)
                    connection.commit()

                    gsv_table = "INSERT INTO gnssegnosedasgsv ""(time, reciever, visible_ID, visible_AZ, visible_EL, visible_SNR) ""VALUES (%s, %s, %s, %s, %s, %s )"
                    gsv_tuple = (gsv_write_time2, reciever, gsv.data[7], gsv.data[8], gsv.data[9], gsv.data[10])
                   
                    gsv_tuple2 = ()
                    for element in gsv_tuple[1:]: # converts everything else than int into int, except for datetime
                        if str(element).isdigit():
                            gsv_tuple2 += (int(element),)
                        else:
                            gsv_tuple2 += (0,)
                    gsv_tuple = (gsv_tuple[0],) + gsv_tuple2
                    
                    cursor.execute(gsv_table, gsv_tuple)
                    connection.commit()

                    gsv_table = "INSERT INTO gnssegnosedasgsv ""(time, reciever, visible_ID, visible_AZ, visible_EL, visible_SNR) ""VALUES (%s, %s, %s, %s, %s, %s )"
                    gsv_tuple = (gsv_write_time2, reciever, gsv.data[11], gsv.data[12], gsv.data[13], gsv.data[14])
                    
                    gsv_tuple2 = () # converts everything else than int into int, except for datetime
                    for element in gsv_tuple[1:]:
                        if str(element).isdigit():
                            gsv_tuple2 += (int(element),)
                        else:
                            gsv_tuple2 += (0,)
                    gsv_tuple = (gsv_tuple[0],) + gsv_tuple2
                    
                    cursor.execute(gsv_table, gsv_tuple)
                    connection.commit()

                elif len(gsv.data) == 19:
                    gsv_table = "INSERT INTO gnssegnosedasgsv ""(time, reciever, visible_ID, visible_AZ, visible_EL, visible_SNR) ""VALUES (%s, %s, %s, %s, %s, %s )"
                    gsv_tuple = (gsv_write_time2, reciever, gsv.data[3], gsv.data[4], gsv.data[5], gsv.data[6])
                    
                    gsv_tuple2 = () # converts everything else than int into int, except for datetime
                    for element in gsv_tuple[1:]:
                        if str(element).isdigit():
                            gsv_tuple2 += (int(element),)
                        else:
                            gsv_tuple2 += (0,)
                    gsv_tuple = (gsv_tuple[0],) + gsv_tuple2
                    
                    cursor.execute(gsv_table, gsv_tuple)
                    connection.commit()

                    gsv_table = "INSERT INTO gnssegnosedasgsv ""(time, reciever, visible_ID, visible_AZ, visible_EL, visible_SNR) ""VALUES (%s, %s, %s, %s, %s, %s )"
                    gsv_tuple = (gsv_write_time2, reciever, gsv.data[7], gsv.data[8], gsv.data[9], gsv.data[10])
                    
                    gsv_tuple2 = ()
                    for element in gsv_tuple[1:]: # converts everything else than int into int, except for datetime
                        if str(element).isdigit():
                            gsv_tuple2 += (int(element),)
                        else:
                            gsv_tuple2 += (0,)
                    gsv_tuple = (gsv_tuple[0],) + gsv_tuple2
                    
                    cursor.execute(gsv_table, gsv_tuple)
                    connection.commit()

                    gsv_table = "INSERT INTO gnssegnosedasgsv ""(time, reciever, visible_ID, visible_AZ, visible_EL, visible_SNR) ""VALUES (%s, %s, %s, %s, %s, %s )"
                    gsv_tuple = (gsv_write_time2, reciever, gsv.data[11], gsv.data[12], gsv.data[13], gsv.data[14])
                    
                    gsv_tuple2 = ()
                    for element in gsv_tuple[1:]:
                        if str(element).isdigit(): # converts everything else than int into int, except for datetime
                            gsv_tuple2 += (int(element),)
                        else:
                            gsv_tuple2 += (0,)
                    gsv_tuple = (gsv_tuple[0],) + gsv_tuple2
                    
                    cursor.execute(gsv_table, gsv_tuple)
                    connection.commit()

                    gsv_table = "INSERT INTO gnssegnosedasgsv ""(time, reciever, visible_ID, visible_AZ, visible_EL, visible_SNR) ""VALUES (%s, %s, %s, %s, %s, %s )"
                    gsv_tuple = (gsv_write_time2, reciever, gsv.data[15], gsv.data[16], gsv.data[17], gsv.data[18])
                    
                    gsv_tuple2 = ()
                    for element in gsv_tuple[1:]: # converts everything else than int into int, except for datetime
                        if str(element).isdigit():
                            gsv_tuple2 += (int(element),) 
                        else:
                            gsv_tuple2 += (0,)
                    gsv_tuple = (gsv_tuple[0],) + gsv_tuple2
                    
                    cursor.execute(gsv_table, gsv_tuple)
                    connection.commit()
                else:
                    print("____________________GSV MESSAGE ERROR____________________________")
                    # if gsv message is len= 19 then it tracks 4 satelites per line (len15 = 3 satelites, len11 = 2, len7 =1)
                    # one satelite has one line in database
            else: pass

        elif line[5] == "T":  # GST
            # print(line)
            try: gst = pynmea2.parse(line)
            except: pass
            
            try: trckd_sat_list.append(tracked_count)
            except: print("no tracked_sats")#adding sum of sats every second from gsv
            tracked_count = 0  # tracked sum = 0  for next second
            
            if float(gst.data[1]) < 100: # If RMS value is higher than 100, sets it to 100, so 1 peak value does not effect the mean value
                 rms_list.append(int(round(float(gst.data[1])))) # that can happen when multipath
            else:
                 print("HIGH RMS -- POSSIBLE MULTIPATH reciver:" + str(reciever))
                 rms_list.append(100)
            
            try: siglat_list.append(float(gst.data[5])) #appendig values to list for mean value
            except: print("no siglat")
            try: siglong_list.append(float(gst.data[6]))
            except: print("no siglong")
            try: sigalt_list.append(float(gst.data[7]))
            except: print("no siglat")
        else:
            print("unknown message!! -- ")
            try: print(line)
            except: pass

cursor.close()
connection.close()
print("--------------------------")
print("MySQL connection is closed")

