#!/usr/bin/env python

#
# Copyright (c) 2010, Patrik Akerfeldt. All rights reserved.
# 
# Redistribution and use in source and binary forms, with or without modification, are
# permitted provided that the following conditions are met:
# 
#    1. Redistributions of source code must retain the above copyright notice, this list of
#       conditions and the following disclaimer.
# 
#    2. Redistributions in binary form must reproduce the above copyright notice, this list
#       of conditions and the following disclaimer in the documentation and/or other materials
#       provided with the distribution.
# 
# THIS SOFTWARE IS PROVIDED BY PATRIK AKERFELDT ``AS IS'' AND ANY EXPRESS OR IMPLIED
# WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED WARRANTIES OF MERCHANTABILITY AND
# FITNESS FOR A PARTICULAR PURPOSE ARE DISCLAIMED. IN NO EVENT SHALL PATRIK AKERFELDT OR
# CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR
# CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR
# SERVICES; LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT (INCLUDING
# NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS SOFTWARE, EVEN IF
# ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
# 
# The views and conclusions contained in the software and documentation are those of the
# authors and should not be interpreted as representing official policies, either expressed
# or implied, of Patrik Akerfeldt.
# 
# 


from bottle import route, run, response, request
from ctypes import cdll, c_char_p, util

#Device methods
TELLSTICK_TURNON = 1
TELLSTICK_TURNOFF = 2
TELLSTICK_BELL = 4
TELLSTICK_TOGGLE = 8
TELLSTICK_DIM = 16
TELLSTICK_LEARN = 32
ALL_METHODS = TELLSTICK_TURNON | TELLSTICK_TURNOFF | TELLSTICK_BELL | TELLSTICK_TOGGLE | TELLSTICK_DIM | TELLSTICK_LEARN

#Error codes
TELLSTICK_SUCCESS = 0
TELLSTICK_ERROR_NOT_FOUND = -1
TELLSTICK_ERROR_PERMISSION_DENIED = -2
TELLSTICK_ERROR_DEVICE_NOT_FOUND = -3
TELLSTICK_ERROR_METHOD_NOT_SUPPORTED = -4
TELLSTICK_ERROR_COMMUNICATION = -5
TELLSTICK_ERROR_UNKNOWN = -99

#Device typedef
TELLSTICK_TYPE_DEVICE = 1
TELLSTICK_TYPE_GROUP = 2

#Protocol Nexa
TELLSTICK_DEVICE_YCR3500 = 1
TELLSTICK_DEVICE_YCR300D = 2
TELLSTICK_DEVICE_WSR1000 = 3
TELLSTICK_DEVICE_CMR1000 = 4
TELLSTICK_DEVICE_CMR300 = 5
TELLSTICK_DEVICE_PA33300 = 6
TELLSTICK_DEVICE_EL2000 = 8
TELLSTICK_DEVICE_EL2005 = 9
TELLSTICK_DEVICE_EL2006 = 10
TELLSTICK_DEVICE_SYCR3500 = 12
TELLSTICK_DEVICE_SYCR300 = 13
TELLSTICK_DEVICE_HDR105 = 14
TELLSTICK_DEVICE_ML7100 = 15
TELLSTICK_DEVICE_EL2004 = 16
TELLSTICK_DEVICE_EL2016 = 17
TELLSTICK_DEVICE_EL2010 = 18
TELLSTICK_DEVICE_LYCR1000 = 20
TELLSTICK_DEVICE_LYCR300 = 21
TELLSTICK_DEVICE_LCMR1000 = 22
TELLSTICK_DEVICE_LCMR300 = 23
TELLSTICK_DEVICE_EL2023 = 24
TELLSTICK_DEVICE_EL2024 = 25
TELLSTICK_DEVICE_EL2021 = 26
TELLSTICK_DEVICE_EL2017 = 27
TELLSTICK_DEVICE_EL2019 = 28

#Protocol Ikea
TELLSTICK_DEVICE_KOPPLA = 19

ret = util.find_library("TelldusCore")
if ret == None:
    print "None"
else:
    print ret
# libtelldus = cdll.LoadLibrary("libtelldus-core.so")
libtelldus = cdll.LoadLibrary(ret)
libtelldus.tdGetName.restype = c_char_p
libtelldus.tdLastSentValue.restype = c_char_p
libtelldus.tdGetProtocol.restype = c_char_p
libtelldus.tdGetModel.restype = c_char_p
libtelldus.tdGetErrorString.restype = c_char_p

