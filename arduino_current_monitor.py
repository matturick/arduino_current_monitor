#!/usr/bin/python
import serial
import syslog
import time
import datetime
import common
import signal
import sys
import os


# START: Global settings
log_file_relative_path = 'arduino_log.txt'
heartbeat_file_relative_path = 'arduino_heartbeat.txt'
kill_file_relative_path = 'kill'    # If a file is found here, the script gracefully exits
threshold_current_amps = 3          # threshold current in amps
consecutive_hot_reads_required = 3  # Number of consecutive "hot" (above threshold) reads to wait before writing to log
timeout_between_activations = 30    # minimum timeout until recording another activation (seconds)
timeout_between_log_entries = 600   # seconds between routine log (AKA "heartbeat") entries
wait_time_seconds = 0.1             # time to wait between serial port interactions (seconds)
port = '/dev/ttyACM0'   # for serial over GPIO
baudrate = 9600         # standard baud rate
# END: Global settings


#convert file paths to absolute paths
my_path = os.path.abspath(os.path.dirname(__file__))
log_file = os.path.join(my_path, log_file_relative_path)
heartbeat_file = os.path.join(my_path, heartbeat_file_relative_path)
kill_file = os.path.join(my_path, kill_file_relative_path)

def signal_handler(sig, frame):
    common.print_and_log("Script terminated by CTRL+C", log_file)
    exit(0)
def kill_file_found():
    os.remove(kill_file)
    common.print_and_log("Script killed by user", log_file)
    exit(0)

def main():
    signal.signal(signal.SIGINT, signal_handler)   

    # START Try to open the serial port
    common.print_and_log("Monitor starting...", log_file)
    try:
        ser = serial.Serial(port,baudrate)
    except Exception, e:
        common.print_and_log('The serial port could not be opened. Exception follows:', log_file)
        common.print_and_log(str(e), log_file)
        exit(0)
    print ser.readline()
    # END: Try to open the serial port

    # Main loop
    terminate = False
    last_hot_measurement_datetime = None    
    last_log_recorded_datetime = None
    number_of_consecutive_hot_reads = 0
    activation_timeout = False      # True if timeout_between_activations hasn't lapsed

    while not terminate:
        if(os.path.exists(kill_file)):
            kill_file_found()
        file_to_write = log_file
        log_this = False
        time.sleep(wait_time_seconds)   

        # Ask for the measurement & parse it
        try: 
            ser.write('i') # Sending character 'i' asks for current
            time.sleep(wait_time_seconds)
            result = ser.readline().replace('\n','').replace('\r','')
            result_list = result.split(' ')
        except Exception, e:
            common.print_and_log('The serial port could not be opened. Exception follows:',log_file)
            common.print_and_log(str(e),log_file)
            common.print_and_log("Closing...",log_file)
            exit(0)
        if(len(result_list) < 2):
            common.print_and_log("Bad measurement obtained: " + result)
            continue
        
        # Format for output
        output_line = datetime.datetime.now().strftime(common.standard_strftime_format) + ", Apparent Power: " + result_list[0] + "VA, RMS Current: " + result_list[1] + "A"
        try: 
            current = float(result_list[1])
        except:
            common.print_and_log("Bad measurement obtained: " + result)
            continue 

        # Check if we are in 'activation timeout'
        if not last_hot_measurement_datetime: # Will hit this if we haven't had any 'hot' measurement yet
            activation_timeout = False 
        else:
            hot_measurement_expiration = last_hot_measurement_datetime + datetime.timedelta(seconds = timeout_between_activations)
            if datetime.datetime.now() > hot_measurement_expiration:
                activation_timeout = False
        
        if activation_timeout is True:
            output_line = output_line + " - (TO)"

        # Evaluate current level
        # Check if we exceed current threshold
        # If you exceed and are not in timeout, count as a "hot" read
        if(activation_timeout is False and current > threshold_current_amps):
            number_of_consecutive_hot_reads = number_of_consecutive_hot_reads + 1
            if number_of_consecutive_hot_reads >= consecutive_hot_reads_required:
                # after so many consecutive hot reads, record message and set timer
                last_hot_measurement_datetime = datetime.datetime.now()
                activation_timeout = True
                log_this = True
                output_line = output_line + " - CURRENT DETECTED"
            else:
                output_line = output_line + " - CURRENT..."            
        else:
            number_of_consecutive_hot_reads = 0
        
        # If the logging interval expired, log the current to the "heartbeat" file
        if last_log_recorded_datetime is None:
            log_this = True
            output_line = output_line + " (routine log)"
            file_to_write = heartbeat_file
        else:
            log_expiration = last_log_recorded_datetime + datetime.timedelta(seconds = timeout_between_log_entries)
            if datetime.datetime.now() > log_expiration:
                log_this = True
                file_to_write = heartbeat_file
                output_line = output_line + " (routine log)"

        # Send output
        if log_this:
            common.print_and_log(output_line, file_to_write)
            last_log_recorded_datetime = datetime.datetime.now()
        else:
            common.print_and_log(output_line)

if __name__ == '__main__':
    main()

