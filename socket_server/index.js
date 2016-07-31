var http = require('http');
var server = http.createServer();
var io = require('socket.io')(server);
var redis = require('node-redis');
var request = require('request');
var cookie = require('cookie');
var process = require('process');

var config = require('./config');

var sockets = {};

var sub = redis.createClient({
  host: config.REDIS_HOST,
  port: 6379,
  db: 2
});

sub.on('message', function(channel, message) {
  console.log(channel, message);
  message = message.toString();
  if (sockets[channel]) {
    sockets[channel].emit('data', message);
  }
});

io.on('connection', function(socket) {
  var cookies = cookie.parse(socket.handshake.headers.cookie);
  if (sockets[cookies.sessionid]) {
    console.log('Existed');
  } else {
    console.log('New');

    sub.subscribe(cookies.sessionid);
  }

  sockets[cookies.sessionid] = socket

  socket.on('data', function(data) {
    console.log(data);
    var url = 'http://' + config.SERVER_HOST + ':' + config.SERVER_PORT + '/socket_api/';
    data.session_id = cookies.sessionid
    request.get({
      url: url,
      qs: data
    }, function(err, data) {
      if (err) {
        console.error(err);
      }
    });
  });
});

server.listen(4000);
