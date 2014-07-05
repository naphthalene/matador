jQuery(document).ready(function($) {
  $(".clickableRow").click(function() {
    window.document.location = $(this).attr("href");
  });
  $('select').selectpicker();
  $('#player_suggest').magicSuggest(
    {
      maxSelection: 1,
      allowFreeEntries: 'false',
      selectionPosition: 'right',
      selectionStacked: 'true',
      id: 'player_suggest',
      name: 'player_suggest',
      data: '/player_suggest/',
      emptyText: 'Select Player',
    }
  );

});
