import subprocess
import json
import paho.mqtt.client as mqtt
import ssl
import time
import hmac
import hashlib
import base64
import urllib.parse
import warnings

# ===================== Configuration =====================
iot_hub_name = "YOUR-IOT-HUB-NAME"
device_id = "YOUR-IOT-HUB-DEVICE"
device_primary_key = "YOUR-DEVICE-PRIMARY-KEY"  # 🔐 Base64 key

mqtt_host = f"{iot_hub_name}.azure-devices.net"
mqtt_port = 8883

client_id = device_id
username = f"{iot_hub_name}.azure-devices.net/{device_id}/?api-version=2021-04-12"
resource_uri = f"{iot_hub_name}.azure-devices.net/devices/{device_id}"

# ===================== SAS Token Generator =====================
def generate_sas_token(uri, key, expiry_in_secs=3600):
    expiry = int(time.time()) + expiry_in_secs
    sign_key = f"{uri}\n{expiry}".encode("utf-8")
    key_bytes = base64.b64decode(key)
    signature = base64.b64encode(
        hmac.new(key_bytes, sign_key, hashlib.sha256).digest()
    )
    sig_encoded = urllib.parse.quote(signature, safe="")
    return f"SharedAccessSignature sr={uri}&sig={sig_encoded}&se={expiry}", expiry

# Initial token
sas_token, token_expiry = generate_sas_token(resource_uri, device_primary_key)

# ===================== Choose Initial Provider =====================
initial_provider = input("📡 Choose location provider to use (network/gps): ").strip().lower()
if initial_provider not in ["network", "gps"]:
    print("❌ Invalid choice. Defaulting to 'network'.")
    initial_provider = "network"
fallback_provider = "gps" if initial_provider == "network" else "network"

# ===================== Location Fetcher =====================
def get_location(provider):
    try:
        output = subprocess.check_output(["termux-location", "-p", provider])
        return json.loads(output)
    except Exception as e:
        print(f"❌ {provider} failed: {e}")
        return None

# ===================== MQTT Setup =====================
warnings.filterwarnings("ignore", category=DeprecationWarning)

def on_connect(client, userdata, flags, rc):
    print(f"✅ Connected with result code {rc}")

client = mqtt.Client(client_id=client_id, protocol=mqtt.MQTTv311)
client.username_pw_set(username=username, password=sas_token)
client.tls_set(cert_reqs=ssl.CERT_REQUIRED, tls_version=ssl.PROTOCOL_TLSv1_2)
client.on_connect = on_connect
client.connect(mqtt_host, mqtt_port, 60)
client.loop_start()

# ===================== SAS Refresh Logic =====================
def refresh_sas_token_if_needed():
    global sas_token, token_expiry
    if time.time() > token_expiry - 60:
        print("🔁 SAS token expired or about to expire. Regenerating...")
        sas_token, token_expiry = generate_sas_token(resource_uri, device_primary_key)
        client.username_pw_set(username=username, password=sas_token)

# ===================== Send GPS Logic =====================
def send_gps():
    refresh_sas_token_if_needed()

    location = get_location(initial_provider)
    if not location:
        print(f"⚠️ {initial_provider} failed, trying {fallback_provider}...")
        location = get_location(fallback_provider)
        if not location:
            print("❌ Both providers failed. Skipping...")
            return

    speed_mps = location.get("speed", 0)
    speed_kph = speed_mps * 3.6
    accuracy = location.get("accuracy", None)

    print(f"📡 Provider: {initial_provider}")
    print(f"🚦 Speed: {speed_kph:.1f} km/h")
    print(f"🎯 Accuracy: {accuracy} meters" if accuracy is not None else "🎯 Accuracy: N/A")

    payload = json.dumps({
        "latitude": location["latitude"],
        "longitude": location["longitude"],
        "altitude": location.get("altitude", 0),
        "timestamp": int(time.time())
    })

    topic = f"devices/{device_id}/messages/events/"
    print("📤 Sending GPS:", payload)
    client.publish(topic, payload, qos=1)

# ===================== Main Loop =====================
try:
    while True:
        send_gps()
        time.sleep(3)
except KeyboardInterrupt:
    print("🚫 Program interrupted. Exiting...")
    client.loop_stop()
    client.disconnect()
