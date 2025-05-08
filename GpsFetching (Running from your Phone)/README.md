
## 📍 IoT GPS Location Uploader to Azure IoT Hub

This Python script captures GPS or network-based location data on an Android device (using Termux) and publishes it to an [Azure IoT Hub](https://azure.microsoft.com/en-us/products/iot-hub) using MQTT. It handles secure authentication via SAS tokens and includes fallback logic for improved location reliability.

---

## 🛠️ Requirements

- An Android device with **[Termux](https://f-droid.org/packages/com.termux/)** installed.
- [`termux-api`](https://wiki.termux.com/wiki/Termux:API) package installed (`pkg install termux-api`).
- Python 3.x
- Required Python libraries:
  ```bash
  pip install paho-mqtt
  ````

---

## 📦 Configuration

Edit the top of the script to configure:

```python
iot_hub_name = "YOUR-IOT-HUB-NAME"
device_id = "YOUR-IOT-HUB-DEVICE"
device_primary_key = "YOUR-DEVICE-PRIMARY-KEY"  # Base64-encoded primary key from Azure IoT Hub
```

You can find these in the Azure Portal under:

* **IoT Hub → Devices → Your Device → Primary Key**

---

## 📡 How It Works

1. Prompts you to choose a location provider: `network` or `gps`.
2. Uses `termux-location` to fetch live location data.
3. Publishes location (latitude, longitude, altitude, timestamp) to Azure IoT Hub via MQTT.
4. Automatically regenerates SAS tokens when expired.
5. Retries with a fallback provider if the first fails.

---

## 📤 Message Format

Each message published to Azure contains:

```json
{
  "latitude": 12.345678,
  "longitude": 98.765432,
  "altitude": 12.3,
  "timestamp": 1715176342
}
```

---

## 🔐 Authentication

The script generates [SAS Tokens](https://learn.microsoft.com/en-us/azure/iot-hub/iot-hub-devguide-security#security-tokens) using HMAC-SHA256 to authenticate the device securely.

---

## 🚀 Running the Script

Run on Termux:

```bash
python gps_uploader.py
```

> 📌 On first run, you'll be prompted to choose a location provider (`network` is faster, `gps` is more accurate).

---

## 🧪 Example Output

```
📡 Choose location provider to use (network/gps): gps
✅ Connected with result code 0
📡 Provider: gps
🚦 Speed: 0.0 km/h
🎯 Accuracy: 8.06 meters
📤 Sending GPS: {"latitude":12.345678,"longitude":98.765432,"altitude":5.6,"timestamp":1715176342}
```

---

## 🛑 Stop the Script

Press `Ctrl + C` to stop the script gracefully.

---

## 📎 License

This script is provided for educational and prototyping purposes.

---

## 🙋 Need Help?

If you run into issues with the MQTT connection or SAS tokens, double-check:

* Your IoT Hub name and device ID
* That your device is registered in Azure IoT Hub
* Network connectivity on your Android device