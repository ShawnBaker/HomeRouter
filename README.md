# RPi Camera Viewer

Installation scripts and web management interface for creating
a simple home router based on Ubuntu Server 18.04.

## Copyright and License

Copyright &copy; 2018 Shawn Baker using the [MIT License](https://opensource.org/licenses/MIT).

## Instructions

* install Ubuntu Server 18.04.1
  * connect the server to your network with the port to be used for the LAN interface
  * the other port will be the WAN interface
* login
  * use "ip a" to get the
    * names of your WAN and LAN interfaces
    * IP address of the server
* copy your SSH key to the server
  * ex: ssh-copy-id user@server
  * ex: SFTP
  * **You must do this step before going any further.**
* log in with your SSH key
  * git clone https://github.com/ShawnBaker/HomeRouter.git
  * cd HomeRouter/scripts
  * chmod +x *
  * sudo ./install-sys.sh
  * wait for the system to reboot
* log in with your SSH key
  * cd HomeRouter/scripts
  * sudo ./install-net.sh LAN server-IP domain-name WAN [MAC]
    * ex: sudo ./install-net.sh enp4s5 192.168.0.10 my.domain enp4s6
    * ex: sudo ./install-net.sh enp4s5 192.168.0.10 my.domain enp4s6 11:22:33:44:55:66
  * wait for the system to reboot
* plug in your WAN cable and disconnect your router
  * it might take some time for all your devices to adjust to the new server/router
* go to http://server-IP:5000 and log in with your system user name and password
