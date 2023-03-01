# Self Driving PiCar
 Self driving PiCar using lane keep algorithm and communication protocol.

## Installation 
  [Full Guide](https://docs.sunfounder.com/projects/picar-v/en/latest/servo_configuration.html#get-source-code)

>1. cd ~
>2. git clone https://github.com/sunfounder/SunFounder_PiCar-V -b V3.0
>3. cd ~/SunFounder_PiCar-V
>4. sudo ./install_dependencies
>5. cd ~/SunFounder_PiCar-V
>6. picar servo-install

## Starting the server: 
>
> - cd ~/SunFounder_PiCar-V/remote-control
> - sudo ./start

## Wheel Calibration
  Clibrate the wheels using the web browser when you run sudo ./start there will be a calibration place, move the front wheels and click OK.
  Then use the offset in the config file of the source code.

#### Make sure the ports are open: *sudo ufw disable*

## Ad Hoc Wireless Network
[Guide](https://pyshine.com/How-to-configure-Raspberry-Pi-in-Ad-hoc-wifi-mode/)

[Guide 2](https://wiki.debian.org/WiFi/AdHoc)

#### Setup
```
cd /etc/network

# Backup
sudo cp interfaces wifi-interface
sudo nano adhoc-interface
```

#### First car
```
auto wlan0
iface wlan0 inet static
    address 192.168.4.1
    netmask 255.255.255.0
    wireless-channel 1
    wireless-essid RPitest
    wireless-mode ad-hoc
```
    
#### Second car
```
auto wlan0
iface wlan0 inet static
    address 192.168.4.2
    netmask 255.255.255.0
    wireless-channel 1
    wireless-essid RPitest
    wireless-mode ad-hoc
```
 
#### Now enable it by replacing the interfaces file
```
cd /etc/network
sudo cp /etc/network/adhoc-interface interfaces
```

#### MUST DO: sudo nano /etc/dhcpcd.conf

Set the file to only have the following.

```

denyinterfaces wlan0

```

This took ages to figure out, you must do this in order to stop wlan0 not using the static ip. DHCP client will try see if there is anything to connect to and assign an ip, this is not what we want.

Use this if there are issues https://github.com/simondlevy/RPiAdHocWiFi
