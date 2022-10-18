const searchSubmit = document.getElementById('searchSubmit');


async function performSearch(searchUrl, queryValue){
  let data = {"query_text": queryValue}
  const response = await fetch(searchUrl, {
    "method": "POST",
    "headers": {"Content-Type": "application/json"},
    "body": JSON.stringify(data)
  });
  // Populate table with data and unhide
  console.log("before response check");
  console.log(response.statusText);
  if (response.ok) {
    console.log("response was ok");
    // populate table with new data
    updateTable(await response.json())
  }
}
// populate table with new data
function updateTable(data) {
  console.log(data)
  try{
    console.log(vendorBar)
    updateCharts(data)
  }catch(ReferenceError){
    main(data)
  }
    
  
  const tbody = document.getElementById("sql_search_results_table_body");
  // clear existing data from tbody if it exists
  tbody.innerHTML = "";
  var p = "";

  // Iterate over each record in returned data and populate table
  for(var record in data) {
    // Add opening tag for row
    p += "<tr>"
    recordKeys = Object.keys(record)
    values.forEach(value => {
      p += "<td>" + record[value] + "</td>";
    })
    // Add closing tag for row
    p += "</>tr>";
  }
  // Unhide table
  document.getElementById("sql_search_results_table").style.display = '';
  tbody.insertAdjacentHTML("beforeend", p);
  }

function main(qData)  {
  var ctx1 = document.getElementById('oblBar').getContext('2d');
  const oblBar = new Chart(ctx1, {
      type: 'bar',
      data: {
          labels: abrev(qData['charts'][5]['x_values']),
          datasets: [{
              label: 'Dollars Obligated',
              data : qData['charts'][5]['y_values'],
              backgroundColor: [
                'rgba(100, 38, 103, 0.5)',
                'rgba(206, 0, 88, 0.2)',
                'rgba(237, 139, 0, 0.2)',
                'rgba(247, 234, 72, 0.2)',
                'rgba(80, 133, 144, 0.2)'
              ],
              borderColor: [
                'rgba(100, 38, 103, 0.5)',
                'rgba(206, 0, 88, 0.2)',
                'rgba(237, 139, 0, 0.2)',
                'rgba(247, 234, 72, 0.2)',
                'rgba(80, 133, 144, 0.2)'
              ],
              borderwidth: 1
          }]
      },
      options: {
        responsive: true,
        scales: {
          yAxes: [{
            ticks: {
              beginAtZero: true
            }
          }]
        }
      },
      // plugins: [{
      //   beforeInit: function (chart) {
      //     chart.data.labels.forEach(function (value, index, array) {
      //       var a = [];
      //       a.push(value.slice(0,5));
      //       var i = 1;
      //       while(value.length > (i * 6)) {
      //         a.push(value.slice(i * 6, (i+1) * 6));
      //         i++;
      //       }
      //       array[index] = a;
      //     })
      //   }
      // }]
  });

  // Add the data to these bar graphs
  var ctx3 = document.getElementById('vendorBar').getContext('2d');
  const vendorBar = new Chart(ctx3, {
    type: 'bar',
    data: {
      labels: qData['charts'][1]['x_values'].slice(0, 5),
      datasets: [{
        label: "Vendors by Unique Contracts",
        data: qData['charts'][1]['y_values'].slice(0, 5),
        backgroundColor: [
          'rgba(100, 38, 103, 0.5)',
          'rgba(206, 0, 88, 0.2)',
          'rgba(237, 139, 0, 0.2)',
          'rgba(247, 234, 72, 0.2)',
          'rgba(80, 133, 144, 0.2)'
        ],
        borderColor: [
          'rgba(100, 38, 103, 0.5)',
          'rgba(206, 0, 88, 0.2)',
          'rgba(237, 139, 0, 0.2)',
          'rgba(247, 234, 72, 0.2)',
          'rgba(80, 133, 144, 0.2)'
        ],
        borderwidth: 1
      }]
    },
    options: {
      responsive: true,
      scales: {
        yAxes: [{
          ticks: {
            beginAtZero: true
          }
        }]
      }
    }
  })
  var ctx4 = document.getElementById('naicsBar').getContext('2d');
  const naicsBar = new Chart(ctx4, {
    type: 'bar',
    data: {
      labels: qData['charts'][3]['x_values'].slice(0, 5),
      datasets: [{
        label: 'Top NAICS vendors by number of contracts',
        data: qData['charts'][3]['y_values'].slice(0, 5),
        backgroundColor: [
          'rgba(100, 38, 103, 0.5)',
          'rgba(206, 0, 88, 0.2)',
          'rgba(237, 139, 0, 0.2)',
          'rgba(247, 234, 72, 0.2)',
          'rgba(80, 133, 144, 0.2)'
        ],
        borderColor: [
          'rgba(100, 38, 103, 0.5)',
          'rgba(206, 0, 88, 0.2)',
          'rgba(237, 139, 0, 0.2)',
          'rgba(247, 234, 72, 0.2)',
          'rgba(80, 133, 144, 0.2)'
        ],
        borderwidth: 1
      }]
    },
    options: {
      // maintainAspectRatio: false,
      scales: {
        xAxes: [{
          ticks: {
              display: false
          }
        }],
        yAxes: [{
          ticks: {
            beginAtZero: true
          }
        }]
      },
      plugins: {
        legend: {
          display: false
        }
      },
      responsive: true,
      scales: {
        yAxes: [{
          ticks: {
            beginAtZero: true
          }
        }]
      },
      
    }
  })
  var ctx5 = document.getElementById('darpaLine').getContext('2d');
  const darpaLine = new Chart(ctx5, {
    type: 'line',
    data: {
      labels: qData['charts'][6]['x_values'],
      datasets: [{
        label: 'Dollars Obligated by Fiscal Year',
        data: qData['charts'][6]['y_values'],
        backgroundColor: [
          'rgba(100, 38, 103, 0.5)',
          'rgba(206, 0, 88, 0.2)',
          'rgba(237, 139, 0, 0.2)',
          'rgba(247, 234, 72, 0.2)',
          'rgba(80, 133, 144, 0.2)'
        ],
        borderColor: [
          'rgba(100, 38, 103, 0.5)',
          'rgba(206, 0, 88, 0.2)',
          'rgba(237, 139, 0, 0.2)',
          'rgba(247, 234, 72, 0.2)',
          'rgba(80, 133, 144, 0.2)'
        ],
        borderwidth: 1,
        fill: false
      }],
      options: {
        responsive: true,
        title: {
          display: true,
        }
      }
    }
  })
  var ctx8 = document.getElementById('commercialPie').getContext('2d');
  lbls = splitXandY(qData['charts'][4]['chart_data'])
  const commercialPie = new Chart(ctx8, {
    type: 'pie',
    data: {
      labels: lbls[0],
      datasets: [{
        data: lbls[1],
        backgroundColor: [
          'rgba(100, 38, 103, 0.5)',
          'rgba(206, 0, 88, 0.2)',
          'rgba(237, 139, 0, 0.2)',
          'rgba(247, 234, 72, 0.2)',
          'rgba(80, 133, 144, 0.2)'
        ],
      }],
      options: {
        title: {
          display: true,
          text: 'TEST'
        }
      },
      
    },
    
    
  })
  var ctx6 = document.getElementById('vendorTable');
  createVendorTable(qData['charts'][0]['chart_data'],ctx6)
  var ctx7 = document.getElementById('naicsTable');
  createNaicsTable(qData['charts'][2]['chart_data'], ctx7)
  
}


