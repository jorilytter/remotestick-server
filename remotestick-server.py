#!/usr/bin/env python

#
#   Copyright 2015 Jori Lytter
#   Copyright 2010 Patrik Akerfeldt
#
#   Licensed under the Apache License, Version 2.0 (the "License");
#   you may not use this file except in compliance with the License.
#   You may obtain a copy of the License at
#
#       http://www.apache.org/licenses/LICENSE-2.0
#
#   Unless required by applicable law or agreed to in writing, software
#   distributed under the License is distributed on an "AS IS" BASIS,
#   WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
#   See the License for the specific language governing permissions and
#   limitations under the License.
#
#
#

from bottle import route, run, response, request, static_file
from ctypes import util
from ctypes import *
from getopt import getopt, GetoptError
from sys import argv, exit, platform
from base64 import b64encode
import time

VERSION = "0.5.0"
API_VERSION = 2

#Device methods
TELLSTICK_TURNON = 1
TELLSTICK_TURNOFF = 2
TELLSTICK_BELL = 4
TELLSTICK_TOGGLE = 8
TELLSTICK_DIM = 16
TELLSTICK_LEARN = 32
ALL_METHODS = TELLSTICK_TURNON | TELLSTICK_TURNOFF | TELLSTICK_BELL | TELLSTICK_TOGGLE | TELLSTICK_DIM | TELLSTICK_LEARN

reqauth = True
username = None
password = None
libtelldus = None
static_folder = "./static/"

def loadlibrary(libraryname=None):
    if libraryname == None:
        libraryname = "telldus-core"
        ret = util.find_library(libraryname)
    else:
        ret = libraryname

    if ret == None:
        return (None, libraryname)

    global libtelldus
    libtelldus = cdll.LoadLibrary(ret)
    libtelldus.tdGetName.restype = c_char_p
    libtelldus.tdLastSentValue.restype = c_char_p
    libtelldus.tdGetProtocol.restype = c_char_p
    libtelldus.tdGetModel.restype = c_char_p
    libtelldus.tdGetErrorString.restype = c_char_p
    libtelldus.tdLastSentValue.restype = c_char_p

    return ret, libraryname

def errmsg(x):
    return {
        100: "Authentication failed",
        101: "Unsupported format",
        201: "Name not supplied",
        202: "Model not supplied",
        203: "Protocol not supplied",
        210: "Malformed parameters",
        211: "No device removed",
        220: "Method not supported",
        300: "Telldus-core error"
    }[x]

def err(responsecode, request, code, code_msg=None):
    response.status = responsecode
    if responsecode == 401:
        response.headers.append("WWW-Authenticate", "Basic realm=\"RemoteStick\"")

    if code_msg == None:
        code_msg = errmsg(code)

    return "{\"request\": \"" + request + "\", \"error\": \"" + code_msg + "\"}"

def authenticate(auth):
    global username, password
    if reqauth and auth == None:
        return False
    elif reqauth:
        sentUsername, sentPassword = auth
        return (username == sentUsername and password == sentPassword)
    else:
        return True

def read_device(identity):
    name = libtelldus.tdGetName(identity)
    lastcmd = libtelldus.tdLastSentCommand(identity, 1)
    protocol = libtelldus.tdGetProtocol(identity)
    model = libtelldus.tdGetModel(identity)
    methods = libtelldus.tdMethods(identity, ALL_METHODS)
    lastValue = libtelldus.tdLastSentValue(identity)

    element = ("{"
            "{\"id\": \"" + str(identity) + "},"
            "{\"name\": \"" + name + "\"},"
            "{\"protocol\": \"" + protocol + "\"},"
            "{\"model\": \"" + model + "\"},")

    if lastcmd == 1:
        element += "{\"lastcmd\": \"ON\"},"
    else:
        element += "{\"lastcmd\": \"OFF\"}"
    if lastValue != None and lastValue != "":
        try:
            lastValueConverted = int(lastValue)
            element += ",{\"lastvalue\": \"" + str(lastValueConverted) + "\"}"
        except Exception, e:
            pass

    if methods & TELLSTICK_BELL:
        element += ",{\"supportedMethod\": {\"id\": \"" + str(TELLSTICK_BELL) + "\", \"name\": \"TELLSTICK_BELL\"}"
    if methods & TELLSTICK_TOGGLE:
        element += ",{\"supportedMethod\": {\"id\": \"" + str(TELLSTICK_TOGGLE) + "\", \"name\": \"TELLSTICK_TOGGLE\"}"
    if methods & TELLSTICK_TURNOFF:
        element += ",{\"supportedMethod\": {\"id\": \"" + str(TELLSTICK_TURNOFF) + "\", \"name\": \"TELLSTICK_TURNOFF\"}"
    if methods & TELLSTICK_TURNON:
        element += ",{\"supportedMethod\": {\"id\": \"" + str(TELLSTICK_TURNON) + "\", \"name\": \"TELLSTICK_TURNON\"}"
    if methods & TELLSTICK_DIM:
        element += ",{\"supportedMethod\": {\"id\": \"" + str(TELLSTICK_DIM) + "\", \"name\": \"TELLSTICK_DIM\"}"
    if methods & TELLSTICK_LEARN:
        element += ",{\"supportedMethod\": {\"id\": \"" + str(TELLSTICK_LEARN) + "\", \"name\": \"TELLSTICK_LEARN\"}"
    element += "}"
    return element

