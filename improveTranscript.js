iframe = document.querySelector("#iframe-main").contentWindow.document;

// remove page clutter
[ "#UbcHeaderWrapper", 
  "#UbcBottomInfoWrapper",
  "#UbcUtilNavWrapper"].forEach(function(n){
    document.querySelector(n).remove();
});

// remove calculator and semester navigator
[ "#calculator_title", 
  "#calculator_title_text", 
  ".ui-tabs-nav"].forEach(function(n){
    iframe.querySelector(n).remove();
});

// space things out a bit better 
iframe.querySelector("h1").style = "margin:10px 0 -20px 70px;"
iframe.querySelector("#header-invisible img").style = "margin-bottom: 15px;"

 // center table and set to width of UBC header image 
iframe.querySelector("#tabs").style = "margin: 0px auto; width:590px";

//iframe.querySelector("#printer").click();

var tableElement = iframe.getElementById('allSessionsGrades');
var tableRows = tableElement.children[0].children;
var n = tableRows.length;
for(var i = 0; i < n; i++){
    var row = tableRows[i];
    var entry = row.insertCell(1);
    console.log(i);
    if(i === 0){
        entry.innerText = 'Course Name';
    }
    else{
        entry.innerText = 'Applied Linear Algebra';
    }
    
}
