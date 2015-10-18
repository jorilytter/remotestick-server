
function health() {
  var request = new XMLHttpRequest()
  request.open('GET', '/health', true)

  request.onload = function () {
    if (request.status >= 200 && request.status < 400) {
      var data = JSON.parse(request.responseText)
      document.getElementById('health-status').innerHTML = data.health
    } else {
      console.err('Error received from REST API', request.status, request.responseText)
    }
  };

  request.onerror = function (error) {
    console.err('Error: ', error)
  };

  request.send()
}

document.onreadystatechange = function(){
  if (document.readyState === 'complete') {
    health()
  }
}