def pre_check():
    if not authenticate(request.auth):
        return False, 401, 100
    return True, None, None

def set_headers():
    response.set_content_type("application/json; charset=utf8")
    response.headers.append("X-API-VERSION", str(API_VERSION))
    response.headers.append("X-VERSION", VERSION)

@route("/health", method="GET")
def health():
    set_headers()
    return "{\"health\": \"OK\"}"

@route("/devices", method="GET")
def devices():
    set_headers()
    result = "{["
    numDevices = libtelldus.tdGetNumberOfDevices()
    for i in range(numDevices):
        result += read_device(libtelldus.tdGetDeviceId(i))
    result += "]}"
    return result

@route("/devices", method="POST")
def new_device():
    request_str = "POST /devices"
    set_headers()

    name = request.POST.get("name", "").strip()
    if not name:
        return err(400, request_str, 201)

    model = request.POST.get("model", "")
    if not model:
        return err(400, request_str, 202)

    protocol = request.POST.get("protocol", "")
    if not protocol:
        return err(400, request_str, 203)

    rawParams = request.POST.get("parameters", "")
    parameters = []
    if rawParams != None:
        for param in rawParams.split():
            keyval = param.split("=")
            if len(keyval) != 2:
                return err(400, request_str, 210)
            else:
                parameters.append(keyval)
    identity = libtelldus.tdAddDevice()
    libtelldus.tdSetName(identity, name.strip())
    libtelldus.tdSetProtocol(identity, protocol.strip())
    libtelldus.tdSetModel(identity, model.strip())
    for param in parameters:
        libtelldus.tdSetDeviceParameter(identity, param[0], param[1])
    retval = read_device(identity)
    return retval

@route("/devices/:id", method="GET")
def get_device(id):
    request_str = "GET /devices/" + id
    set_headers()

    try:
        retval = read_device(int(id))
        return retval
    except ValueError:
        return err(400, request_str, 210)


@route("/devices/:id", method="DELETE")
def delete_device(id):
    request_str = "DELETE /devices/" + id
    set_headers()

    try:
        retval = libtelldus.tdRemoveDevice(int(id))
    except ValueError:
        return err(400, request_str, 210)

    if retval == 1:
        return "{\"status\": \"OK\"}"
    else:
        return err(400, request_str, 211)

@route("/devices/:id", method="PUT")
def change_device(id):
    request_str = "PUT /devices/" + id
    set_headers()

    name = request.POST.get("name", "").strip()
    protocol = request.POST.get("protocol", "").strip()
    model = request.POST.get("model", "").strip()
    if name:
        libtelldus.tdSetName(int(id), name)

    if model:
        libtelldus.tdSetModel(int(id), model)

    if protocol:
        libtelldus.tdSetProtocol(int(id), protocol)

    try:
        retval = read_device(int(id))
        return retval
    except ValueError:
        return err(400, request_str, 210)
    return "{\"status\": \"OK\"}"

@route("/devices/:id/on", method="GET")
def turnon_device(id):
    request_str = "GET /devices/" + id + "/on"
    set_headers()

    try:
        identity = int(id)
    except ValueError:
        return err(400, request_str, 210)

    if libtelldus.tdMethods(identity, TELLSTICK_TURNON) & TELLSTICK_TURNON:
        retval = libtelldus.tdTurnOn(identity)
        if retval == 0:
            return "{\"status\": \"OK\"}"
        else:
            return err(502, request_str, 300, libtelldus.tdGetErrorString(retval))
    else:
        return err(400, request_str, 220)

