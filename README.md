# Build Status

A small app for monitoring the Jenkins builds and displaying the status on a
[PI Hut Status Board](https://thepihut.com/products/status-board-pro).

The project uses python3 running on a Raspberry PI zero. Jenkins API
access uses the [jenkins-webapi](https://pypi.python.org/pypi/jenkins-webapi)
python package.

# Installation

There are two ways included to run the service.

## belena.io

It can be run under the [belena.io cloud](http://belena.io/cloud) container deployment
infrastructure using the supplied Dockerfile.

## systemd

Installation can be done directly on a raspberry pi.
Install using pip:
```
sudo pip3 install -r requirements.txt
sudo pip3 install buildstatus
```

There is an example systemd config supplied which can be edited and installed to
launch the service on boot. Edit the file to configure for your system and
install as follows:
```
sudo cp buildstatus.service.example /etc/systemd/system/buildstatus.service
sudo systemctl daemon-reload
sudo systemctl enable buildstatus.service
sudo systemctl start buildstatus.service
```
