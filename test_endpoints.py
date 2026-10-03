import requests

def test_mayday_endpoint():
    # Automatically test if the beacon route is alive
    response = requests.post("https://www.laveto.net/hangar/mayday_signal", json={"vin_dna": "TEST"})
    if response.status_code == 200:
        print("✅ Beacon Protocol: SUCCESS")
    else:
        print(f"❌ Beacon Protocol: FAILED (Status: {response.status_code})")

if __name__ == "__main__":
    test_mayday_endpoint()