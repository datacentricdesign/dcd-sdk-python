Environment Variables
=====================

There are settings you can provision through environment variables,
provisioning them via a file .env at the root of your project. 

Here is the full list with there default value.

.. code-block:: console

    # The id of your thing, instead of having to change your code
    THING_ID=

    # The path to your public and private keys if they are not
    # in the root folder of your project
    PRIVATE_KEY_PATH=private.pem
    PUBLIC_KEY_PATH=public.pem

    # The path to the folder where to store logs
    LOG_PATH=./logs/
    # The level of logs to generate (ERROR, WARN, INFO,DEBUG)
    LOG_LEVEL=DEBUG
    # The path to the folder where to store data. Data is stored
    # per Thing folders and Property files
    DATA_PATH=./data/

    # The URI to Bucket, when targeting a different version or
    # an instance running on a different server
    HTTP_API_URI=https://dwd.tudelft.nl:443/bucket/api

    # The MQTT host, port and security (mqtt or mqtts) to target
    # a different version or an instance running on a different server
    MQTT_HOST=dwd.tudelft.nl
    MQTT_PORT=8883
    MQTT_SECURED=True