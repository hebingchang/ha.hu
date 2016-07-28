'use strict';

$(function () {
  var socket = io('http://localhost:4000/');

  Vue.config.delimiters = ['$$', '$$'];
  Vue.config.unsafeDelimiters = ['$$$', '$$$'];
  var vm = new Vue({
    el: '#message-box',
    data: {
      messages: []
    }
  });

  socket.on('data', function (data) {
    console.log(data);
  });

  $('#form-id').submit(function (e) {
    e.preventDefault();
    var $id_message = $('#id_message');
    var msg = $(this).serialize().split('=')[1];
    var url = window.location.href.split('/');
    url.pop();
    var to_user = url.pop();
    if (msg !== '') {
      vm.messages.push({message: msg, type: 'post'});
      socket.emit('data', {
        msg: msg,
        to_user: to_user
      })
    }
    $id_message.val(null);
    $id_message.parent().removeClass('is-dirty');
  })
});
