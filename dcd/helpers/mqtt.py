import requests
import logging

def mqtt_result_code(rc):
    switcher = {
        0: "MQTT connection successful",
        1: "MQTT Connection refused - incorrect protocol version",
        2: "MQTT Connection refused - invalid client identifier",
        3: "MQTT Connection refused - server unavailable",
        4: "MQTT Connection refused - bad username or password",
        5: "MQTT Connection refused - not authorised"
    }
    return switcher.get(rc, "Unknown result code: " + str(rc))


def check_digi_cert_ca():
    try:
        f = open("DigiCertCA.crt")
        logging.debug("DigiCertCA.crt exist.")
        f.close()
    except IOError:
        logging.debug("DigiCertCA.crt missing, downloading...")
        # Send HTTP GET request to github to fetch the certificate
        response = requests.get("https://raw.githubusercontent.com/datacentricdesign/dcd-hub/develop/certs/DigiCertCA.crt")
        # If the HTTP GET request can be served
        if response.status_code == 200:
            # Write the file contents in the response to a file specified by
            # local_file_path
            with open("DigiCertCA.crt", 'wb') as local_file:
                for chunk in response.iter_content(chunk_size=128):
                    local_file.write(chunk)
            logging.debug("DigiCertCA.crt downloaded.")
        else:
            logging.warn("DigiCertCA not found.")
