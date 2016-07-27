'use strict';

$(function () {
  Vue.config.delimiters = ['$$', '$$'];
  Vue.config.unsafeDelimiters = ['$$$', '$$$'];
  var vm = new Vue({
    el: '#feed-stream',
    data: {
      feeds: []
    }
  });

  $.ajax({
    url: '/index_feeds/',
    type: 'GET',
    async: true,
    success: function (data) {
      vm.feeds = vm.feeds.concat(data['feeds']);
      console.log(vm.feeds);
    }
  });
});
