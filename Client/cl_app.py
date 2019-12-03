import sys
import csv
import threading
from PyQt5 import QtCore, QtWidgets
from PyQt5.QtWidgets import QDialog, QApplication
from window_config import Ui_MainWindow
from datetime import datetime
import matplotlib
import matplotlib.pyplot as mpp
from matplotlib import dates
import Adafruit_DHT
import boto3
import ast

#Global variables
update_interval = 5 # refresh interval in seconds
unit = 'C' #default temperature units
temp_list=[] #lists for storing temp, rh, and timestamp data for plotting
rh_list=[]
time_list=[]
fmtr = dates.DateFormatter("%H:%M:%S") #date format for timestamp display

temp_high = -40.0; #initial values based on DHT22 datasheet
temp_low = 125.0;
rh_high = 0.0;
rh_low = 100.0;

cntr=0; #no. of measurements for computing statistics

ui=Ui_MainWindow() #initialize app window

sqs = boto3.resource('sqs',aws_access_key_id='AKIAZVHKMN3HJCBYL27Y',aws_secret_access_key='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',region_name='us-west-2') #initialize sqs resource
queue = sqs.get_queue_by_name(QueueName='sqs.fifo',QueueOwnerAWSAccountId='664063995598') #intantiate queue to recieve messages
acchttp='https://sqs.us-west-2.amazonaws.com/664063995598/sqs.fifo'

class Login(QtWidgets.QWidget):
    
    switch_window = QtCore.pyqtSignal() #window switch signal

    def __init__(self):
        
        QtWidgets.QWidget.__init__(self)
        self.setWindowTitle('Client-Side Login Window')

        layout = QtWidgets.QGridLayout()

        self.button = QtWidgets.QPushButton('Login')
        self.username = QtWidgets.QLineEdit()
        self.username.setPlaceholderText('Username')
        self.passwd = QtWidgets.QLineEdit()
        self.passwd.setPlaceholderText('Password')
        self.button.clicked.connect(self.login)

        layout.addWidget(self.username)
        layout.addWidget(self.passwd)
        layout.addWidget(self.button)

        self.setLayout(layout)

    def login(self):
        
        if(self.username.text() == 'tanmay' and self.passwd.text() == '123'):
            self.switch_window.emit() #emit switch signal to invoke main window only if credentials are valid

class Controller:
    
    def __init__(self):
        pass
    
    def show_login(self):
        
        self.login = Login()
        self.login.switch_window.connect(self.show_main) #show main window if switching signal received
        self.login.show()
        
    def show_main(self):
        
        global ui
        self.window = QDialog()
        ui.setupUi(self.window)
        self.login.close()
        self.window.show()
        ui.pushButton_Fetch.clicked.connect(lambda:fetch_and_plot())

def main():
    
    app = QApplication(sys.argv) #launch app
    controller = Controller() #launch controller
    controller.show_login() #show login window
    sys.exit(app.exec_()) #exit app
    
def fetch_and_plot():
    
    global temp, temp_low, temp_high, temp_avg, rh, rh_low, rh_high, rh_avg, ts_temp_low, ts_temp_high, ts_rh_low, ts_rh_high, unit, ui, cntr;
    global queue
    
    #lists for plotting data
    temp_list = []
    temp_high_list = []
    temp_low_list = []
    temp_avg_list = []
    rh_list = []
    rh_high_list = []
    rh_low_list = []
    rh_avg_list = []
    ts_list = []
    count = 0 #To check if queue is not empty
    
    #Loop to receive 20 messgaes and append data to the lists for plotting
    for i in range(2):
        response = queue.receive_messages(QueueUrl='https://sqs.us-west-2.amazonaws.com/664063995598/sqs.fifo',MaxNumberOfMessages=10)
        #response = sqs.Queue(url=acchttp).receive_messages()
        #print(response)
        for msg in response:
            count = count + 1
            m = ast.literal_eval(msg.body)
            temp_list.append(float(m['temperature_str']))
            temp_high_list.append(float(m['temperature_high_str']))
            temp_low_list.append(float(m['temperature_low_str']))
            temp_avg_list.append(float(m['temperature_avg_str']))
            rh_list.append(float(m['rh_str']))
            rh_high_list.append(float(m['rh_high_str']))
            rh_low_list.append(float(m['rh_low_str']))
            rh_avg_list.append(float(m['rh_avg_str']))
            ts_list.append(datetime.strptime(m['timestamp'],'%d %b %Y %H:%M:%S'))
            msg.delete()
            
    # queue was empty
    if count == 0:
        print('Empty Queue')
        return

    #Set Humdity Labels
    ui.label_rh.setText(m['rh_str'])
    ui.label_avg_rh.setText(m['rh_avg_str'])
    ui.label_low_rh.setText(m['rh_low_str'])
    ui.label_high_rh.setText(m['rh_high_str'])
    
    #Values for temperature 
    temp = float(m['temperature_str'])
    temp_avg = float(m['temperature_avg_str'])
    temp_low = float(m['temperature_low_str'])
    temp_high = float(m['temperature_high_str'])
    
    #display temperature data in UI
    display_data()
    
    #Set  timestamp labels
    ui.label_low_temp_timestamp.setText(m['ts_temp_low']) #display timestamps
    ui.label_high_temp_timestamp.setText(m['ts_temp_high'])
    ui.label_low_rh_timestamp.setText(m['ts_rh_low'])
    ui.label_high_rh_timestamp.setText(m['ts_rh_high'])
    ui.label_timestamp.setText(m['timestamp'])
    '''
    #For plotting temperature and humidity time series
    fig = mpp.figure()
    fig.suptitle('Temperature and Humidity Values fetched = ' + str(count))
    mpp.subplot(2,1,1) #temperature plot
    mpp.plot(ts_list,temp_list)
    mpp.plot(ts_list,temp_high_list)
    mpp.plot(ts_list,temp_low_list)
    mpp.plot(ts_list,temp_avg_list)
    mpp.legend(['Curr','Max','Min','Avg'],loc='upper left')
    ax=mpp.gca()
    ax.xaxis.set_major_formatter(fmtr) #format x axis to display formatted time
    mpp.xlabel('Time [mm:ss]')
    mpp.ylabel('Temperature')
    
    mpp.subplot(2,1,2) #relative humidity plot
    mpp.plot(ts_list,rh_list)
    mpp.plot(ts_list,rh_high_list)
    mpp.plot(ts_list,rh_low_list)
    mpp.plot(ts_list,rh_avg_list)
    mpp.legend(['Curr','Max','Min','Avg'],loc='upper left')
    ax=mpp.gca()
    ax.xaxis.set_major_formatter(fmtr)
    mpp.xlabel('Time [mm:ss]')
    mpp.ylabel('Humidity [%]')    
    mpp.show()
    '''
def display_data():
    
    """function to update temperature, humidity depending on radio button selected"""
    
    global temp, temp_low, temp_high, temp_avg, rh, rh_low, rh_high, rh_avg, ts_temp_low, ts_temp_high, ts_rh_low, ts_rh_high, unit, ui, cntr;
    temperature_str = "{:.2f}".format(temp)
    ui.label_temp.setText(temperature_str) #display temperature
    temperature_avg_str = "{:.2f}".format(temp_avg)
    ui.label_avg_temp.setText(temperature_avg_str) #display temperature
    temperature_low_str = "{:.2f}".format(temp_low)
    ui.label_low_temp.setText(temperature_low_str) #display temperature
    temperature_high_str = "{:.2f}".format(temp_high)
    ui.label_high_temp.setText(temperature_high_str) #display temperature

if __name__ == '__main__':
    main() #call to main function
    
