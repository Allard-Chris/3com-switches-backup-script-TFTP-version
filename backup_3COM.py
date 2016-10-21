#!/usr/bin/python
#--------------------------------------------------------------------------------------------------
#
#     Nom : backup_3COM.py
#  Auteur : Allard Chris
#    Date : 21/10/2016
# Version : 1.0
#  Github : https://github.com/Allard-Chris/3COM-switches-backup-script-TFTP-version
#
# This script connect to a list of 3com & HP switches for initiating a backup command to a TFTP server.
# It use Telnet protocol and the login should be the same all on switches that the script will go.
# It require an TFTP server where the backups will be saved.
#
#--------------------------------------------------------------------------------------------------

# Import library
import getpass
import re
import signal
import socket
import sys
import telnetlib
import time

# Function to stop the program
def close_program(signal, frame):
        print("End of script")
        sys.exit(0)

# Function checking IP address syntax
def is_valid_ip(ip):
        result = re.match(r"^(\d{1,3}\.){3}\d{1,3}$", ip)
        return bool(result)

# Call function when system want to stop (command ctrl+c)
signal.signal(signal.SIGINT, close_program)

# VARIABLE SET
tftp_server = "192.168.1.10" # tftp server where will be sent backups
timeout = 180 # Waiting time before considering that there is a timeout (in seconds)
log_file = "log.txt" # Name of output file
hosts_file = "hosts.txt" # Name of input file where they are IP address of switches
telnet_port = 23 # Default telnet port

# Account Parameters
user = raw_input("Enter your remote account: ") # Variable for user account
password = getpass.getpass() # Variable for password account

# Other Variable
successful = 0
failure = 0

# Create an output file for the results
log = open(log_file, "w") # Open or create the file in writing mode

# Load input file
try :
        input_file = open(hosts_file, "r") # Open file in read mode
        hosts = input_file.readlines()
        input_file.close()
except IOError:
        print "Error opening file"
        sys.exit(0)