@route("/devices/:id/off", method="GET")
def turnoff_device(id):
    request_str = "GET /devices/" + id + "/off"
    set_headers()

    try:
        identity = int(id)
    except ValueError:
        return err(400, request_str, 210)

    if libtelldus.tdMethods(identity, TELLSTICK_TURNOFF) & TELLSTICK_TURNOFF:
        retval = libtelldus.tdTurnOff(identity)
        if retval == 0:
            return "{\"status\": \"OK\"}"
        else:
            return err(502, request_str, 300, libtelldus.tdGetErrorString(retval))
    else:
        return err(400, request_str, 220)

@route("/devices/:id/dim/:level", method="GET")
def dim_device(id, level):
    request_str = "GET /devices/" + id + "/dim/" + level
    set_headers()

    try:
        identity = int(id)
        dimlevel = int(level)
#        dimlevel = int(round(int(level)*2.55))
    except ValueError:
        return err(400, request_str, 210)

    if libtelldus.tdMethods(identity, TELLSTICK_DIM) & TELLSTICK_DIM:
        retval = libtelldus.tdDim(identity, dimlevel)
        if retval == 0:
            return "{\"status\": \"OK\"}"
        else:
            return err(502, request_str, 300, libtelldus.tdGetErrorString(retval))
    else:
        return err(400, request_str, 220)

@route("/devices/:id/learn", method="GET")
def learn_device(id):
    request_str = "GET /devices/" + id + "/learn"
    set_headers()

    try:
        identity = int(id)
    except ValueError:
        return err(400, request_str, 210)

    if libtelldus.tdMethods(identity, TELLSTICK_LEARN) & TELLSTICK_LEARN:
        retval = libtelldus.tdLearn(identity)
        if retval == 0:
            return "{\"status\": \"OK\"}"
        else:
            return err(502, request_str, 300, libtelldus.tdGetErrorString(retval))
    else:
        return err(400, request_str, 220)

@route("/", method="GET")
@route("", method="GET")
def static_default():
    global static_folder
    return static_file("index.html", root=static_folder)

@route("/:file#.*[^/]#", method="GET")
def static(file):
    global static_folder
    return static_file(file, root=static_folder)

def usage():
    print "Usage: remotestick-server [OPTION] ..."
    print "Expose tellstick interfaces through RESTful services."
    print ""
    print "Without any arguments remotestick-server will start a http server on 127.0.0.1:8422 where no authentication is required."
    print "Setting the name of the telldus-core library should not be needed. remotestick-server is able to figure out the correct library name automatically. If, for some reason, this is unsuccessful, use --library."
    print ""
    print "Given that static files are not disabled, they are always accessed through the URI path /s/ not matter where the static files folder is defined."
    print ""
    print "-h, --host\t\tHost/IP which the server will bind to, default to loopback"
    print "-p, --port\t\tPort which the server will listen on, default to 8422"
    print "-u, --username\t\tUsername used for client authentication"
    print "-s, --password\t\tPassword used for client authentication"
    print "-l, --library\t\tName of telldus-core library"
    print "-f, --static\t\tPath to static files folder, defaults to ./static"
    print "-d, --disable-static\tDisable static files"
    print "-V, --version\t\tPrint the version number and exit"

def version():
    print "remotestick-server v" + VERSION

def main():
    try:
        opts, args = getopt(argv[1:], "?h:p:u:s:l:f:dV", ["?", "host=", "port=", "username=", "password=", "library=", "static=", "disable-static", "version"])
    except GetoptError, err:
        print str(err)
        usage()
        exit(2)
    host = None
    port = None
    library = None
    global username
    global password
    global reqauth
    global static

    for o, a in opts:
        if o in ("-h", "--host"):
            host = a
        elif o in ("-p", "--port"):
            port = a
        elif o in ("-u", "--username"):
            username = a
        elif o in ("-s", "--password"):
            password = a
        elif o in ("-l", "--library"):
            library = a
        elif o in ("-f", "--static"):
            static_folder = a
        elif o in ("-V", "--version"):
            version()
            exit()
        elif o == "-?":
            usage()
            exit()
        else:
            assert False, "unhandled option " + o

    lib, libname = loadlibrary(library)
    if lib == None:
        print "Error: Cannot find library " + libname
        exit(3)

    if username == None or password == None:
        print "Warning: No authentication required. Please consider setting --username and --password."
        reqauth = False

    if (host == None):
        host = "0.0.0.0"

    if (port == None):
        port = "8422"

    run(host=host, port=port)

if __name__ == "__main__":
    main()
