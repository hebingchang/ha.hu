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
  $('#chat-btn').click(function () {
    var url = '/chat/' + username + '/';
    $(location).attr("href", url);
  });
  $('#delete-btn').click(function () {
    var that = this;
    $.post('/accounts/deactive/', {
      target_user: username,
      csrfmiddlewaretoken: csrf_token
    }).done(function () {
      if ($.trim($(that).text()) == '注销用户') {
        $(that).text('已注销');
      } else {
        $(that).text('注销用户');
      }
    });
  })
});
