$(function () {
  $('.btn-vote').click(function(event) {
  	var a_id = $(event.target.parentNode.parentNode.parentNode).attr('data-answer-id');
  	console.log($('.token'));
  	var token = $('.token')[0].innerHTML;
  	console.log('Token ' + token);
  	var data = {
  		'to_answer': a_id,
  		'csrfmiddlewaretoken': token
  	};
  	$.post('/vote/create/', data);
  });
});
