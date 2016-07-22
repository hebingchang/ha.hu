$(function () {
  $(".mdl-textfield__input").blur(function () {
    $(this).prop('required', true);
  });

  $(".mdl-button[type='submit']").click(function () {
    $(this).parent().siblings().children(".mdl-textfield").children(".mdl-textfield__input").prop('required', true);
  });
});
