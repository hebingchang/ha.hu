var process = require('process');

if (process.env.DJANGO_CONFIG === 'production') {
  var SERVER_HOST = 'web';
  var REDIS_HOST = 'redis';
} else {
  var SERVER_HOST = '127.0.0.1';
  var REDIS_HOST = '127.0.0.1;'
}

exports.SERVER_HOST = SERVER_HOST;
exports.REDIS_HOST = REDIS_HOST;