# Loop on all lines in input file
for switches in hosts:
        switch = switches.split(":")
        try:
                model = switch[0] # Get switch model
                host_name = switch[1] # Get name of the switch in hosts file
                ip_address = switch[2][:len(switch[2]) - 1] # Delete carriage return line feed
        except IndexError:
                ip_address = 'null'
        # Obvious...
        if is_valid_ip(ip_address) and ((model=="1") or (model=="2") or (model=="3")) :
                try :
                        telnet = telnetlib.Telnet(ip_address,telnet_port,timeout) # Open terminal socket to host

                        print time.strftime('%d/%m/%y %H:%M:%S',time.localtime()) + " Running on : " + ip_address # For user information

                        #################
                        # FOR 3COM 4400 #
                        # MODEL : 1     #
                        #################
                        if model == "1":
                                # CONNECTION
                                telnet.read_until("Login:",timeout)
                                telnet.write(user + "\r")
                                telnet.write(password + "\r")
                                telnet.write("\r")

                                # GOING TO SAVE BACKUP MENU
                                telnet.read_until("Select menu option:",timeout)
                                telnet.write("system\r")
                                telnet.read_until("Select menu option (system):",timeout)
                                telnet.write("backupConfig\r")
                                telnet.read_until("Select menu option (system/backupConfig):",timeout)
                                telnet.write("save\r")

                                # CONFIG FOR TFTP BACKUP
                                telnet.read_until("Enter TFTP server IP address",timeout)
                                telnet.write(tftp_server + "\r")
                                telnet.read_until("Enter File Name",timeout)
                                telnet.write(ip_address + "-" + host_name + ".cfg"  + "\r")
                                telnet.read_until("Enter User notes:",timeout)
                                telnet.write("\r")
                                
                                # TRY TO KNOW IF BACKUP IS CORRECTLY DONE AFTER TIMEOUT
                                try:
                                        result = telnet.read_until("Save of system configuration successful.",timeout)
                                except EOFError as e:
                                        print "Timeout"
                                
                                if "Save of system configuration successful." in result:
                                        # Write for log file
                                        log.write(time.strftime('%d/%m/%y %H:%M:%S',time.localtime()) + " " + ip_address + " " + host_name + " : Successful" + "\n")
                                        print time.strftime('%d/%m/%y %H:%M:%S',time.localtime()) + " Successful" # For user information
                                        successful += 1
                                else:
                                        log.write(time.strftime('%d/%m/%y %H:%M:%S',time.localtime()) + " " + ip_address + " Failure - Bad Response Maybe Timeout" + "\n")
                                        print time.strftime('%d/%m/%y %H:%M:%S',time.localtime()) + " Failure on : " + ip_address + " Bad Response Maybe Timeout" # For user information
                                        failure += 1

                                telnet.write("logout\r")

                        #################
                        # FOR 3COM 4500 #
                        # MODEL : 2     #
                        #################
                        if model == "2":
                                # CONNECTION
                                telnet.read_until("Username:",timeout)
                                telnet.write(user + "\r")
                                telnet.write(password + "\r")
                                telnet.write("\r")

                                # GOING TO SAVE BACKUP
                                telnet.write("backup fabric current-configuration to " + tftp_server + " " + ip_address + "-" + host_name + ".cfg" + "\r")
                                                       
                                # TRY TO KNOW IF BACKUP IS CORRECTLY DONE AFTER TIMEOUT
                                try:
                                        result = telnet.read_until("File uploaded successfully.",timeout)
                                except EOFError as e:
                                        print "Timeout"
                                
                                if "File uploaded successfully." in result:
                                        # Write for log file
                                        log.write(time.strftime('%d/%m/%y %H:%M:%S',time.localtime()) + " " + ip_address + " " + host_name + " : Successful" + "\n")
                                        print time.strftime('%d/%m/%y %H:%M:%S',time.localtime()) + " Successful" # For user information
                                        successful += 1
                                else:
                                        log.write(time.strftime('%d/%m/%y %H:%M:%S',time.localtime()) + " " + ip_address + " Failure - Bad Response Maybe Timeout" + "\n")
                                        print time.strftime('%d/%m/%y %H:%M:%S',time.localtime()) + " Failure on : " + ip_address + " Bad Response Maybe Timeout" # For user information
                                        failure += 1
                                
                                telnet.write("\r")
                                telnet.write("quit\r")

                        ################
                        # FOR HP A5500 #
                        # MODEL : 3    #
                        ################
                        if model == "3":
                                # CONNECTION
                                telnet.read_until("Username:",timeout)
                                telnet.write(user + "\r")
                                telnet.write(password + "\r")
                                telnet.write("\r")

                                # GOING TO SAVE BACKUP
                                telnet.write("backup startup-configuration to " + tftp_server + " " + ip_address + "-" + host_name + ".cfg" + "\r")
                                
                                # TRY TO KNOW IF BACKUP IS CORRECTLY DONE AFTER TIMEOUT
                                try:
                                        result = telnet.read_until("finished!",timeout)
                                except EOFError as e:
                                        print "Timeout"
                                
                                if "finished!" in result:
                                        # Write for log file
                                        log.write(time.strftime('%d/%m/%y %H:%M:%S',time.localtime()) + " " + ip_address + " " + host_name + " : Successful" + "\n")
                                        print time.strftime('%d/%m/%y %H:%M:%S',time.localtime()) + " Successful" # For user information
                                        successful += 1
                                else:
                                        log.write(time.strftime('%d/%m/%y %H:%M:%S',time.localtime()) + " " + ip_address + " Failure - Bad Response Maybe Timeout" + "\n")
                                        print time.strftime('%d/%m/%y %H:%M:%S',time.localtime()) + " Failure on : " + ip_address + " Bad Response Maybe Timeout" # For user information
                                        failure += 1

                                telnet.write("\r")
                                telnet.write("quit\r")

                except socket.error, error:
                        log.write(time.strftime('%d/%m/%y %H:%M:%S',time.localtime()) + " " + ip_address + " Failure - " + str(error) + "\n")
                        print time.strftime('%d/%m/%y %H:%M:%S',time.localtime()) + " Failure on : " + ip_address # For user information
                        failure += 1

# End of script
print "End of script"
log.write("\n")
log.write(time.strftime('%d/%m/%y %H:%M:%S',time.localtime()) + " : End of script" + "\n")
log.write("Number of Failures : " + str(failure) + "\n")
log.write("Number of Successful : " + str(successful) + "\n")
sys.exit(0)
