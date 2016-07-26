'use strict';

$(function () {
  $('.btn-vote').click(function (event) {
    var i = $('.btn-vote').toArray().indexOf(this);
    var answer_id = $($('.answer-card')[i]).attr('data-answer-id');
    var token = $($('.token')[0]).text();
    var data = {
      to_answer: answer_id,
      csrfmiddlewaretoken: csrf_token
    };
    $.post('/vote/create/', data).done(function (data) {
      $($('.vote-num')[i]).text(data.vote_num);
    });
  });

  $('#delete_question').click(function () {
    $.post('/questions/delete/', {
      question_id: question_id,
      csrfmiddlewaretoken: csrf_token
    })
  });

  $('.delete_answer').click(function () {
    var that = this;
    $.post('/answers/delete/', {
      question_id: question_id,
      answer_id: $(that).attr('data-answer-id'),
      csrfmiddlewaretoken: csrf_token
    })
  })
});
