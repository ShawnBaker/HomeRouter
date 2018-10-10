# RPi Camera Viewer

Simple router for home use based on Ubuntu Server 18.04.

## Copyright and License

Copyright &copy; 2018 Shawn Baker using the [MIT License](https://opensource.org/licenses/MIT).

## Instructions

* install Ubuntu Server 18.04.1
* login
  * use "ip a" to get
    * the names of your ethernet interfaces
    * the addresss of the server
* copy SSH key to server
  * ssh-copy-id user@address
* log in with SSH key
  - git clone https://github.com/ShawnBaker/HomeRouter.git
  - cd HomeRouter/scripts
  - sudo ./hr-install-sys.sh
  - wait for system to reboot
* log in with SSH key
  - cd HomeRouter/scripts
  - sudo ./hr-install-net.sh enp0s3 192.168.0.10 icey.local enp0s8
  - wait for system to reboot
