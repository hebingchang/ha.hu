var process = require('process');

if (process.env.DJANGO_CONFIG === 'production') {
  var SERVER_HOST = 'nginx';
  var SERVER_PORT = 80;
  var REDIS_HOST = 'redis';
} else {
  var SERVER_HOST = '127.0.0.1';
  var SERVER_PORT = 8000;
  var REDIS_HOST = '127.0.0.1'
}

exports.SERVER_HOST = SERVER_HOST;
exports.SERVER_PORT = SERVER_PORT;
exports.REDIS_HOST = REDIS_HOST;
