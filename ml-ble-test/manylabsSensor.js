(function() {
  'use strict';
  var http_proxy_service_name = 'http_proxy';
  //var service_name = 'heart_rate';
  // heart rate service: 180d
  // 0000180d-0000-1000-8000-00805f9b34fb
  // http_proxy service: 1823 (http_proxy standard name not recognized by bluez-5.44 yet)
  var ml_service_id = '00001823-0000-1000-8000-00805f9b34fb'
  var service_name = ml_service_id;
  //var service_name = 'http_proxy';
  //   optionalServices: ['ba42561b-b1d2-440a-8d04-0cefb43faece']

  class ManylabsSensor {
    constructor() {
      this.device = null;
      this.server = null;
      this._characteristics = new Map();
    }
    connect() {
      //return navigator.bluetooth.requestDevice({filters:[{services:[ "heart_rate" ]}]})

      return navigator.bluetooth.requestDevice({
        // filters: [...] <- Prefer filters to save energy & show relevant devices.
        acceptAllDevices: true,
        optionalServices: ['heart_rate', ml_service_id]})
      /*
      */

      //return navigator.bluetooth.requestDevice({filters:[{services:[ 'battery_service' ]}]})
      //return navigator.bluetooth.requestDevice({filters:[{services:[ 'device_information' ]}]})
      .then(device => {
        this.device = device;
        return device.gatt.connect();
      })
      .then(server => {
        this.server = server;
        return Promise.all([
          server.getPrimaryService(service_name).then(service => {
            return Promise.all([
              this._cacheCharacteristic(service, 'body_sensor_location'),
              this._cacheCharacteristic(service, 'heart_rate_measurement'),
            ])
          })
        ]);
      })
    }

    /* Manylabs Sensor Service */

    getBodySensorLocation() {
      return this._readCharacteristicValue('body_sensor_location')
      .then(data => {
        let sensorLocation = data.getUint8(0);
        switch (sensorLocation) {
          case 0: return 'Other';
          case 1: return 'Chest';
          case 2: return 'Wrist';
          case 3: return 'Finger';
          case 4: return 'Hand';
          case 5: return 'Ear Lobe';
          case 6: return 'Foot';
          default: return 'Unknown';
        }
     });
    }
    startNotificationsHeartRateMeasurement() {
      return this._startNotifications('heart_rate_measurement');
    }
    stopNotificationsHeartRateMeasurement() {
      return this._stopNotifications('heart_rate_measurement');
    }
    parseHeartRate(value) {
      // In Chrome 50+, a DataView is returned instead of an ArrayBuffer.
      value = value.buffer ? value : new DataView(value);
      let flags = value.getUint8(0);
      let rate16Bits = flags & 0x1;
      let result = {};
      let index = 1;
      if (rate16Bits) {
        result.heartRate = value.getUint16(index, /*littleEndian=*/true);
        index += 2;
      } else {
        result.heartRate = value.getUint8(index);
        index += 1;
      }
      let contactDetected = flags & 0x2;
      let contactSensorPresent = flags & 0x4;
      if (contactSensorPresent) {
        result.contactDetected = !!contactDetected;
      }
      let energyPresent = flags & 0x8;
      if (energyPresent) {
        result.energyExpended = value.getUint16(index, /*littleEndian=*/true);
        index += 2;
      }
      let rrIntervalPresent = flags & 0x10;
      if (rrIntervalPresent) {
        let rrIntervals = [];
        for (; index + 1 < value.byteLength; index += 2) {
          rrIntervals.push(value.getUint16(index, /*littleEndian=*/true));
        }
        result.rrIntervals = rrIntervals;
      }
      return result;
    }

    /* Utils */

    _cacheCharacteristic(service, characteristicUuid) {
      return service.getCharacteristic(characteristicUuid)
      .then(characteristic => {
        this._characteristics.set(characteristicUuid, characteristic);
      });
    }
    _readCharacteristicValue(characteristicUuid) {
      let characteristic = this._characteristics.get(characteristicUuid);
      return characteristic.readValue()
      .then(value => {
        // In Chrome 50+, a DataView is returned instead of an ArrayBuffer.
        value = value.buffer ? value : new DataView(value);
        return value;
      });
    }
    _writeCharacteristicValue(characteristicUuid, value) {
      let characteristic = this._characteristics.get(characteristicUuid);
      return characteristic.writeValue(value);
    }
    _startNotifications(characteristicUuid) {
      let characteristic = this._characteristics.get(characteristicUuid);
      // Returns characteristic to set up characteristicvaluechanged event
      // handlers in the resolved promise.
      return characteristic.startNotifications()
      .then(() => characteristic);
    }
    _stopNotifications(characteristicUuid) {
      let characteristic = this._characteristics.get(characteristicUuid);
      // Returns characteristic to remove characteristicvaluechanged event
      // handlers in the resolved promise.
      return characteristic.stopNotifications()
      .then(() => characteristic);
    }
  }

  window.manylabsSensor = new ManylabsSensor();

})();
