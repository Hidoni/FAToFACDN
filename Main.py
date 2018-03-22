import subprocess

while True:
    script = subprocess.Popen(['python', 'FAToFACDN.py']).wait()  # Run This Code until something breaks.
    print("Got error code {0}, restarting....".format(script))
