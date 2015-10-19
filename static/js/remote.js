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
  var textC = document.createElement('p')
  var text = document.createTextNode("id: " + device.id + "; name: " + device.name)
  textC.appendChild(text)
  container.appendChild(textC)
}

function listDevices() {
  devices.map(deviceInfo)
}

function health() {
  var request = new XMLHttpRequest()
  request.open('GET', '/health', true)

  request.onload = function () {
    if (request.status >= 200 && request.status < 400) {
      var data = JSON.parse(request.responseText)
      var statusText = document.createTextNode(data.health)
      var icon = document.getElementById('health-status-icon')

      if (data.health.toLowerCase() === 'ok') {
        removeClass(icon, 'fa-heart-o')
        removeClass(icon, 'gray')
        addClass(icon, 'fa-heart')
        addClass(icon, 'red')
      } else {
        removeClass(icon, 'fa-heart')
        removeClass(icon, 'red')
        addClass(icon, 'fa-heart-o')
        addClass(icon, 'gray')
      }
    } else {
      console.err('Error received from REST API', request.status, request.responseText)
    }
  };

  request.onerror = function (error) {
    console.err('Error: ', error)
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

document.onreadystatechange = function(){
  if (document.readyState === 'complete') {
    health()
    listDevices()
  }
}
