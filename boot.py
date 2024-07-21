# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#os.dupterm(None, 1) # disable REPL on UART(0)

import time,lib,webrepl,gc,os, machine
from machine import Pin, I2C,WDT,Timer
led=Pin(2,Pin.OUT)
led.off()
net=lib.wifi("yourSSD","PWD","temperature")
webrepl.start()

if(not net[1]):
  lib.ap("temperature_seinor","1234567788")
  print("wifi连接失败,已打开wifi热点,temperature_seinor,1234567788,\n 5分钟后重启")
  Timer(-1).init(period=300000, mode=Timer.PERIODIC, callback=lambda t:machine.reset())
  raise
  
  
  
from AHT10  import AHT10
#魔改了ssd1306 直接操作现存不用framebuffer 对8266友好
from oled_save_mem  import oled

from mqtt  import mqtt
i2c = I2C(scl=Pin(14), sda=Pin(12), freq=1000000)

hm= AHT10(i2c)




def p_data(topic,msg):
         print(topic,msg)

lib.update_time()
mq=mqtt("192.168.5.1",1883,"homeassistant",p_data,client_id="hass")
mq.connect()

hassConfig_T='homeassistant/sensor/sensorBedroomT/config'
hassConfig_H='homeassistant/sensor/sensorBedroomH/config'
hassConfig_V='homeassistant/sensor/sensorBedroom/state'

config_T="""
{

   "device_class":"temperature",

   "state_topic":"homeassistant/sensor/sensorBedroom/state",

   "unit_of_measurement":"°C",

   "value_template":"{{ value_json.temperature}}",

   "unique_id":"temp01ae",

   "device":{

      "identifiers":[

          "bedroom01ae"

      ],

      "name":"温度计",

      "manufacturer": "Example sensors Ltd.",

      "model": "K9",

      "serial_number": "12AE3010545",

      "hw_version": "1.01a",

      "sw_version": "2024.1.0",

      "configuration_url": "https://example.com/sensor_portal/config"

   }

}

"""

config_H="""

{

   "device_class":"humidity",

   "state_topic":"homeassistant/sensor/sensorBedroom/state",

   "unit_of_measurement":"%",

   "value_template":"{{ value_json.humidity}}",


   "unique_id":"hum01ae",

   "device":{
      "name":"湿度计",
      "identifiers":[
         "bedroom01ae"

      ]

   }

}

"""


config_Value="""

{

   "temperature":%f,

   "humidity":%f

}

"""

def feedDog():
  tim = Timer(-1)
  tim.init(period=1000, mode=Timer.PERIODIC, callback=lambda t:wdt.feed())
  
#开启看门狗I
wdt = WDT()

#启用oled显示
#display=oled(i2c)


mq.publish(b"启动,IP:%s"%(net[0].ifconfig()[0]),'txt/state')
gc.collect()
led.on()
timeFlag=True
while (1):
    try:
       
      
       wdt.feed()
       sec=time.localtime()[5]
       mq.check_msg()
       if sec%7==0:
              mq.publish(config_T,hassConfig_T)
       if sec%10==0:
              mq.publish(config_H,hassConfig_H)
        

              pass
              mq.ping()
       
       t=hm.temperature()
       h=hm.humidity()
       #display.clear()
       #display.string(str(t))
       

       if sec%2==0:
         
         led.off()
         if timeFlag:
            print(t,h,sec)
            mq.publish(config_Value%(t,h),hassConfig_V)
            timeFlag=False
            
       else:
            
            led.on()
            timeFlag=True
            
    except KeyboardInterrupt:
      feedDog()
      mq.publish(b"手动中断",'txt/state')
      print("手动中断,开始喂狗")
      raise "中断"


