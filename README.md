# ImprovedUBCTranscript
Bookmarklet that builds on top of [crclayton](https://github.com/crclayton) bookmarklet to improve the unofficial UBC Transcript.

It does this in three ways:
1. Adding a course names columns (Main thing missing from crclayton awesome bookmarklet)
2. Removing unnecessary widgets (calculator), columns (I didn't think the standing column added much information)
3. Spacing items out better and increasing the width of the table (It will appear as if some columns are cut-off but it looks fine in the print preview)

## Instructions FROM [crclayton's github](https://github.com/crclayton/ubc-unofficial-transcript-exporter)

1. There's a link on [**this page**]() that you should drag onto your bookmarks bar. <sup><sup>Sorry for the redirect, I can't embed bookmarklets on GitHub</sup></sup>

2. Go to your [**Grades Summary**](https://ssc.adm.ubc.ca/sscportal/servlets/SRVSSCFramework?function=SessGradeRpt) page.

3. Click the bookmark link to run!

## Output

The code gets rid of the extra tabs/average calculator app, spaces things out a little better, and aligns the table to the header. 

![](./Comparison.png "Logo Title Text 1")

### Known Issues:
Some older courses that no longer exist will have empty course name columns. 
The only fix for this is to manually add the names yourself by editing the html.
