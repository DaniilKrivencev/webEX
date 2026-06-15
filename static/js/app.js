// Delete book modal — Bootstrap 5 API
function confirmDelete(bookId, bookTitle) {
  document.getElementById('deleteBookName').textContent = bookTitle;
  document.getElementById('deleteForm').action = '/books/' + bookId + '/delete';
  var modal = new bootstrap.Modal(document.getElementById('deleteModal'));
  modal.show();
}

// Auto-dismiss flash alerts after 5s
document.querySelectorAll('.alert').forEach(function(el) {
  setTimeout(function() {
    var bsAlert = bootstrap.Alert.getOrCreateInstance(el);
    if (bsAlert) bsAlert.close();
  }, 5000);
});

// Init EasyMDE on all textarea.easymde
document.addEventListener('DOMContentLoaded', function() {
  document.querySelectorAll('textarea.easymde').forEach(function(el) {
    new EasyMDE({
      element: el,
      spellChecker: false,
      autofocus: false,
      placeholder: el.placeholder || 'Введите текст в формате Markdown...',
      toolbar: [
        'bold','italic','heading','|','quote','unordered-list','ordered-list',
        '|','link','|','preview','side-by-side','fullscreen','|','guide'
      ],
      status: ['lines','words'],
      minHeight: '200px'
    });
  });
});
