package main

import (
	"encoding/json"
	"fmt"
	"log"
	"net/http"
)

// Index just shows that the site is online
func Index(w http.ResponseWriter, r *http.Request) {
	version := "1.0"
	fmt.Fprintf(w, "<h1> UBC API is ONLINE<h1><h2>Version: %s<h2>", version)
}

// GetCourses is the endpoint for getting multiple course via query parameters
func GetCourses(w http.ResponseWriter, r *http.Request) {
	courses := make([]Course, 0)

	values := r.URL.Query()
	for k := range values {
		courseCode := values.Get(k)
		course, err := RetrieveCourse(courseCode)
		if err == nil {
			courses = append(courses, course)
		} else {
			log.Println(err.Error())
		}
	}

	if len(courses) != 0 {
		if err := json.NewEncoder(w).Encode(courses); err != nil {
			w.WriteHeader(http.StatusInternalServerError)
			log.Fatalf("Cannot marshal JSON: %s", err.Error())
			return
		}
	}
}