def errmsg(x):
    return {
        100: "API key could not be verified",
        101: "Unsupported format",
        201: "Name not supplied",
        202: "Model not supplied",
        203: "Protocol not supplied",
        210: "Malformed parameters",
        211: "No device removed",
        220: "Method not supported",
        300: "Telldus-core error"
    }[x]
   
def err(format, responsecode, request, code, code_msg=None):
    response.status = responsecode
    if code_msg == None:
        code_msg = errmsg(code)
    
    if format == "xml":
        return err_xml(request, code_msg)
    else:
        return err_xml(request, code_msg)

def err_xml(request, msg):
    return "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<hash>\n\t<request>" + request + "</request>\n\t<error>" + msg + "</error>\n</hash>"

def authenticate(encoded_base64):
    print encoded_base64
    if encoded_base64 == "Basic dGVzdDp0ZXN0":
        return True
    else:
        return False

def read_device(identity):
    name = libtelldus.tdGetName(identity)
    lastcmd = libtelldus.tdLastSentCommand(identity, 1)
    protocol = libtelldus.tdGetProtocol(identity)
    model = libtelldus.tdGetModel(identity)
    methods = libtelldus.tdMethods(identity, ALL_METHODS)
    element = "<device id=\"" + str(identity) + "\">\n\t\t<name>" + name + "</name>\n\t\t<protocol>" + protocol + "</protocol>\n\t\t<model>" + model + "</model>\n"
    element += "\t\t<lastcmd>" + ("ON" if lastcmd == 1 else "OFF") + "</lastcmd>\n"
    if methods & TELLSTICK_BELL:
        element += "\t\t<supportedMethod id=\"" + str(TELLSTICK_BELL) + "\">" + "TELLSTICK_BELL</supportedMethod>\n"
    if methods & TELLSTICK_TOGGLE:
        element += "\t\t<supportedMethod id=\"" + str(TELLSTICK_TOGGLE) + "\">" + "TELLSTICK_TOGGLE</supportedMethod>\n"
    if methods & TELLSTICK_TURNOFF:
        element += "\t\t<supportedMethod id=\"" + str(TELLSTICK_TURNOFF) + "\">" + "TELLSTICK_TURNOFF</supportedMethod>\n"
    if methods & TELLSTICK_TURNON:
        element += "\t\t<supportedMethod id=\"" + str(TELLSTICK_TURNON) + "\">" + "TELLSTICK_TURNON</supportedMethod>\n"
    if methods & TELLSTICK_DIM:
        element += "\t\t<supportedMethod id=\"" + str(TELLSTICK_DIM) + "\">" + "TELLSTICK_DIM</supportedMethod>\n"
    if methods & TELLSTICK_LEARN:
        element += "\t\t<supportedMethod id=\"" + str(TELLSTICK_LEARN) + "\">" + "TELLSTICK_LEARN</supportedMethod>\n"
    element += "</device>\n"
    return element

def pre_check(format, accepted_formats):
    if format not in accepted_formats:
        return False,  400, 101
    
    if not authenticate(request.authorization):
        return False, 401, 100
    
    return True, None, None

def set_content_type(format):
    if format == "xml":
        response.content_type = 'text/xml; charset=UTF-8'

@route('/devices\.:format', method='GET')
def devices(format):
    ok, response_code, error_code = pre_check(format, ["xml"])
    if not ok:
        return err(format, response_code, 'GET /devices.' + format, error_code)
    set_content_type(format)

    result = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n<devices>\n"
    numDevices = libtelldus.tdGetNumberOfDevices()
    for i in range(numDevices):
        result += read_device(libtelldus.tdGetDeviceId(i))
    result += "</devices>"
    return result

@route('/devices\.:format', method='POST')
def new_device(format):
    request_str = 'POST /devices.' + format
    ok, response_code, error_code = pre_check(format, ["xml"])
    if not ok:
        return err(format, response_code, request_str, error_code)
    set_content_type(format)
    
    name = request.POST.get('name', '').strip()
    if not name:
        return err(format, 400, request_str, 201)

    model = request.POST.get('model', '').strip()
    if not model:
        return err(format, 400, request_str, 202)

    protocol = request.POST.get('protocol', '').strip()
    if not protocol:
            return err(format, 400, request_str, 203)
        
    rawParams = request.POST.get('parameters', '').strip()
    print rawParams
    parameters = []
    if rawParams != None:
        for param in rawParams.split():
            keyval = param.split('=')
            if len(keyval) != 2:
                return err(format, 400, request_str, 210)
            else:
                parameters.append(keyval)

    identity = libtelldus.tdAddDevice()
    libtelldus.tdSetName(identity, name)
    libtelldus.tdSetProtocol(identity, protocol)
    libtelldus.tdSetModel(identity, model)
    print parameters
    for param in parameters:
        libtelldus.tdSetDeviceParameter(identity, param[0], param[1])

    retval = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    retval += read_device(identity)
    return retval

