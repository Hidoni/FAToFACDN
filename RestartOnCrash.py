# Since I'm running this on windows, this is the easiest way to have it restart the program upon a crash.
import subprocess

while True:
    script = subprocess.Popen(['python', 'FAToFACDNv2.py']).wait() # Run This Code until something breaks.

    if script != 0: # If the exit code isn't 0, which will be 100% of the time with this bot
        print("Got error code " + str(script) + "...\nRestarting script...")
        continue
    else:
        break
