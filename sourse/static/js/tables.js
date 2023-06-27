window.addEventListener('DOMContentLoaded', function () {
  var tableContainer = document.querySelector('.table-container');
  var isMouseDown = false;
  var startX;
  var scrollLeft;

  tableContainer.addEventListener('mousedown', function (e) {
    isMouseDown = true;
    startX = e.pageX - tableContainer.offsetLeft;
    scrollLeft = tableContainer.scrollLeft;
  });

  tableContainer.addEventListener('mouseleave', function () {
    isMouseDown = false;
  });

  tableContainer.addEventListener('mouseup', function () {
    isMouseDown = false;
  });

  tableContainer.addEventListener('mousemove', function (e) {
    if (!isMouseDown) return;
    e.preventDefault();
    var x = e.pageX - tableContainer.offsetLeft;
    var walk = (x - startX) * 1.5; // adjust scrolling speed here
    tableContainer.scrollLeft = scrollLeft - walk;
  });
});