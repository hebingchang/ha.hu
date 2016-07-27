'use strict';

$(function () {
  Vue.config.delimiters = ['$$', '$$'];
  Vue.config.unsafeDelimiters = ['$$$', '$$$'];
  var vm = new Vue({
    el: '#container',
    data: {
      feeds: [],
      is_signed: null,
      cur_user: null
    }
  });

  $.get('/index_feeds/').done(function (data) {
    vm.feeds = vm.feeds.concat(data['feeds']);
    vm.$set('is_signed', data['is_signed']);
    vm.$set('cur_user', data['cur_user']);
  });

  $('#sign-btn').click(function () {
    var self = this;
    $.post('/accounts/sign/', {
      username: $(self).attr('data-username'),
      csrfmiddlewaretoken: csrf_token
    }).done(function () {
      $(self).parent().append("<span>您今天已经签过到了...</span>");
      $(self).remove();
    })
  })
});
