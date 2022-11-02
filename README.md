# Self Driving PiCar
 Self driving PiCar using a neural network.

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

#### Make sure the ports are open: *sudo ufw disable*

## Static IPV4
> 1. Right click Wifi Icon -> Wireless and Wired Network Settings -> Select wlan interface or an SSID
> 2. IPV4 -> 192.168.1.120/24
> 3. Router -> 192.168.1.1
> 4. DNS Servers -> 192.168.1.1
> 5. Leave the rest empty and keep "Automatically configure empty options" checked

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
 
#### Install dhcp for mac to ssh into car
```
sudo apt-get install isc-dhcp-server
sudo nano /etc/dhcp/dhcpd.conf
```

```
 # Scroll down and paste this to the end
 # This will assign the first device connected X.X.X.3 up to X.X.X.10
 ddns-update-style interim;
  default-lease-time 600;
  max-lease-time 7200;
  authoritative;
  log-facility local7;
  subnet 192.168.4.0 netmask 255.255.255.0 {
   range 192.168.4.3 192.168.4.10;
  }

# Now enable it by replacing the interfaces file
cd /etc/network
sudo cp /etc/network/adhoc-interface interfaces

# Or if you want to switch back to the old file
sudo cp /etc/network/wifi-interface interfaces

# sudo reboot now
```
#### Make sure to remove the networks in to stop auto connecting
/etc/wpa_supplicant/wpa_supplicant.conf
