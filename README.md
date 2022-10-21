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
