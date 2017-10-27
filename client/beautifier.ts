interface CourseMap {
    [key: string]: string;
}

const VERSION = '1.1';
const VERSION_KEY = 'version_key';
const URL_SOURCE = 'http://arashout.site/posts/improved-ubc-transcript';

const COL_INDEX_RETRIEVAL = Object.freeze({
    COURSE_CODE: 0,
    LETTER_GRADE: 3,
});
const COL_INDEX_REMOVAL = Object.freeze({
    SECTION: 1,
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

// Reverse loop so that we can remove rows during iteration
for (let i = tableRows.length - 1; i >= 0; i--) {
    let row = <HTMLTableRowElement>tableRows[i];

    // If there is no letter grade than remove the row and move to the next iteration!
    const cellLetterGrade = <HTMLElement>row.children[COL_INDEX_RETRIEVAL.LETTER_GRADE];
    const letterGrade = cellLetterGrade.innerText;
    if (letterGrade === '') {
        tableBody.removeChild(row);
        continue;
    }

    // Collect course names to send via HTTP request
    // Add a new column for the course name
    const cellCourseCode = <HTMLTableCellElement>row.children[COL_INDEX_RETRIEVAL.COURSE_CODE];
    const courseCode = replaceNbsps(cellCourseCode.innerText);
    // If statement is for getting rid of fluff
    if(courseCode !== '' && courseCode !== 'Course'){
        courseList.push(courseCode);
    }
    

    // Remove useless columns
    row.removeChild(row.children[COL_INDEX_REMOVAL.STANDING]);
    row.removeChild(row.children[COL_INDEX_REMOVAL.SECTION]);

    let cellCourseName = row.insertCell(1);
    cellCourseName.style.textAlign = 'center';
    if (i === 0) {
        cellCourseName.innerText = 'Course Name';
        cellCourseName.classList.add('listHeader');
    }
    else {
        cellCourseName.id = courseCode
        cellCourseName.classList.add('listRow');
    }
}

// Build API endpoint with params
let queryString = '';
for (let i = 0; i < courseList.length; i++) {
    const courseCode = courseList[i];
    queryString += `c${i}=${courseCode}&`;
}
queryString += `${VERSION_KEY}=${VERSION}`

const apiEndpoint = 'https://arashout.pythonanywhere.com/courses';
const completeURL = apiEndpoint + '?' + queryString;

fetch(completeURL, {
    method: 'GET',
    headers: {
        'Accept': 'application/json, text/plain, */*',
        'Content-Type': 'application/json'
    },
    mode: 'cors',
})
.then( (response: Response) => {
    return response.json() 
})
.catch( (reason: string) => {
    console.log(reason);
})
.then( (courseMap: CourseMap) => {
    if(courseMap[VERSION_KEY] !== VERSION){
        alert(`
        You do not have the latest version of the bookmarklet which means it may not
        work properly or you may be missing new features.\n
        Get the latest version from:\n${URL_SOURCE}\n\n
        Version: ${VERSION}\tNewest Version: ${courseMap[VERSION_KEY]}
        `);
    }

    courseList.forEach( (courseCode: string) => {
        const cellCourseName = <HTMLTableCellElement>iframe.getElementById(courseCode);
        cellCourseName.contentEditable = 'true';
        cellCourseName.innerText = courseMap[courseCode];
    });
});