import os
import sys
import datetime
import math
import common

def timedelta_to_string(input_timedelta):
    delta_minutes = (input_timedelta).seconds / 60
    delta_days = (input_timedelta).days # need days also, because seconds rolls over after 1 day
    delta_minutes = delta_minutes + (1440*delta_days) 
    if delta_days > 0:
        days_string = " [" + str(delta_days) + " day"
        if delta_days > 1:
            days_string += "s]"
        else:
            days_string += "]"
    else:
        days_string = ""
    result_string = str(int(math.floor(delta_minutes))) + " minutes" + days_string
    return result_string

def get_stats(log_file, heartbeat_file):
    # check if files exist, read log file into a list 
    if(not os.path.exists(log_file)):
        print("Log file " + log_file + " doesn't exist!")
        sys.exit(0)
    with open(log_file, "r") as file: 
        input_lines = file.read().splitlines()
    if(not os.path.exists(heartbeat_file)):
        print("Heartbeat file " + heartbeat_file + " doesn't exist!")
        sys.exit(0)
    with open(heartbeat_file, "r") as file: 
        hb_input_lines = file.read().splitlines()
    
    # Pull list of heartbeat entries from HB file 
    list_of_hb_log_entries = []
    key_phrase = "log"
    for l in hb_input_lines:
        if(key_phrase in l):
            list_of_hb_log_entries.append(l)
    if(len(list_of_hb_log_entries) == 0):
        print("No heartbeat entries found in file " + heartbeat_file)  
        sys.exit(0)   
    # Find latest HB log entry
    i = len(list_of_hb_log_entries) - 1
    while i > 0:
        l = list_of_hb_log_entries[i]
        try:
            timestamp_hb = datetime.datetime.strptime(l.split(',')[0], common.standard_strftime_format)
            print "Last HB: " + str(timestamp_hb)
            break
        except:
            pass

    # Pull list of activations from log file 
    list_of_log_entries = []
    key_phrase = "CURRENT DETECTED"
    for l in input_lines:
        if(key_phrase in l):
            list_of_log_entries.append(l)
    if(len(list_of_log_entries) == 0):
        print("No log entries found in file " + log_file)  
        sys.exit(0)       
    
    # Convert found entries into timestamps 
    list_of_timestamps = [ ]
    for l in list_of_log_entries:
        try:
            timestamp = datetime.datetime.strptime(l.split(',')[0], common.standard_strftime_format)
            list_of_timestamps.append(timestamp)
        except:
            pass
    print(str(len(list_of_timestamps)) + " entries found ")

    # Evaluate list of timestamps
    now = datetime.datetime.now()
    last_24_hours = 0
    last_7_days = 0
    last_n = 5      # Output average of last n measurements
    last_n_average = datetime.timedelta(0)
    q = 0
    for i, t in enumerate(list_of_timestamps):
        # Count last 7 days/last 24 hours activations
        delta_now = now - t
        if(delta_now < datetime.timedelta(days = 7)):
            last_7_days = last_7_days + 1
        if(delta_now < datetime.timedelta(days = 1)):
            last_24_hours = last_24_hours + 1
        delta_minutes = 0
        delta_days = 0
        days_string = ""
        # Count + print time between activations
        if i > 0:
            timedelta = list_of_timestamps[i] - list_of_timestamps[i-1]
            timedelta_string = timedelta_to_string(timedelta)
        else:
            timedelta = 0
            timedelta_string = ""
        print(datetime.datetime.strftime(t, common.standard_strftime_format) + ", " + timedelta_string)
        if( len(list_of_timestamps) - i - 1 < last_n):
            last_n_average += timedelta
            q = q + 1

    print(" ")
    if(len(list_of_timestamps) >= last_n):
        last_n_average = last_n_average / last_n
        print("Last 5 Average: " + timedelta_to_string(last_n_average))
    print("Last 24 hours:  " + str(last_24_hours)  + " activations")
    print("Last 7 days:    " + str(last_7_days) + " activations")
    last_activated_timestamp = str(datetime.datetime.strftime(list_of_timestamps[len(list_of_timestamps) - 1], common.standard_strftime_format))    
    print("Last activated: " + last_activated_timestamp + ", " + timedelta_to_string(delta_now))
    delta_hb = now - timestamp_hb
    print "Last HB:        " + str(datetime.datetime.strftime(timestamp_hb, common.standard_strftime_format))
    print("")



if __name__ == '__main__':
    if(len(sys.argv) != 3):
        print("")
        print("Usage:")
        print("python current_stats.py [LOG_FILE_PATH] [HEARTBEAT_FILE_PATH]")
        print("python current_stats.py current_monitor/arduino_log.txt current_monitor/arduino_heartbeat.txt")
        print("")
        sys.exit(1)
    print str(sys.argv[1])
    print str(sys.argv[2])
    get_stats(sys.argv[1], sys.argv[2])
