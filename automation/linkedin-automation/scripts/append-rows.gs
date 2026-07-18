/**
 * Web App endpoint — accepts POST requests with JSON search results.
 * Deploy: Deploy → New deployment → Web app → Execute as Me → Anyone can access.
 */
function doPost(e) {
  var rows = JSON.parse(e.postData.contents);
  var sheet = SpreadsheetApp.getActiveSpreadsheet().getSheetByName('Sheet1');
  if (!sheet) {
    sheet = SpreadsheetApp.getActiveSpreadsheet().getActiveSheet();
  }

  if (sheet.getLastRow() === 0) {
    sheet.appendRow(['Name', 'Degree', 'Headline', 'Location', 'Current Job', 'Followers', 'Mutual Connections', 'Profile URL']);
  }

  rows.forEach(function(row) {
    sheet.appendRow([
      row.name || '',
      row.degree || '',
      row.headline || '',
      row.location || '',
      row.currentJob || '',
      row.followers || '',
      row.mutualConnections || '',
      row.profileUrl || ''
    ]);
  });

  return ContentService.createTextOutput('ok:' + rows.length);
}
