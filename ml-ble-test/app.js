var canvas = document.querySelector('canvas');
var statusText = document.querySelector('#statusText');
var responseText = document.querySelector('#responseText');
var button = document.querySelector('#selectButton');


function startConnect() {
  statusText.textContent = 'Waiting for notifications...';

  manylabsBle.connect()
  .then(() => manylabsBle.startNotificationsHttpStatus().then(handleHttpStatus))
  .then(() => manylabsBle.requestGet())
  .catch(error => {
    console.log("apps.js: manylabsBle.connect error")
    statusText.textContent = error;
  });
}

function clear() {
  responseText.textContent = "";
}

function formatTime(dt) {
  var ts = dt.format("dd/MM/yyyy HH:mm:ss fff");
  return ts;
}

button.addEventListener('click', function() {
  manylabsBle.connect()
  .then( () =>  {
    statusText.textContent = 'Waiting for notifications...';
  })
  .then(() => manylabsBle.startNotificationsHttpStatus().then(handleHttpStatus))
  .then(() => manylabsBle.requestGet())
  .catch(error => {
    console.log("apps.js: manylabsBle.connect error")
    statusText.textContent = error;
  });
});


function handleHttpStatus(heartRateMeasurement) {
  console.log("handleHttpStatus")
  heartRateMeasurement.addEventListener('characteristicvaluechanged', event => {
    console.log("handleHttpStatus.event characteristicvaluechanged")
    //console.log("event.target.value=" + event.target.value);
    //var heartRateMeasurement = manylabsBle.parseHeartRate(event.target.value);
    var value = event.target.value;
    // In Chrome 50+, a DataView is returned instead of an ArrayBuffer.
    value = value.buffer ? value : new DataView(value);
    let http_status = value.getUint8(0);
    options = { hour12: false }
    var ts = new Date();
    var dt_prefix = ts.toLocaleTimeString('en-US', options) + ": ";
    statusText.innerHTML = dt_prefix + "HTTP Status=" + http_status;
    if (http_status == manylabsBle.STATUS_BIT_BODY_RECEIVED) {
      // retrieve http body
      console.log("handleHttpStatus.event: Retrieving body...");
      manylabsBle.getHttpBody().then(body => {
        console.log("getHttpBody.body: " + body);
        responseText.innerHTML += "<br/>";
        //responseText.innerHTML += ts.toLocaleTimeString('en-US', options) + "." + (ts.getTime() % 999) + ": " + body;
        responseText.innerHTML += dt_prefix + body;
     });

    } else {
      console.log("handleHttpStatus.event: Body not received: http_status=" + http_status);
    }
    /*
    statusText.innerHTML = heartRateMeasurement.heartRate;
    //statusText.innerHTML = heartRateMeasurement.heartRate + ' &#x2764;';
    heartRates.push(heartRateMeasurement.heartRate);
    if (heartRates.length > 50) {
      heartRates = heartRates.slice(5);
    }
    drawWaves();
    */
  });
}

var heartRates = [];
var mode = 'bar';

canvas.addEventListener('click', event => {
  mode = mode === 'bar' ? 'line' : 'bar';
  drawWaves();
});

function drawWaves() {
  requestAnimationFrame(() => {
    //console.log("heartRates.length: " + heartRates.length);
    canvas.width = parseInt(getComputedStyle(canvas).width.slice(0, -2)) * devicePixelRatio;
    canvas.height = parseInt(getComputedStyle(canvas).height.slice(0, -2)) * devicePixelRatio;

    var context = canvas.getContext('2d');
    var margin = 2;
    var max = Math.max(0, Math.round(canvas.width / 11));
    var offset = Math.max(0, heartRates.length - max);
    context.clearRect(0, 0, canvas.width, canvas.height);
    context.strokeStyle = '#00796B';
    if (mode === 'bar') {
      for (var i = 0; i < Math.max(heartRates.length, max); i++) {
        var barHeight = Math.round(heartRates[i + offset ] * canvas.height / 200);
        context.rect(11 * i + margin, canvas.height - barHeight, margin, Math.max(0, barHeight - margin));
        context.stroke();
      }
    } else if (mode === 'line') {
      context.beginPath();
      context.lineWidth = 6;
      context.lineJoin = 'round';
      context.shadowBlur = '1';
      context.shadowColor = '#333';
      context.shadowOffsetY = '1';
      for (var i = 0; i < Math.max(heartRates.length, max); i++) {
        var lineHeight = Math.round(heartRates[i + offset ] * canvas.height / 200);
        if (i === 0) {
          context.moveTo(11 * i, canvas.height - lineHeight);
        } else {
          context.lineTo(11 * i, canvas.height - lineHeight);
        }
        context.stroke();
      }
    }
  });
}

window.onresize = drawWaves;

document.addEventListener("visibilitychange", () => {
  if (!document.hidden) {
    drawWaves();
  }
});
