'use strict';

$(function () {

	var maxSize = 1024 * 1024 * 2; //2 MB
    $('#img-input').change( function () {
    	if (this.files[0].size > maxSize) {
    		alert('The size of image should be smaller than 2 MB');
    		return;
    	}
    	$('#img-form').submit();
    	this.value='';
    });
});
