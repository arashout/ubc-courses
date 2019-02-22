# UBC API [![Build Status](https://travis-ci.org/arashout/ubcapi.svg?branch=master)](https://travis-ci.org/arashout/ubcapi)
## What it does:
Beautifies the lacking unofficial UBC transcript with extra information and better formatting.

## How it does this:
It does this in several ways:
1. Adding a course names columns
2. Removing unnecessary widgets
3. Spacing items out better and increasing the width of the table 
4. Allow you to manually edit course names
5. Optionally allow you to remove unnecessary columns + rows

## Instructions

1. There's a link on [**this page**](http://arashout.site/posts/improved-ubc-transcript) that you should drag onto your bookmarks bar

2. Go to your [**Grades Summary**](https://ssc.adm.ubc.ca/sscportal/servlets/SRVSSCFramework?function=SessGradeRpt) page.

3. Click the bookmark link to run!

## Output

The code gets rid of the extra tabs/average calculator app, spaces things out a little better, and aligns the table to the header. 

![After Transcript Example](./examples/After.png "After Transcript Example")

## Before Picture

This is what the transcript looked like before
![Before Transcript Example](./examples/Before.png "Before Transcript Example")

## How it works:
This application is split into 2 parts the [the bookmarklet](#Bookmarklet) and [the server](#The Server)

### Bookmarklet
- The bookmarklet is JavaScript code that runs on the user's browser to:
1. Prompts the user for input regarding what features to remove
2. Formats the page by removing unnecessary features
3. Make an GET request to the server to retrieve course names for the course codes on the grades page
4. Populates the new column called 'Course Names'

### The Server
1. Respond to GET requests from client

## Credits:
- [crclayton](https://github.com/crclayton) originally created the bookmarklet that formatted the transcript, I'm simply building off of it.
