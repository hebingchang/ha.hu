$(function () {
  $(".mdl-textfield__input").blur(function () {
    $(this).prop('required', true);
    $(this).parent().addClass('is-invalid');
  });

  $(".mdl-button[type='submit']").click(function () {
    $(this).parent().siblings().children(".mdl-textfield").addClass('is-invalid');
    $(this).parent().siblings().children(".mdl-textfield").children(".mdl-textfield__input").prop('required', true);
  });
});
