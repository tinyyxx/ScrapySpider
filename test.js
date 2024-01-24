function generateLabel($) {
  'use strict';

  const accountIdMap = {
    'matthew@mxcsneaker.com': '8841',
  }

  const currentAccount = $('body > nav > div > div.navbar-header > a').text().match(/\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b/g);
  const accountId = accountIdMap[currentAccount[0]];

  if (!currentAccount || !accountId) {
    alert('找不到当前账号对应的账号ID');
    return;
  }


  $('table tr').each(function(index) {
    if (index <= 1) { return; }
    const printIcon = $('<span>').addClass('glyphicon glyphicon-print');
    printIcon.click(function() {
      const clickedRow = $(this).closest('tr');
      const rowData = [];
      clickedRow.find('td').each(function() {
        rowData.push($(this).text());
      });

      print(rowData);
    });

    $(this).find('td:last').append(printIcon);

  });

  function print(rowData){
    $('body').append(
      $('<div>').attr('id', 'mxc-kc-label').append(
        $('<div>').css('display', 'flex').append(
          $('<div>').attr('id', 'mxc-kc-qrcode').css({'width': '100px', 'height': 'auto'}),
          $('<div>').append(
            $('<div>').css('height', '50px').text(`ORDER_NO: ${rowData[1]}`),
            $('<div>').text(`ITEM_NO: ${rowData[8]}`)
          )
        ),
        $('<div>').css('display', 'flex').append(
          $('<div>').css('width', '100px').text(accountId),
          $('<div>').text(`SIZE:US ${rowData[10]}`)
        ),
        // '24-2-172'
      )
    );

    $('#mxc-kc-qrcode').qrcode({width: 80,height: 80,text: `HYO${rowData[1]}`});

    printJS('mxc-kc-label','html')

    $('#label').remove();

  }

}
