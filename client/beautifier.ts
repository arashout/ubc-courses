// Column indexes of those that matter
const COL_INDEX = Object.freeze({
    COURSE_CODE: 0,
    LETTER_GRADE: 3,
    STANDING: 10
});

// Replace the HTML space character thing with empty string
function replaceNbsps(str: string): string {
    const re = new RegExp(String.fromCharCode(160), 'g');
    return str.replace(re, '');
}

function formatGradeSummary(iframeDocument: Document): void {
    // CREDIT: Original formatting code is from
    // https://github.com/crclayton
    // https://github.com/crclayton/ubc-unofficial-transcript-exporter

    // remove page clutter
    ['#UbcHeaderWrapper',
        '#UbcBottomInfoWrapper',
        '#UbcUtilNavWrapper'].forEach(function (n) {
            document.querySelector(n)!.remove();
        });

    // remove calculator and semester navigator
    ['#calculator_title',
        '#calculator_title_text',
        '.ui-tabs-nav'].forEach(function (n) {
            iframeDocument.querySelector(n)!.remove();
        });

    // space things out a bit better 
    iframeDocument.querySelector('h1')!.setAttribute('style', 'margin:10px 0 -20px 70px;');
    iframeDocument.querySelector('#header-invisible img')!.setAttribute('style', 'margin-bottom: 15px;');

    // center table and set to width of UBC header image 
    iframeDocument.querySelector('#tabs')!.setAttribute('style', 'margin: 0px auto; width:800px');
}

const iframe = (<HTMLIFrameElement>document.querySelector('#iframe-main')).contentWindow.document;
formatGradeSummary(iframe);

const tableElement = <HTMLTableElement>iframe.querySelector('#allSessionsGrades');
const tableBody = tableElement.children[0];
const tableRows = tableBody.children;
const n = tableRows.length;

let courseList: string[] = [];
let courseCellMap: Map<string, HTMLTableCellElement> = new Map();

// Reverse loop so that we can remove rows during iteration
for (let i = tableRows.length - 1; i >= 0; i--) {
    let row = <HTMLTableRowElement>tableRows[i];
    // Remove useless columns
    row.removeChild(row.children[COL_INDEX.STANDING]);
    // If there is no letter grade than remove the row and move to the next iteration!
    const cellLetterGrade = <HTMLElement>row.children[COL_INDEX.LETTER_GRADE];
    const letterGrade = cellLetterGrade.innerText;
    if (letterGrade === '') {
        tableBody.removeChild(row);
        continue;
    }

    // Collect course names to send via HTTP request
    // Add a new column for the course name
    const cellCourseCode = <HTMLTableCellElement>row.children[COL_INDEX.COURSE_CODE];
    const courseCode = replaceNbsps(cellCourseCode.innerText);
    courseList.push(courseCode);

    let cellCourseName = row.insertCell(1);
    cellCourseName.style.textAlign = 'center';
    if (i === 0) {
        cellCourseName.innerText = 'Course Name';
        cellCourseName.classList.add('listHeader');
    }
    else {
        cellCourseName.id = courseCode
        courseCellMap.set(courseCode, cellCourseCode);
        cellCourseName.classList.add('listRow');
    }
}

const apiEndpoint = 'https://ubacpi.herokuapp.com/courses';

let completeURL = apiEndpoint + '?';
for (let i = 0; i < courseList.length; i++) {
    const courseCode = courseList[i];
    // If statement is for getting rid of fluff
    if(courseCode !== '' && courseCode !== 'Course'){
        completeURL += `c${i}=${courseCode}&`;
    }
}

fetch(completeURL, {
    method: 'GET',
    headers: {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json'
    },
    mode: 'cors',
})
.then( (response: Response) => {
    console.log(JSON.parse(response.toString()));
    return response.json() 
})
.catch( (reason: string) => {
    console.log(reason);
})
.then( (obj: any) => {
    console.log(obj);
});

// FOR Debugging
courseCellMap.forEach( (cell, courseCode) => {
    cell.innerText = courseCode;
});

// TODO: Loop over keys of response
