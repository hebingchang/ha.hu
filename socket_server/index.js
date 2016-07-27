var express = require('express');

var app = express();
var http = require('http');
var server = require('http').Server(app);
var io = require('socket.io')(server);
var redis = require('node-redis');
var request = require('request');
var cookie = require('cookie');

var sub = redis.createClient({
  host: '127.0.0.1',
  port: 6379,
  db: 2
});

io.on('connection', function(socket) {
  var cookies = cookie.parse(socket.handshake.headers.cookie);

  sub.on('message', function(channel, message) {
    if (channel === 'data_' + cookies.sessionid) {
      console.log(message);
      socket.emit(message);
    }
  });

  sub.subscribe('data_' + cookies.sessionid);

  socket.on('data', function(data) {
    var url = 'http://localhost:8000/socket_api/';

    request.get({
      url: url,
      qs: {
        data: data,
        session_id: cookies.sessionid
      }
    });
  });
});

server.listen(4000);
