
//アンカーリンク調整
$(function () {
	var headerHight = 100;
	$('a[href^="#"]').click(function () {
		var href = $(this).attr("href");
		var target = $(href == "#" || href == "" ? "html" : href);
		var position = target.offset().top - headerHight;
		$("html, body").animate({ scrollTop: position }, 550, "swing");
		return false;
	});
});
  
  //高さ揃え
$(function(){
	$('.plans .box h3').matchHeight();
	$('.price .box p').matchHeight();
	$('.campaign dt').matchHeight();
});

//animation
document.addEventListener('DOMContentLoaded', function(){
  var trigger = new ScrollTrigger();
});

//pagetop
$(function () {
    $.scrollUp({
        scrollName: 'scrollUp', // 表示される要素のID
        topDistance: '100', // トップからどんくらいったら表示するか (px)
        topSpeed: 300, // トップに戻る速度 (ms)
        animation: 'fade', // アニメーションFade, slide, none
        animationInSpeed: 200, // 表示のアニメーションスピード (ms)
        animationOutSpeed: 200, // 消えるアニメーションスピード (ms)
        scrollText: '<img src="https://dev3.osoujihonpo.com/assets/images/kajitatsu/top/arrow_up.svg">', // テキスト
    });
});

//faq
$(function(){
	var openClassName = 'is-open';
	$('.faq dt').click(function(){
		$(this).next('.faq dd').slideToggle();
		$(this).toggleClass(openClassName);
	});
});


//個別のアニメーション
jQuery(function ($) {
  var fadeIn = $('.fade-in');
  $(window).on('scroll', function () {
    $(fadeIn).each(function () {
      var offset = $(this).offset().top;
      var scroll = $(window).scrollTop(); 
      var windowHeight = $(window).height();
      if (scroll > offset - windowHeight + 50) {
        $(this).addClass("scroll-in");
      }
    });
  });
});