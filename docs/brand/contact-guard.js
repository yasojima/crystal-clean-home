document.addEventListener('submit', function(event) {
  if (event.target.matches('[data-contact-unconfigured]')) {
    event.preventDefault();
    event.stopImmediatePropagation();
    alert('お問い合わせの送信先は準備中です。現在、このフォームからは送信できません。');
  }
}, true);
const nativeSubmit = HTMLFormElement.prototype.submit;
HTMLFormElement.prototype.submit = function() {
  if (this.matches('[data-contact-unconfigured]')) {
    alert('お問い合わせの送信先は準備中です。現在、このフォームからは送信できません。');
    return;
  }
  return nativeSubmit.call(this);
};
