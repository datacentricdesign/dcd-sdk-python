# This example shows how to fetch data from a shared property.
import sys

from dcd.bucket.thing import Thing

def main():
    # Instantiate a thing with its credential
    # By default, looking into .env for THING_ID and PRIVATE_KEY_PATH (default "./private.pem")
    my_thing = Thing()

    # If we fail to connect to the Thing, we leave the program
    if not my_thing.http.is_connected:
        sys.exit()

    group = "dcd:groups:my-group"

    # Fetch shared properties
    shared_properties = my_thing.find_shared_properties(group)

    print(shared_properties)
    
    # UNIX timestamp in millisecond also works (and is used for the API).
    # This is just more convenient here use the date
    from_ts = "2021-12-15 00:00:00"
    to_ts = "2021-12-15 00:00:00"

    # Try to read the first shared property found
    shared_properties[0].read(from_ts,to_ts,time_interval=None,time_fct=None,shared_with=group)

if __name__ == "__main__":
    main()