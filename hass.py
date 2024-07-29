import time,mqtt,ujson



class hass:
    def __init__(self,ip="192.168.5.1",port=1883,client_id='hass_TH'):
        
        self.hassConfig_T_topic='homeassistant/sensor/sensorBedroomT/config'
        self.hassConfig_H_topic='homeassistant/sensor/sensorBedroomH/config'
        self.hassConfig_V_topic='homeassistant/sensor/sensorBedroom/state'
        self.topic='homeassistant'
        self.text_topic='txt/state'
        self.config_T="""
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
        }}
        """
        self.config_H="""
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
        }}
        """


        self.config_Value="""
        {
        "temperature":%f,
        "humidity":%f
        }
    """
        self.mq=mqtt.mqtt("192.168.5.1",1883,self.topic,self.callback_rec,client_id)
        self.mq.connect()
    def callback_rec(self,topic,msg):
        pass
    def registrar(self,type="t"):
        if type=='h':
            self.mq.publish(self.config_H,self.hassConfig_H_topic)
            return
        self.mq.publish(self.config_T,self.hassConfig_T_topic)
        return
        
    def publish(self,t,h):
        self.mq.publish(self.config_Value%(t,h),self.hassConfig_V_topic)
    def text(self,txt):
        self.mq.publish(str(txt).encode(),self.text_topic)


