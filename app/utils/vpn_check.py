# vpn_check.py
import requests

def is_vpn(ip_address: str) -> bool:
    """
    Detect if an IP belongs to a VPN/Proxy using ip-api.com.
    Returns True if VPN/Proxy is detected.
    """
    try:
        url = f"http://ip-api.com/json/{ip_address}?fields=proxy,hosting"
        response = requests.get(url, timeout=5)
        data = response.json()

        # If 'proxy' or 'hosting' is True, it might be VPN/Datacenter IP
        return data.get("proxy", False) or data.get("hosting", False)

    except Exception as e:
        print("VPN check error:", e)
        return False
