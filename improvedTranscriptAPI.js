var COL_INDEX = Object.freeze({
    COURSE_CODE: 0,
    LETTER_GRADE: 3,
    STANDING: 10
});

function replaceNbsps(str) {
  var re = new RegExp(String.fromCharCode(160), 'g');
  return str.replace(re, ' ');
}

function httpGetAsync(theUrl, element, callback)
{
    var xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
            callback(xmlHttp.responseText, element);
    }
    xmlHttp.open("GET", theUrl, true); // true for asynchronous 
    xmlHttp.send(null);
}

function changeElementFromResponse(responseContent, element){
    var responseObject = JSON.parse(responseContent);
    var courseName = responseObject['name'];
    if(courseName !== undefined){
        element['innerText'] = courseName;
    }
}

function formatGradeSummary(){
    var iframe = document.querySelector('#iframe-main').contentWindow.document;
    // CREDIT: Original formatting code is from
    // https://github.com/crclayton
    // https://github.com/crclayton/ubc-unofficial-transcript-exporter

    // remove page clutter
    [ '#UbcHeaderWrapper', 
    '#UbcBottomInfoWrapper',
    '#UbcUtilNavWrapper'].forEach(function(n){
        document.querySelector(n).remove();
    });

    // remove calculator and semester navigator
    [ '#calculator_title', 
    '#calculator_title_text', 
    '.ui-tabs-nav'].forEach(function(n){
        iframe.querySelector(n).remove();
    });

    // space things out a bit better 
    iframe.querySelector('h1').style = 'margin:10px 0 -20px 70px;'
    iframe.querySelector('#header-invisible img').style = 'margin-bottom: 15px;'

    // center table and set to width of UBC header image 
    iframe.querySelector('#tabs').style = 'margin: 0px auto; width:800px';
    return iframe;
}

var iframe = formatGradeSummary();

var tableElement = iframe.getElementById('allSessionsGrades');
var tableBody = tableElement.children[0];
var tableRows = tableBody.children;
var n = tableRows.length;

var root = "https://jsonplaceholder.typicode.com";
var urlWithoutNumber = root + '/users/';

for(var i = tableRows.length - 1; i >= 0; i--){
    var row = tableRows[i];
    row.removeChild(row.children[COL_INDEX.STANDING]);
    var courseCode = replaceNbsps(row.children[COL_INDEX.COURSE_CODE].innerText);
    var letterGrade = row.children[COL_INDEX.LETTER_GRADE].innerText;
    if(letterGrade === ''){
        tableBody.removeChild(row);
    }
    else{
        var entry = row.insertCell(1);
        entry.style.textAlign = 'center';
        if(i === 0){
            entry.innerText = 'Course Name';
            entry.classList.add('listHeader');
        }
        else{
            httpGetAsync(urlWithoutNumber + (i - 10), entry, changeElementFromResponse);
            entry.classList.add('listRow');
        }
    }
}

iframe.querySelector('#printer').click();