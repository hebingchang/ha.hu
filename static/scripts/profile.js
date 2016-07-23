/**
 * Created by tianyizhuang on 7/23/16.
 */

'use strict';

$(function() {
  $('#follow-btn').click(function (event) {
    var that = this;
    $.post('/follow/', {
      to_user: username,
      csrfmiddlewaretoken: csrf_token
    }).done(function(data) {
      console.log(data);
      $(that).text('已关注');
    });
  });
});