/*Utility Functions*/

function updateCharts(qData){
  oblBar.data.datasets.data = abrev(qData['charts'][5]['y_values'])
  vendorBar.data.datasets.data = qData['charts'][1]['y_values'];
  vendorBar.update();
  naicsBar.data.datasets.data = qData['charts'][3]['y_values']
  naicsBar.update();
  darpaLine = qData['charts'][6]['y_values']
  darpaLine.update();
  lbls = splitXandY(qData['charts'][4]['chart_data']);
  commercialPie = lbls[1];
  commercialPie.update();
}

function splitXandY(data){
  console.log(data)
  xLabels = [];
  yLabels = [];
  for(let i = 0; i < data.length; i++){
    xLabels[i] = data[i]['name'];
    yLabels[i] = data[i]['count'];
  }
  return [xLabels, yLabels];
}

function abrev(xLabels){
  const aLabels = [];
  for(let i = 0; i < xLabels.length; i++) {
    // Catches Special cases for abreviating 
    if(xLabels[i] == "DEPT OF THE ARMY"){
      aLabels[i] = "ARMY";  
    } else if(xLabels[i] == "DEPT OF THE NAVY"){
      aLabels[i] = "NAVY";
    } else if(xLabels[i] == "DEPT OF THE AIR FORCE"){
      aLabels[i] = "AIR FORCE";
    } else if(xLabels == "U.S. SPECIAL OPERATIONS COMMAND (USSOCOM)"){
      aLabels[i] = "USSOCOM";
      // Does general abriviations
    } else {
      // console.log(label)
      try{
        var abbrev = xLabels[i].replace(/\([^\)]*\)/g).match(/\b([A-Z])/g).join('')
        // console.log(allData[abbrev] == null)
        aLabels[i] = abbrev
      } catch(TypeError) {
        console.log('Done!')
      }
    }
  }
  return aLabels;
}

/*Table Functions */

function createVendorTable(data, ctx){
  
  var vendorTable = document.createElement("table"), row, sei, piid, vendor, dollars;
  ctx.appendChild(vendorTable);
  
  headers = Object.keys(data[0]);
  header = vendorTable.insertRow();
  sei = header.insertCell();
  piid = header.insertCell();
  vendor = header.insertCell();
  dollars = header.insertCell();

  sei.innerHTML = headers[0];
  piid.innerHTML = headers[1];
  vendor.innerHTML = headers[2];
  dollars.innerHTML = headers[3]; 

  for(let key in data) {
    row = vendorTable.insertRow();
    sei = row.insertCell();
    piid = row.insertCell();
    vendor = row.insertCell();
    dollars = row.insertCell();

    sei.innerHTML = data[key]['vendor_sam_entity_id'];
    piid.innerHTML = data[key]['num_piids'];
    vendor.innerHTML = data[key]['vendor_name'];
    dollars.innerHTML = data[key]['total_dollars_obligated'];

  }
}

function createNaicsTable(data, ctx){
  
  console.log(Object.keys(data[0]));
  headers = Object.keys(data[0]);
  var naicsTable = document.createElement("table"), row, desc, piid, dollars;
  ctx.appendChild(naicsTable);
  
  header = naicsTable.insertRow();
  desc = header.insertCell();
  piid = header.insertCell();
  dollars = header.insertCell();

  desc.innerHTML = headers[0];
  piid.innerHTML = headers[1];
  dollars.innerHTML = headers[2];

  for(let key in data) {
    row = naicsTable.insertRow();
    desc = row.insertCell();
    piid = row.insertCell();
    dollars = row.insertCell();

    desc.innerHTML = data[key]['naics_description'];
    piid.innerHTML = data[key]['num_piids'];
    dollars.innerHTML = data[key]['total_dollars_obligated'];
  }
}