Getting Started
===============

**Requirements:** Python 3

Create a Thing
**************

To interact with Bucket, the first step is to visit `Bucket <https://dwd.tudelft.nl/bucket>`_ to create an account and a Thing.

During this process you will get the ID of your Thing (starting with `dcd:things:...`) and you will generate a public/private key.

These 2 pieces of information are needed for your Python code to interact with Bucket.

Setup a Python project
**********************

Create a folder for your project and open it with VisualStudio Code.

To avoid disturbing other Python setup on your machine, we setup a virtual environment with `virtualenv`.
To create a virtual environment called `venv`, open the terminal (VisualStudio Code, directly in your project)
and execute the following command:

.. code-block:: console

    virtualenv venv

Then we activate this environment with source:

.. code-block:: console

    source venv/bin/activate

If it worked properly, you should see `(venv)` appearing on the left side of the line in the Terminal.

We can now install the DCD SDK library

.. code-block:: console

    pip install dcd-sdk

At this stage you can be prompted to update your pip module, you can do so with:

.. code-block:: console

    pip install --upgrade pip


Your Python setup is now ready.

Basic example
*************

In this example, we will create a property Accelerometer generating random values. It shows how to establish a connection with 
Bucket using your Thing id and your private key. This is a typical case for a Python code running on a device to collect data. 

In the file explorer (left-side panel), create a new file `example.py` and add the following lines.

.. code-block:: python
   :linenos:

    # Import Thing from the Data-Centric Design 
    from dcd.bucket.thing import Thing

    # Create an instance of Thing
    # (Replace with your thing id and the path to your private key)
    my_thing = Thing(thing_id="dcd:things:7f7fe4c6-45e9-42d2-86e2-a6794e386108",
                    private_key_path="/path/to/private.pem")


You can run this example in the terminal:

.. code-block:: console

    python example.py


To stop the program, press `CTRL+C`.

Once the connection is established with your Thing, we can get an overview of
this Thing by printing the output of the method to_json(). Add the following
line at the bottom of the file and run the program again. If you just registered
your Thing on Bucket, it has only an id, a name and a type.

.. code-block:: python

    print(my_thing.to_json())

Let's create a property 'My Python accelerometer'. The method find_or_create()
looks for an existing property with this name. If none is found, it creates a
new on with the type 'ACCELEROMETER' 

.. code-block:: python

    my_property = my_thing.find_or_create_property(
        "My Python Accelerometer", "ACCELEROMETER")

Let's have a look at the property, it should contain the name and a unique id.
The type also contains the dimensions, 3 in the case of an accelerometer.

.. code-block:: python

    print(my_property.to_json())

We are ready to send data. In the code below we create a function that generates
an array with 3 random values and add them to the property. We then make an infinite
loop (while True) to send these random values every 2 seconds.

To generate random numbers we need the library `random` and to wait 2 seconds
we need the library `time`. These are part of Python, we just import them at
the top of the file.

.. code-block:: python

    from random import random
    import time


Then, we can write our function at the bottom of the file.

.. code-block:: python
   :linenos:

    # Let's create a function that generate random values
    def generate_dum_property_values(the_property):
        # Define a tuple with the current time, and 3 random values
        values = (random(), random(), random())
        # Update the values of the property
        the_property.update_values(values)

    # Finally, we call our function to start generating dum values
    while True:
        generate_dum_property_values(my_property)
        # Have a 2-second break
        time.sleep(2)

Environment Variables
*********************

To avoid credentials in your code, the DCD Python Kit is looking for your thing id and private key
from the environment variables. To set these variables, create a file `.env` and add the following lines
(replace the thing id and the path by yours).

.. code-block:: console

    THING_ID=dcd:things:7f7fe4c6-45e9-42d2-86e2-a6794e386108
    PRIVATE_KEY_PATH=/path/to/private.pem


The full example can be found `Here <https://github.com/datacentricdesign/dcd-sdk-python/blob/master/dcd/examples.py>`_