@route('/devices/:id\.:format', method='GET')
def get_device(id, format):
    request_str = 'GET /devices/' + id + "." + format
    ok, response_code, error_code = pre_check(format, ["xml"])
    if not ok:
        return err(format, response_code, request_str, error_code)
    set_content_type(format)

    retval = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    try:
        retval += read_device(int(id))
        return retval
    except ValueError:
        return err(format, 400, request_str, 210)


@route('/devices/:id\.:format', method='DELETE')
def delete_device(id, format):
    request_str = 'DELETE /devices/' + id + "." + format
    ok, response_code, error_code = pre_check(format, ["xml"])
    if not ok:
        return err(format, response_code, request_str, error_code)
    set_content_type(format)

    try:
        retval = libtelldus.tdRemoveDevice(int(id))
    except ValueError:
        return err(format, 400, request_str, 210)

    if retval == 1:
        return ""
    else:
        return err(format, 400, request_str, 211)

@route('/devices/:id\.:format', method='PUT')
def change_device(id, format):
    request_str = 'PUT /devices/' + id + "." + format
    ok, response_code, error_code = pre_check(format, ["xml"])
    if not ok:
        return err(format, response_code, request_str, error_code)
    set_content_type(format)

    name = request.POST.get('name', '').strip()
    protocol = request.POST.get('protocol', '').strip()
    model = request.POST.get('model', '').strip()
    if not name:
        return err(format, 400, request_str, 101)
        
    libtelldus.tdSetName(int(id), name)
    libtelldus.tdSetProtocol(int(id), protocol)
    libtelldus.tdSetModel(int(id), model)
    
    retval = "<?xml version=\"1.0\" encoding=\"UTF-8\"?>\n"
    try:
        retval += read_device(int(id))
        return retval
    except ValueError:
        return err(format, 400, request_str, 210)
    return ""

@route('/devices/:id/on\.:format', method='GET')
def turnon_device(id, format):
    request_str = 'GET /devices/' + id + "/on." + format
    ok, response_code, error_code = pre_check(format, ["xml"])
    if not ok:
        return err(format, response_code, request_str, error_code)
    set_content_type(format)
    
    try:
        identity = int(id)
    except ValueError:
        return err(format, 400, request_str, 210)
    
    if libtelldus.tdMethods(identity, TELLSTICK_TURNON) & TELLSTICK_TURNON:    
        retval = libtelldus.tdTurnOn(identity)
        if retval == 0:
            return ""
        else:
            return err(format, 502, request_str, 300, libtelldus.tdGetErrorString(retval))
    else:
        return err(format, 400, request_str, 220)

@route('/devices/:id/off\.:format', method='GET')
def turnoff_device(id, format):
    request_str = 'GET /devices/' + id + "/off." + format
    ok, response_code, error_code = pre_check(format, ["xml"])
    if not ok:
        return err(format, response_code, request_str, error_code)
    set_content_type(format)

    try:
        identity = int(id)
    except ValueError:
        return err(format, 400, request_str, 210)
    
    if libtelldus.tdMethods(identity, TELLSTICK_TURNOFF) & TELLSTICK_TURNOFF:    
        retval = libtelldus.tdTurnOff(identity)
        if retval == 0:
            return ""
        else:
            return err(format, 502, request_str, 300, libtelldus.tdGetErrorString(retval))
    else:
        return err(format, 400, request_str, 220)

@route('/devices/:id/dim/:level\.:format', method='GET')
def dim_device(id, level, format):
    request_str = 'GET /devices/' + id + "/dim/" + level + "." + format
    ok, response_code, error_code = pre_check(format, ["xml"])
    if not ok:
        return err(format, response_code, request_str, error_code)
    set_content_type(format)

    try:
        identity = int(id)
        dimlevel = chr(int(level))
    except ValueError:
        return err(format, 400, request_str, 210)

    if libtelldus.tdMethods(identity, TELLSTICK_DIM) & TELLSTICK_DIM:    
        retval = libtelldus.tdDim(identity, dimlevel)
        if retval == 0:
            return ""
        else:
            return err(format, 502, request_str, 300, libtelldus.tdGetErrorString(retval))
    else:
        return err(format, 400, request_str, 220)

run(reloader=True, port=8001)
