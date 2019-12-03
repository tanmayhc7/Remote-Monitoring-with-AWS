# Remote-Monitoring-with-AWS
This was developed for CMPE 297-01 IoT Course.
The project demo can be found [here](https://youtu.be/HBdQzKkqzAA)

# About the Project:
Server-side and client-side Qt dashboards are created for displaying temperature and humidity values read from a DHT22 sensor. The server-side Raspberry Pi (temp_rh_app.py) measures temperature and relative humidity at 5s intervals and stores them in a '.csv' file. A second server-side script (basicPubSub.py) reads this CSV file, and publishes it to the AWS IoT Core at the 'sdk/test/Python' topic.

On the AWS, a lambda function was created that is triggered upon each message reception, and writes this data into a SQS FIFO queue. The client-side Raspberry Pi (temp_rh_app.py) uses a BOTO3 client to interface with, and read messages from the SQS queue. 

-----
## Running the application -- Server
Navigate to the Server folder:
```
cd Server
```
Issue the following from a Bash shell to start data collection and server-side UI:
```
sudo python3 app.py
```
Login credentials for server-side UI:
```
username: tanmay
password: 123
```
Launch the script that initiates MQTT messaging to the AWS IoT Thing:
```
./start.sh
```
## Running the application -- Client
```
cd Client
```
Launch the client-side application:
```
python3 cl_app.py
```
Login credentials for client-side UI:
```
username: tanmay
password: 123
```
