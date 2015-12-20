

function deviceInfo(device) {

  var container = document.getElementById('outlets-info')
  var link = deviceLink(device)
  var deviceNameSection = deviceName(device.name)
  var deviceIconContainer = deviceIcon(device)

  var deviceContainer = document.createElement('div')
  addClass(deviceContainer, 'device')
  deviceContainer.appendChild(deviceNameSection)
  deviceContainer.appendChild(deviceIconContainer)
  link.appendChild(deviceContainer)
  container.appendChild(link)
}

function deviceIcon(device) {

  var deviceIconContainer = document.createElement('div')
  var icon = lightBulbIcon(device)
  deviceIconContainer.appendChild(icon)
  addClass(deviceIconContainer, 'device-details')

  return deviceIconContainer
}

function deviceName(name) {

  var deviceNameSection = document.createElement('div')
  var deviceName = document.createTextNode(name)
  deviceNameSection.appendChild(deviceName)
  addClass(deviceNameSection, 'device-name')

  return deviceNameSection
}

function deviceLink(device) {

  var link = document.createElement('a')
  link.setAttribute('href', '#')

  if (device.lastcmd.toLowerCase() === 'off') {
    link.setAttribute('onclick', 'turnOn(' + device.id + ');return false;')
  } else {
    link.setAttribute('onclick', 'turnOff(' + device.id + ');return false;')
  }

  return link
}

function lightBulbIcon(device) {

  var icon = document.createElement('i')
  addClass(icon, 'fa')
  addClass(icon, 'fa-lightbulb-o')

  if (device.lastcmd.toLowerCase() === 'off') {
    addClass(icon, 'gray')
  } else {
    addClass(icon, 'yellow')
  }

  return icon
}


function deviceTurnedOn(device) {
  return device.lastcmd.toLowerCase() === 'on'
}

function deviceTurnedOff(device) {
  return device.lastcmd.toLowerCase() === 'off'
}

function getDeviceId(device) {
  return device.id
}

function allOffButton(devices) {

  var anyDeviceTurnedOn = devices.filter(deviceTurnedOn).length > 0
  var deviceIds = devices.filter(deviceTurnedOn).map(getDeviceId)

  var container = document.getElementById('outlets-info')
  var link = document.createElement('a')
  link.setAttribute('href', '#')
  link.setAttribute('onclick', 'allOff([' + deviceIds + ']);return false;')

  var allOffSection = document.createElement('div')
  var name = document.createTextNode('All OFF')
  allOffSection.appendChild(name)
  addClass(allOffSection, 'device-name')

  var buttonContainer = document.createElement('div')
  addClass(buttonContainer, 'device')
  addClass(buttonContainer, 'halfbutton')
  
  buttonContainer.appendChild(allOffSection)

  link.appendChild(buttonContainer)
  container.appendChild(link)

  if (anyDeviceTurnedOn) {
    removeClass(allOffSection, 'gray')
    addClass(allOffSection, 'yellow')
  } else {
    removeClass(allOffSection, 'yellow')
    addClass(allOffSection, 'gray')
  }
}

function allOnButton(devices) {
	var anyDeviceTurnedOff = devices.filter(deviceTurnedOff).length > 0
	var deviceIds = devices.filter(deviceTurnedOff).map(getDeviceId)
	
	var container = document.getElementById('outlets-info')
  var link = document.createElement('a')
  link.setAttribute('href', '#')
  link.setAttribute('onclick', 'allOn([' + deviceIds + ']);return false;')

  var allOnSection = document.createElement('div')
  var name = document.createTextNode('All ON')
  allOnSection.appendChild(name)
  addClass(allOnSection, 'device-name')

  var buttonContainer = document.createElement('div')
  addClass(buttonContainer, 'device')
  addClass(buttonContainer, 'halfbutton')
  buttonContainer.appendChild(allOnSection)

  link.appendChild(buttonContainer)
  container.appendChild(link)

  if (anyDeviceTurnedOff) {
    removeClass(allOnSection, 'gray')
    addClass(allOnSection, 'yellow')
  } else {
    removeClass(allOnSection, 'yellow')
    addClass(allOnSection, 'gray')
  }	
}

function listDevices() {

  var request = new XMLHttpRequest()
  request.open('GET', '/devices', true)

  request.onload = function () {
    if (request.status >= 200 && request.status < 400) {
      var response = JSON.parse(request.responseText)
      var container = document.getElementById('outlets-info')
      while (container.hasChildNodes()) {
        container.removeChild(container.firstChild);
      }
      response.devices.map(deviceInfo)
	  allOnButton(response.devices)
      allOffButton(response.devices)
    } else {
      console.error('Error received from REST API', request.status, request.responseText)
    }
  }

  request.onerror = function (error) {
    console.error('Error: ', error)
  };

  request.send()
}

function allOff(deviceIds) {

  deviceIds.map(function(deviceId) {
    var url = '/devices/' + deviceId + '/off'
    toggleOutlet(url)
  })
}

function allOn(deviceIds) {
	deviceIds.map(function(deviceId){
		var url = '/devices/' + deviceId + '/on'
		toggleOutlet(url)
	})
}

function turnOn(deviceId) {
  toggleOutlet('/devices/' + deviceId + '/on')
}

function turnOff(deviceId) {
  toggleOutlet('/devices/' + deviceId + '/off')
}

function toggleOutlet(requestUrl) {

  var request = new XMLHttpRequest()
  request.open('GET', requestUrl, true)

  request.onload = function () {
    if (request.status >= 200 && request.status < 400) {
      var data = JSON.parse(request.responseText)
      if (data.status.toLowerCase() === 'ok') {
        listDevices()
      } else {
        console.error('Error while turning outlet on', request.responseText)
      }
    } else {
      console.error('Error received from REST API', request.status, request.responseText)
    }
  }

  request.onerror = function (error) {
    console.error('Error: ', error)
  };

  request.send()
}

function addClass(element, className) {

  if (element.classList) {
    element.classList.add(className)
  } else {
    element.className += ' ' + className
  }
}

function removeClass(element, className) {

  if (element.classList) {
    element.classList.remove(className)
  } else {
    element.className = element.className.replace(new RegExp('(^|\\b)' + className.split(' ').join('|') + '(\\b|$)', 'gi'), ' ')
  }
}

document.onreadystatechange = function() {

  if (document.readyState === 'complete') {
    listDevices()
  }
}
