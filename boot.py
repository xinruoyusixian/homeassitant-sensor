


# This file is executed on every boot (including wake-boot from deepsleep)
#import esp
#esp.osdebug(None)
#os.dupterm(None, 1) # disable REPL on UART(0)

import time,lib,webrepl,gc,os, machine,display,hass
from machine import Pin, I2C,WDT,Timer
from AHT10  import AHT10   
i2c = I2C(scl=Pin(14), sda=Pin(12), freq=1000000)



led=Pin(2,Pin.OUT)
led.off()
OLED_SW=False
hm= AHT10(i2c)
display=display.display(i2c,128,32)
display.text("connecting wifi...",0,10)
display.show()

net=lib.wifi("PDCN_2.4G","1234567788","temperature")

webrepl.start()







restCout=300

if(not net[1]):

  lib.ap("temperature_seinor")

  print("wifi连接失败,已打开wifi热点,temperature_seinor,1234567788,\n 5分钟后重启")

  #Timer(-1).init(period=180000, mode=Timer.PERIODIC, callback=lambda t:machine.reset())
  
  while True:
      if restCout==0:
          machine.reset()
      t=hm.temperature()
      h=hm.humidity()
      def func(that):
          that.fill(0)
          that.text("Reset At %ss" %restCout,3,3)
      display.display(str(t),str(h),"h","ap",func)
      time.sleep(1)
      display.display(str(t),str(h),"t","ap",func)

      time.sleep(1)
      restCout-=2
  
  
  

restCout=30
while 1:
    display.fill(0)
    display.text("wating for %ss"%restCout,0,10)
    display.show()
    time.sleep(1)
    if restCout==0:
      break
    restCout-=1


lib.update_time()
def feedDog():
  tim = Timer(-1)
  tim.init(period=1000, mode=Timer.PERIODIC, callback=lambda t:wdt.feed())
  
def mqMsg(tpoic,msg):
  global OLED_SW
  msg=msg.decode()
  print(msg)
  if msg=="ON":
      OLED_SW=True
      ha.sw_On()
  if msg=="OFF":
      OLED_SW=False
      ha.sw_Off()
#开启看门狗I
wdt = WDT()
ha=hass.hass()
ha.callback_rec("homeassistant/bedroom/switch1/set",mqMsg)
ha.text("启动,IP:%s"%net[0].ifconfig()[0])

ha.registrar('t')#注册温度传感器
ha.registrar('h')#注册温度传感器

led.on()
timeFlag=True
gc.mem_free()

display.fill(0)

count=0
display.poweroff()
isTimeUpdated=False
displayType=True
while (1):
    try:
       wdt.feed()
       sec=time.localtime()[5]
       t=hm.temperature()
       h=hm.humidity()
       runSec=time.ticks_ms()/1000
        
       if OLED_SW:
            display.poweron()
       else:
            display.poweroff()   
       ha.check_msg()
       if sec%5==0:
         led.off()
         if timeFlag:
            #print(t,h,disSW.value())
            ha.publishTH(t,h)
            timeFlag=False
       else:
            led.on()
            timeFlag=True
       

       if count%10==0:
          displayType=False if displayType else True
          if displayType:

            display.display(str(t),str(h),"h")
          else:
            display.display(str(t),str(h),"t")
       #手动计数器     
       count+=1
       if count%399==0:
           ha.registrar('h')#注册温度传感器
           #ha.text("注册湿度")
       if count%599==0:
           ha.registrar('t')#注册温度传感器
           #ha.text("注册温度")
       if count%899==0:
            #尝试更新时间 直到更新成功
            if not isTimeUpdated:
              print("开始更新时间")
              if lib.update_time():
                isTimeUpdated=True
                ha.text("时间更新成功")
                
       if count==19000:
            count=0
            ha.text("运行时间:%.2f H"%(runSec/3600))




       gc.collect()

    except KeyboardInterrupt:

      feedDog()

      ha.text("手动中断")

      print("中断,开始喂狗")

      raise "中断"

    except Exception as e:

        print(e)

        ha.text(str(e))



