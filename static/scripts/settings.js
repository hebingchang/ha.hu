'use strict';

$(function () {
  $('#uploadBtn').change(function () {
    $('#uploadFile').val(this.files[0].name);
  });
});
