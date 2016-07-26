'use strict';

$(function () {
  $('#follow-btn').click(function () {
    var that = this;
    $.post('/follow/', {
      to_user: username,
      csrfmiddlewaretoken: csrf_token
    }).done(function () {
      if ($.trim($(that).text()) == '关注') {
        $(that).text('已关注');
      } else {
        $(that).text('关注');
      }
    });
  });
});
