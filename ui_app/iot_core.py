from AWSIoTPythonSDK.MQTTLib import AWSIoTMQTTClient
import time
import json

client = AWSIoTMQTTClient("raspiDeviceID001")
client.configureEndpoint("awv4wp0jjayh9-ats.iot.us-east-2.amazonaws.com", 8883)
client.configureCredentials("certificates/AmazonRootCA1.crt", "certificates/private.pem.key", "certificates/certificate.pem.crt")

client.configureOfflinePublishQueueing(-1)  # Infinite queueing
client.configureDrainingFrequency(2)  # 2 Hz
client.configureConnectDisconnectTimeout(10)  # 10 sec
client.configureMQTTOperationTimeout(5)  # 5 sec

# Connect
client.connect()

# Publish a message every 5 seconds
while True:
    message = {
        "temperature": 23.5,
        "humidity": 60,
        "device": "raspberry_pi"
    }
    client.publish("/sensors/", json.dumps(message), 1)
    print("Message published")
    time.sleep(5)
