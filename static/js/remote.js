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
    } else {
      console.error('Error received from REST API', request.status, request.responseText)
    }
  }

  request.onerror = function (error) {
    console.error('Error: ', error)
  };

  request.send()
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
