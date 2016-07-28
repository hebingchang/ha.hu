var express = require('express');

var app = express();
var http = require('http');
var server = require('http').Server(app);
var io = require('socket.io')(server);
var redis = require('node-redis');
var request = require('request');
var cookie = require('cookie');

var sockets = {}

var sub = redis.createClient({
  host: '127.0.0.1',
  port: 6379,
  db: 2
});

sub.on('message', function(channel, message) {
  message = message.toString();
  console.log(channel, message);
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
    var url = 'http://localhost:8000/socket_api/';
    data.session_id = cookies.sessionid
    request.get({
      url: url,
      qs: data
    });
  });
});

server.listen(4000);
