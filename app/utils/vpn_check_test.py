from vpn_check import is_vpn

user_ip = "8.8.8.8"  # Example IP
if is_vpn(user_ip):
    print("VPN detected! Access denied.")
else:
    print("No VPN detected.")
