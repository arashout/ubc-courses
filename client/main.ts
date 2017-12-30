/**
 * Calculate a 32 bit FNV-1a hash
 * Found here: https://gist.github.com/vaiorabbit/5657561
 * Ref.: http://isthe.com/chongo/tech/comp/fnv/
 *
 * @param {string} message the input value
 * @param {boolean} [asString=false] set to true to return the hash value as 
 *     8-digit hex string instead of an integer
 * @param {integer} [seed] optionally pass the hash of the previous chunk
 * @returns {integer | string}
 */
function hashFnv32a(message: string, seed = 0x811c9dc5): string {
    let hval = seed;
    for (let i = 0, l = message.length; i < l; i++) {
        hval ^= message.charCodeAt(i);
        hval += (hval << 1) + (hval << 4) + (hval << 7) + (hval << 8) + (hval << 24);
    }
    // Convert to 8 digit hex string
    return ("0000000" + (hval >>> 0).toString(16)).substr(-8);
}

interface CourseMap {
    [key: string]: string;
};
interface UserChoice {
    removeNoGradeRow: boolean;
    removeSectionColumn: boolean;
    removeStandingColumn: boolean;
};

const VERSION = '1.2';
const VERSION_KEY = 'version_key';
const DIGEST_KEY = 'digest_key';
const URL_SOURCE = 'http://arashout.site/posts/improved-ubc-transcript';

const COL_INDEX_RETRIEVAL = Object.freeze({
    COURSE_CODE: 0,
    LETTER_GRADE: 3,
});
const COL_INDEX_REMOVAL = Object.freeze({
    SECTION: 1,
    STANDING: 10
});
const BIT_FLAGS = Object.freeze({
    KEEP_NO_GRADE_ROW: 1, // 001
    KEEP_SECTION_COLUMN: 2, // 010
    KEEP_STANDING_COLUMN: 4, // 100
})

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

function getUserChoice(bitmask: number): UserChoice {
    return {
        removeNoGradeRow: !(bitmask & BIT_FLAGS.KEEP_NO_GRADE_ROW),
        removeSectionColumn: !(bitmask & BIT_FLAGS.KEEP_SECTION_COLUMN),
        removeStandingColumn: !(bitmask & BIT_FLAGS.KEEP_STANDING_COLUMN),
    }
}

const iframe = (<HTMLIFrameElement>document.querySelector('#iframe-main')).contentWindow.document;
formatGradeSummary(iframe);

const tableElement = <HTMLTableElement>iframe.querySelector('#allSessionsGrades');
const tableBody = tableElement.children[0];
const tableRows = tableBody.children;

let courseList: string[] = [];

// Get user input about what features they want
const promptMessage = `
    001: Keep courses with no grades\n
    010: Keep the section column\n
    100: Keep the standing column\n
    0: Default behaviour (Remove all clutter)\n
    e.g Type 011 to enable the first 2 options
    `;
const bitmaskString = <string>prompt(promptMessage, '0');
const bitmask = parseInt(bitmaskString, 2);
const userChoice = getUserChoice(bitmask);

// Reverse loop so that we can remove rows during iteration
for (let i = tableRows.length - 1; i >= 0; i--) {
    const row = <HTMLTableRowElement>tableRows[i];

    // If there is no letter grade than remove the row and move to the next iteration!
    const cellLetterGrade = <HTMLElement>row.children[COL_INDEX_RETRIEVAL.LETTER_GRADE];
    const letterGrade = cellLetterGrade.innerText;
    if (userChoice.removeNoGradeRow && letterGrade === '') {
        tableBody.removeChild(row);
        continue;
    }

    // Collect course names to send via HTTP request
    // Add a new column for the course name
    const cellCourseCode = <HTMLTableCellElement>row.children[COL_INDEX_RETRIEVAL.COURSE_CODE];
    const courseCode = replaceNbsps(cellCourseCode.innerText);
    // If statement is for getting rid of fluff
    if (courseCode !== '' && courseCode !== 'Course') {
        courseList.push(courseCode);
    }

    // Remove useless columns
    // Remove higher index first to avoid indexing problems
    if (userChoice.removeStandingColumn) { row.removeChild(row.children[COL_INDEX_REMOVAL.STANDING]); }
    if (userChoice.removeSectionColumn) { row.removeChild(row.children[COL_INDEX_REMOVAL.SECTION]); }

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
queryString += `${VERSION_KEY}=${VERSION}&`

// Create a unique digest for each user without (Avoid use of student number)
const digest = hashFnv32a(courseList.join());
queryString += `${DIGEST_KEY}=${digest}`;

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
    .then((response: Response) => {
        return response.json()
    })
    .catch((reason: string) => {
        console.log(reason);
    })
    .then((courseMap: CourseMap) => {
        if (courseMap[VERSION_KEY] !== VERSION) {
            alert(`
        You do not have the latest version of the bookmarklet which means it may not
        work properly or you may be missing new features.\n
        Get the latest version from:\n${URL_SOURCE}\n\n
        Version: ${VERSION}\tNewest Version: ${courseMap[VERSION_KEY]}
        `);
        }

        courseList.forEach((courseCode: string) => {
            const cellCourseName = <HTMLTableCellElement>iframe.getElementById(courseCode);
            cellCourseName.contentEditable = 'true';
            cellCourseName.innerText = courseMap[courseCode];
        });
    });