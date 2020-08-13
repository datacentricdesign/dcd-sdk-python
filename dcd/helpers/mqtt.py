import requests


def mqtt_result_code(rc):
    switcher = {
        0: "Connection successful",
        1: "Connection refused - incorrect protocol version",
        2: "Connection refused - invalid client identifier",
        3: "Connection refused - server unavailable",
        4: "Connection refused - bad username or password",
        5: "Connection refused - not authorised"
    }
    return switcher.get(rc, "Unknown result code: " + str(rc))


def check_digi_cert_ca():
    try:
        f = open("DigiCertCA.crt")
        print("DigiCertCA.crt exist.")
        f.close()
    except IOError:
        print("DigiCertCA.crt missing, downloading...")
        # Send HTTP GET request to github to fetch the certificate
        response = requests.get("https://raw.githubusercontent.com/datacentricdesign/dcd-hub/develop/certs/DigiCertCA.crt")
        # If the HTTP GET request can be served
        if response.status_code == 200:
            # Write the file contents in the response to a file specified by
            # local_file_path
            with open("DigiCertCA.crt", 'wb') as local_file:
                for chunk in response.iter_content(chunk_size=128):
                    local_file.write(chunk)
            print("DigiCertCA.crt downloaded.")
        else:
            print("DigiCertCA not found.")
