# [DCD SDK Python](https://datacentricdesign.org/tools/sdk-python/)

Python SDK for the tools of the Data-Centric Design Lab

![version](https://img.shields.io/badge/version-0.1.3-blue.svg)
![license](https://img.shields.io/badge/license-MIT-blue.svg)
[![GitHub issues open](https://img.shields.io/github/issues/datacentricdesign/dcd-sdk-python.svg?maxAge=2592000)]()
[![GitHub issues closed](https://img.shields.io/github/issues-closed-raw/datacentricdesign/dcd-sdk-python.svg?maxAge=2592000)]()

[SDK page](https://datacentricdesign.org/tools/sdk-python/)


# Getting Started

**Requirements:** Python 3

## Create a Thing

To interact with bucket, the first step is to visit [Bucket](https://dwd.tudelft.nl/bucket) to create an account and a Thing.

During this process you will get the ID of your Thing (starting with dcd:things:...) and you will generate a public/private key.

These 2 pieces of information are needed for your Python code to interact with Bucket.

## Setup s Python project

Create a folder for your project and open it with VisualStudio Code.

To avoid distubing other Python setup on your machine, we setup a virtual environment with virtualenv.
To create a virtualenvironment called 'venv', open the terminal (VisualStudio Code, directly in your project)
and execute the following command:

```sh
virtualenv venv
```

Then we activate this environment with source:

```sh
source venv/bin/activate
```

If it worked properly, you should see (venv) appearing on the left side of the line in terminal.

We can now install the DCD SDK library

```sh
pip install dcd-sdk
```

At this stage you can be prompted to update your pip module, you can do so with:

```sh
pip install --upgrade pip
```

Your Python setup is now ready.

## Basic example

In this example we will create a property Accelerometer generating random values. It shows how to establish a connection with 
Bucket using your Thing id and your private key. This is a typical case for a Python code running on a device to collect data. 

In the file explorer (left-side panel), create a new file 'example.py' and add the following lines.

```python
# Import Thing from the Data-Centric Design 
from dcd.entities.thing import Thing

# Create an instance of Thing
# (Replace with your thing id and the path to your private key)
my_thing = Thing(thing_id='dcd:things:7f7fe4c6-45e9-42d2-86e2-a6794e386108',
                 private_key_path='/Users/jbourgeois/Desktop/private.pem')
```

You can run this example in the terminal:

```sh
python example.py
```

To stop the programme, press CTRL+C.

Once the connection is established with your Thing, we can get an overview of
this Thing by printing the output of the method to_json(). Add the following
line at the bottom of the file and run the programme again. If you just registered
your Thing on Bucket, it has only an id, a name and a type.

```python
print(my_thing.to_json())
```

Let's create a property 'My Python accelerometer'. The method find_or_create()
looks for an existing property with this name. If none is found, it creates a
new on with the type 'ACCELEROMETER' 

```python
my_property = my_thing.find_or_create_property(
    "My Python Accelerometer", 'ACCELEROMETER')
```

Let's have a look at the property, it should contain the name and a unique id.
The type also contains the dimensions, 3 in the case of an accelerometer.

```python
print(my_property.to_json())
```

We are ready to send data. In the code below we create a function that generates
an array with 3 random values and add them to the property. We then make an infinite
loop (while True) to send these random values every 2 seconds.

To generate random numbers we need the library 'random' and to wait 2 seconds
we need the library 'time'. These are part of Python, we just import them at
the top of the file.

```python
from random import random
import time
```

Then, we can write our function at thebottomof the file.

```python
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
```

The full example can be found [here](https://github.com/datacentricdesign/dcd-sdk-python/blob/master/dcd/examples/thing_example.py)

# Thing

* Thing()

Instantiate a connection to Bucket for a Thing

  * thing_id (required), the id of the Thing to connect
  * private_key_path (optional), the path to the private key. If no path is provided, it looks for the file 'private.pem' in the current folder.

* thing.read()

Fetch the Thing details from Bucket. This method is automatically called Thing() connection succeed.

* thing.to_json()

Format all Thing details as a JSON object.

* thing.find_property_by_name()

  * property_name_to_find (required) the name of the property we are looking for

* thing.create_property()

  * name (required)
  * typeId (required)

* thing.update_property()
  * prop (required)
  * file_name (optional)


* thing.read_property()
  * property_id (required)
  * from_ts (optional)
  * to_ts (optional)

* thing.find_or_create_property()
  * property_name (required)
  * typeId (required)

## Developers

To publish a new version of the SDK:

python3 setup.py sdist bdist_wheel
python3 -m twine upload dist/dcd-sdk-0.0.5.tar.gz


# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
