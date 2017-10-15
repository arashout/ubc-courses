const COL_INDEX = Object.freeze({
    COURSE_CODE: 0,
    LETTER_GRADE: 3,
    STANDING: 10
});

function replaceNbsps(str) {
  const re = new RegExp(String.fromCharCode(160), 'g');
  return str.replace(re, ' ');
}

function httpGetAsync(url, callback)
{
    let xmlHttp = new XMLHttpRequest();
    xmlHttp.onreadystatechange = function() { 
        if (xmlHttp.readyState == 4 && xmlHttp.status == 200)
            callback(xmlHttp.responseText);
    }
    xmlHttp.open('GET', url, true); // true for asynchronous 
    xmlHttp.send(null);
}

/**
 * Ridiculous name! Function that returns a callback function for changing the entry element to the course name
 * @param {*} element 
 */
function createChangeCourseNameCallback(element){
    return function(response){
        let course = JSON.parse(response);
        if(course['name'] !== undefined){
            element['innerText'] = course['name'];
        }
        else{
            console.log(response);
            console.log(course);
        }
    }
}

function formatGradeSummary(iframeElement){
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
        iframeElement.querySelector(n).remove();
    });

    // space things out a bit better 
    iframeElement.querySelector('h1').style = 'margin:10px 0 -20px 70px;'
    iframeElement.querySelector('#header-invisible img').style = 'margin-bottom: 15px;'

    // center table and set to width of UBC header image 
    iframeElement.querySelector('#tabs').style = 'margin: 0px auto; width:800px';
}

let iframe = document.querySelector('#iframe-main').contentWindow.document;
formatGradeSummary();

const tableElement = iframe.getElementById('allSessionsGrades');
const tableBody = tableElement.children[0];
const tableRows = tableBody.children;
const n = tableRows.length;

var rootAPIUrl = 'https://arashout.pythonanywhere.com/course/api/v1.0/code/';

for(let i = tableRows.length - 1; i >= 0; i--){
    let row = tableRows[i];
    row.removeChild(row.children[COL_INDEX.STANDING]);
    let courseCode = replaceNbsps(row.children[COL_INDEX.COURSE_CODE].innerText);
    let letterGrade = row.children[COL_INDEX.LETTER_GRADE].innerText;
    if(letterGrade === ''){
        tableBody.removeChild(row);
    }
    else{
        let entry = row.insertCell(1);
        entry.style.textAlign = 'center';
        if(i === 0){
            entry.innerText = 'Course Name';
            entry.classList.add('listHeader');
        }
        else{
            let apiURL = rootAPIUrl + courseCode;
            httpGetAsync(apiURL, createChangeCourseNameCallback(entry));
            entry.classList.add('listRow');
        }
    }
}