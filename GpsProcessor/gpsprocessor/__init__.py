import json
import logging
import azure.functions as func

def main(events):
    messages = []

    for event in events:
        try:
            gps_data = json.loads(event.get_body().decode('utf-8'))

            logging.info(f"Received GPS: {gps_data}")

            messages.append({
                "target": "newGpsLocation",
                "arguments": [gps_data]
            })

        except Exception as e:
            logging.error(f"Error processing GPS data: {e}")

    return messages
