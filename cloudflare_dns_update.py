import requests
from typing import List

# Adjust acc. to your information
ZONEID = ""
TOKEN = ""
DOMAINS = ["*.example.org", "example.org"]

def updateIPs(
    zoneID : str, 
    token : str, 
    domains : List[str], 
    ipv4 : str = None, 
    ipv6 : str = None
):
    """Uses the cloudflare API to update the given domain's IPV4 and/or IPV6 adresses."""

    if ipv4 is None and ipv6 is None:
        raise Exception("Either an IPV4 or IPV6 adress must be given.")
    
    if domains is None or not hasattr(domains, '__len__') or len(domains) == 0:
        raise Exception("At least one domain (*.example.org, example.org) must be given.")

    headers = {
        "content-type": "application/json",
        "Authorization": f"Bearer {token}"
    }

    # First request the current records and match them with the domain list
    availableRecords = requests.get(
        url=f"https://api.cloudflare.com/client/v4/zones/{zoneID}/dns_records",
        headers = headers
    ).json()

    if not availableRecords["success"]:
        errors = "\n".join("\t" + e["message"] + f" (Code {e['code']})" for e in availableRecords["errors"])
        raise Exception("Requesting existing entries failed with message: \n" + errors)

    # Match available records against requested domains and update
    matchingRecords = [r for r in availableRecords["result"] if r["type"] in ["A", "AAAA"] and r["name"] in domains]
    for record in matchingRecords:
        updateIP = ipv4 if record["type"] == "A" else ipv6
        if updateIP is None or record["content"] == updateIP: continue

        recordID = record["id"]
        recordName = record["name"]
        recordType = record["type"]

        response = requests.put(
            url = f"https://api.cloudflare.com/client/v4/zones/{zoneID}/dns_records/{recordID}",
            headers=headers,
            json={
                "content": updateIP,
                "type": recordType,
                "name": recordName
            }
        ).json()

        if not response["success"]:
            errors = "\n".join("\t" + e["message"] + f" (Code {e['code']})" for e in response["errors"])
            raise Exception(f"Update for {recordName} (Type: {recordType}) failed: \n" + errors)

def determineIPs():
    ipv4 = requests.get("https://api.ipify.org").text
    ipv6 = requests.get("https://api64.ipify.org").text
    return ipv4, ipv6

if __name__ == "__main__":
    ipv4, ipv6 = determineIPs()
    updateIPs(ZONEID, TOKEN, DOMAINS, ipv4,ipv6)
