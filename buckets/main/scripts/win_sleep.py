import ctypes
import os
import sys
import subprocess
import time
try:
 is_admin = os.getuid() == 0
except AttributeError:
 is_admin = ctypes.windll.shell32.IsUserAnAdmin() != 0

if not is_admin:
    print("ERROR: This script must be run with administrative privileges.")
    sys.exit(1)
    
def put_computer_to_sleep(seconds):
    print("The computer is getting ready to go to sleep...")
    time.sleep(seconds)
    subprocess.run('rundll32.exe powrprof.dll,SetSuspendState 0,1,0', shell=True)
    print("The computer has just woken up.")

def get_user_defined_time():
    while True:
        try:
            user_time = int(input("Enter the time in minutes and press <Enter>: "))
            if user_time >= 1:
                return user_time * 60
            else:
                print("ERROR: You MUST enter the number of minutes.")
        except ValueError:
            print("Invalid input. Please enter a number.")

def main():
    sleep_options = {
        1: 900,
        2: 1800,
        3: 2700,
        4: 3600,
        5: 4500,
        6: 5400,
        7: 6300,
        8: 7200,
    }

    while True:
        print("\nOptions:")
        print("[1] 15 minutes\n[2] 30 minutes\n[3] 45 minutes\n[4] 60 minutes")
        print("[5] 75 minutes\n[6] 90 minutes\n[7] 105 minutes\n[8] 120 minutes")
        print("[9] User Defined\n[0] Exit")

        choice = input("Enter an option number: ")
        if choice.isdigit():
            choice = int(choice)
            if choice == 0:
                sys.exit(0)
            elif choice == 9:
                seconds = get_user_defined_time()
            elif choice in sleep_options:
                seconds = sleep_options[choice]
            else:
                print("Invalid choice. Please try again.")
                continue

            put_computer_to_sleep(seconds)
        else:
            print("Invalid input. Please enter a number.")

main()