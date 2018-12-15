# micropython-outletcntrl
Outlet control for tuya smart tywe3s (esp8266) wireless outlets

I found nice wireless outlets on amazon but didn't want to use the Tuya Smart Life app.
https://www.amazon.com/gp/product/B0713SKWQ1/ref=oh_aui_search_detailpage?ie=UTF8&psc=1

I replaced the orignal firmware with micropython (esp8266-20171101-v1.9.3) and wrote this code so that I could use the outlets with Home Assistant.

Uses MQTT to communicate with the outlet for both status and control.
