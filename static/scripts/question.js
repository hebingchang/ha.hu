'use strict';

$(function () {
  $('.btn-vote').click(function (event) {
    var i = $('.btn-vote').toArray().indexOf(this);
    var answer_id = $($('.answer-card')[i]).attr('data-answer-id');
    var token = $($('.token')[0]).text();
    var data = {
      to_answer: answer_id,
      type: 'up',
      csrfmiddlewaretoken: csrf_token
    };
    $.post('/vote/create/', data).done(function (data) {
      $($('.vote-num')[i]).text(data.vote_num);
    });
  });

  $('.comment-btn').click(function (event) {
    var i = $('.comment-btn').toArray().indexOf(this);
    var answer_id = $($('.answer-card')[i]).attr('data-answer-id');
    var panel = $('.comment-panel')[i];
    var list = $('.comment-list')[i];
    var btn = $('.comment-btn')[i];

    if ($(panel).css('display') == 'none') {
      $.get(("/comments/"+answer_id + "/"), function(data, status) {
        $(panel).css('display', 'block');
        $(list).html(data);
        $(btn).text("Hide Comment");
      });
    } else {
      $(panel).css('display', 'none');
      $(btn).text("Show Comment");
    }
  });


  $('.comment-add-btn').click(function (event) {
    var i = $('.comment-add-btn').toArray().indexOf(this);
    var answer_id = $($('.answer-card')[i]).attr('data-answer-id');
    var content = $($('.comment-content')[i]).val();
    var list = $('.comment-list')[i];
    var btn = $('.comment-btn')[i];
    if (content === '') {
      return;
    }

    var data = {
      to_answer: answer_id,
      content: content,
      csrfmiddlewaretoken: csrf_token
    }
    $.post('/comment/create/', data, function(data, status) {
      $(list).html(data);
      $($('.comment-content')[i]).val('');
    });

  });

  $('.btn-downvote').click(function (event) {
    var i = $('.btn-downvote').toArray().indexOf(this);
    var answer_id = $($('.answer-card')[i]).attr('data-answer-id');
    var token = $($('.token')[0]).text();
    var data = {
      to_answer: answer_id,
      type: 'down',
      csrfmiddlewaretoken: csrf_token
    };
    $.post('/vote/create/', data).done(function (data) {
      $($('.vote-num')[i]).text(data.vote_num);
    });
  });

  $('#delete_question').click(function () {
    $.post('/question/delete/', {
      question_id: question_id,
      csrfmiddlewaretoken: csrf_token
    }).done(function() {
      window.location.href = '/discover';
    });
  });

  $('.delete_answer').click(function () {
    var that = this;
    $.post('/answers/delete/', {
      question_id: question_id,
      answer_id: $(that).attr('data-answer-id'),
      csrfmiddlewaretoken: csrf_token
    }).done(function() {
      window.location.reload();
    });
  });

  $('.avatar').click(function () {
    var i = $('.avatar').toArray().indexOf(this);
    var username = $($('.username')[i]).text();
    var url = '/profile/' + username;
    $( location ).attr("href", url);
  });
});
