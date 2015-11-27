# remotestick-server

## What is it?
RemoteStick server exposes the Tellstick
(see [Telldus Homepage](http://www.telldus.se) ) interface through RESTful
services. RemoteStick server uses the native library libtelldus-core to
communicate with the Tellstick. It supports resource browsing and resource
operations (like turning on/off a device). Responses are given in JSON format.
It aims to fully reflect the capabilities of the libtelldus-core.

## Prerequisites
telldus-core need be installed. telldus-core is an open-source library developed
by the very same company manufacturing the Tellstick, namely Telldus.
Either:

 * install TelldusCenter from
 [http://download.telldus.se/TellStick/Software/TelldusCenter](http://download.telldus.se/TellStick/Software/TelldusCenter)
 (which will give you the telldus-core library as well) or
 * compile/install telldus-core manually. telldus-core is found here
 [http://download.telldus.se/TellStick/Software/telldus-core/](http://download.telldus.se/TellStick/Software/telldus-core/)

## Modifications
  * This version works only on Linux
  * REST responses are JSON
  * Static resources are served from _/_ instead of _/s/*_
  * Disabling of static resources is removed

## Getting it

 * A stable version of the *original* RemoteStick Server is found here
 http://github.com/pakerfeldt/remotestick-server/.

## Using it
The -? flag will give you help about available command line arguments:
    remotestick-server.py -?

Starting RemoteStick server is as simple as (although not recommended, see
below):
    remotestick-server.py

By default, no authentication will be required (making it possible for anyone to
query your tellstick) and the RESTful services will listen for connections on
your-hostname:8422. Only Basic Authentication (HTTP) currently supported.
You should at least set a username and password, requiring client
authentication:
    remotestick-server.py --username MyUsername --password MyPassword

Project root contains a file `etc.init.d.rstick` that can be used as a init script to start 
the service but stopping the service doesn't work yet.

## Troubleshooting

### Linux
Depending on where the telldus-core library is installed on your system you may
have to define the environment variable LD_LIBRARY_PATH to include the directory
where telldus-core is located.
    export LD_LIBRARY_PATH=${LD_LIBRARY_PATH}:/opt/telldus/bin
