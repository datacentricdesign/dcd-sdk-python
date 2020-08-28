from dcd.helpers.network import get_local_ip, get_external_ip, check_type_ip

local_ip = get_local_ip()
type_local_ip = check_type_ip(local_ip)
print(local_ip + ' ' + str(type_local_ip))
external_ip = get_external_ip()
type_external_ip =  check_type_ip(external_ip)
print(external_ip + ' ' + str(type_external_ip))
