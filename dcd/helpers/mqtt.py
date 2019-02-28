
def mqtt_result_code(rc):
    switcher = {
        0: "Connection successful",
        1: "Connection refused – incorrect protocol version",
        2: "Connection refused – invalid client identifier",
        3: "Connection refused – server unavailable",
        4: "Connection refused – bad username or password",
        5: "Connection refused – not authorised"
    }
    return switcher.get(rc, "Unknown result code: " + str(rc))
