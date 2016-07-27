'use strict';

$(function () {
  $('#img-input').change( function () {
     $('#img-form').submit();
     this.value='';
  });
});
