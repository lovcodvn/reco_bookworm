$(function() {
  // Button will be disabled until we type something inside the input field
  const source = document.getElementById('autoComplete');
  const inputHandler = function(e) {
    if(e.target.value==""){
      $('.book-button').attr('disabled', false);
    }
    else{
      $('.book-button').attr('disabled', false);
    }
  }
  source.addEventListener('input', inputHandler);

  $('.fa-arrow-up').click(function(){
    $('html, body').animate({scrollTop:0}, 'slow');
  });

  $('.app-title').click(function(){
    window.location.href = '/';
  })

  $('.book-button').on('click',function(){
    var title = $('.book').val();
    var user = document.getElementById('user').value
//    var genre = 'happy'
    var e = document.getElementById('dropdown');
    var genre = e.options[e.selectedIndex].value;


//    if (title=="") {
//      $('.results').css('display','none');
//      $('.fail').css('display','block');
//    }

    if (($('.fail').text() && ($('.footer').css('position') == 'absolute'))) {
      $('.footer').css('position', 'fixed');
    }
    else{
        $("#loader").fadeIn();
        parse_title(title, user, genre);
    }
  });
});

// will be invoked when clicking on the recommended book cards
function recommendcard(e){
  $("#loader").fadeIn();
  var user = $('.user').val();
  var title = e.getAttribute('title');
//  var genre = 'happy'
  var e = document.getElementById('dropdown');
  var genre = e.options[e.selectedIndex].value;
  parse_title(title, user, genre);
}


// passing title detail to python's flask for displaying
function parse_title(book_title, user, genre){
  details = {
      'title':book_title,
      'user' : user,
      'genre': genre
  }

  $.ajax({
    type:'POST',
    data:details,
    url:"/recommend",
    dataType: 'html',
    complete: function(){
      $("#loader").delay(500).fadeOut();
    },
    success: function(response) {
      $('.results').html(response);
      $('#autoComplete').val('');
      $('.footer').css('position','absolute');
      if ($('.book-content')) {
        $('.book-content').after('<div class="gototop"><i title="Go to Top" class="fa fa-arrow-up"></i></div>');
      }
      $(window).scrollTop(0);
    }
  });
}


//function myFunction() {
//  document.getElementById("myDropdown").classList.toggle("show");
//}
//
//// Close the dropdown menu if the user clicks outside of it
//window.onclick = function(event) {
//  if (!event.target.matches('.dropbtn')) {
//    var dropdowns = document.getElementsByClassName("dropdown-content");
//    var i;
//    for (i = 0; i < dropdowns.length; i++) {
//      var openDropdown = dropdowns[i];
//      if (openDropdown.classList.contains('show')) {
//        openDropdown.classList.remove('show');
//      }
//    }
//  }
//}