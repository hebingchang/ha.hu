$(function () {
  $.get('/settings/profile', function (data) {
    var $is_login = $('#is_login');
    console.log(data.username, $is_login);
    if (typeof data.username !== 'undefined') {
      $is_login.attr('href', '/profile/' + data.username + '/');
      $is_login.text(data.username);
    } else {
      $is_login.text('Log in');
    }
  });
});
