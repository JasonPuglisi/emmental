/* Signup functions */

function toggleSignup() {
  if (!$('.signup-button').hasClass('active')) {
    if ($('.login-button').hasClass('active')) {
      hideLogin();
    }

    showSignup();
  } else {
    hideSignup();
  }
}

function showSignup() {
  $('.signup-button').addClass('active');
  $('.signup-form').removeClass('hidden');
}

function hideSignup() {
  $('.signup-button').removeClass('active');
  $('.signup-form').addClass('hidden');
}

function submitSignup() {
  $('.signup-form').submit();
}

/* Login functions */

function toggleLogin() {
  if (!$('.login-button').hasClass('active')) {
    if ($('.signup-button').hasClass('active')) {
      hideSignup();
    }

    showLogin();
  } else {
    hideLogin();
  }
}

function showLogin() {
  $('.login-button').addClass('active');
  $('.login-form').removeClass('hidden');
}

function hideLogin() {
  $('.login-button').removeClass('active');
  $('.login-form').addClass('hidden');
}

function submitLogin() {
  $('.login-form').submit();
}
