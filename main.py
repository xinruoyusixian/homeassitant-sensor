# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#os.dupterm(None, 1) # disable REPL on UART(0)

import time,lib,webrepl,gc,os, machine,display,hass
from machine import Pin, I2C,WDT,Timer


i2c = I2C(scl=Pin(14), sda=Pin(12), freq=1000000)
led=Pin(2,Pin.OUT)
led.off()


display=display.display(i2c,128,32)
display.oled.text("connecting wifi...",0,10)
display.oled.show()

net=lib.wifi("PDCN_2.4G","1234567788","temperature")
webrepl.start()

if(not net[1]):
  lib.ap("temperature_seinor","1234567788")
  print("wifi连接失败,已打开wifi热点,temperature_seinor,1234567788,\n 5分钟后重启")
  Timer(-1).init(period=180000, mode=Timer.PERIODIC, callback=lambda t:machine.reset())
  display.oled.text("AP OPEND...",0,10)
  display.oled.show()
  raise
  
  
  
from AHT10  import AHT10       


hm= AHT10(i2c)



lib.update_time()


def feedDog():
  tim = Timer(-1)
  tim.init(period=1000, mode=Timer.PERIODIC, callback=lambda t:wdt.feed())
  
#开启看门狗I
wdt = WDT()
ha=hass.hass()
ha.mq.publish(b"启动,IP:%s"%(net[0].ifconfig()[0]),'txt/state')

led.on()
timeFlag=True
display.oled.fill(0)
display.draw_ui()

count=0
display.oled.poweroff()
disSW=Pin(16,Pin.IN)
while (1):
    try:
       wdt.feed()
       sec=time.localtime()[5]
              
       t=hm.temperature()
       h=hm.humidity()
        
       if disSW.value():
            display.oled.poweron()
       else:
            display.oled.poweroff()   
       ha.mq.check_msg()
       if sec%4==0:
         led.off()
         if timeFlag:
            print(t,h,disSW.value())
            ha.publish(t,h)
            timeFlag=False
       else:
            led.on()
            timeFlag=True


       if count<15:
          time.sleep(0.1)
          display.display(str(t),str(h),"h")
       else:
          time.sleep(0.1)
          display.display(str(t),str(h),"t")
       #手动计数器     
       count+=1
       if count==30:
          count=0
       gc.collect()
    except KeyboardInterrupt:
      feedDog()
      ha.mq.publish(b"手动中断",'txt/state')
      print("中断,开始喂狗")
      raise "中断"
    finally:
        ha.mq.publish(b"出现异常",'txt/state')


