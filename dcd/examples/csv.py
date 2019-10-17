import datetime
import time
from random import random

file = open("my-property.csv", "a")

def write_in_csv(values):
    file.write(','.join(values))
    file.write('\n')

try:
    # Finally, we call our function to start generating dum values
    while True:
        current_time = int(datetime.datetime.utcnow().timestamp()*1000)
        print(current_time)
        values = (current_time, str(random()), str(random()), str(random()))
        write_in_csv(values)
        # Have a 2-second break
        time.sleep(1)

except Exception:
    print("hello")
    file.close()

