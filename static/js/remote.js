var devices = [{
  id: "1",
  name: "TV",
  protocol: "foo",
  model: "bar",
  lastCommand: "ON",
  lastValue: "tadaa",
  supportedMethod: {id: "TELLSTICK_TURNOFF", name: "TELLSTICK_TURNOFF"}
},{
  id: "2",
  name: "Työhuone",
  protocol: "foo",
  model: "bar",
  lastCommand: "OFF",
  lastValue: "tadaa",
  supportedMethod: {id: "TELLSTICK_TURNON", name: "TELLSTICK_TURNON"}
}]

function deviceInfo(device) {

  var container = document.getElementById('outlets-info')

  var link = document.createElement('a')
  link.setAttribute('href', '#')
  if (device.lastCommand.toLowerCase() === 'off') {
    link.setAttribute('onclick', 'turnOn(' + device.id + ');return false;')
  } else {
    link.setAttribute('onclick', 'turnOff(' + device.id + ');return false;')
  }

  var deviceContainer = document.createElement('div')
  addClass(deviceContainer, 'device')

  var deviceNameSection = document.createElement('div')
  var deviceName = document.createTextNode(device.name)
  deviceNameSection.appendChild(deviceName)
  addClass(deviceNameSection, 'device-name')

  var deviceIconContainer = document.createElement('div')
  var icon = lightBulbIcon(device)
  deviceIconContainer.appendChild(icon)
  addClass(deviceIconContainer, 'device-details')

  deviceContainer.appendChild(deviceNameSection)
  deviceContainer.appendChild(deviceIconContainer)

  link.appendChild(deviceContainer)
  container.appendChild(link)
}

function lightBulbIcon(device) {

  var icon = document.createElement('i')
  addClass(icon, 'fa')
  addClass(icon, 'fa-lightbulb-o')

  if (device.lastCommand.toLowerCase() === 'off') {
    addClass(icon, 'gray')
  } else {
    addClass(icon, 'yellow')
  }

  return icon
}

function listDevices() {

  var container = document.getElementById('outlets-info')
  while (container.hasChildNodes()) {
    container.removeChild(container.firstChild);
  }

  devices.map(deviceInfo)
}

function turnOn(deviceId) {
  toggleOutlet('/devices/' + deviceId + '/on')
}

function turnOff(deviceId) {
  toggleOutlet('/devices/' + deviceId + '/off')
  listDevices()
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
