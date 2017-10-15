package main

import (
	"fmt"
	"log"
	"net/http"

	"github.com/gorilla/mux"
)

func GetCourseEndpoint(w http.ResponseWriter, req *http.Request) {
	fmt.Fprintln(w, "Course Endpoint")
}

func main() {
	router := mux.NewRouter()
	router.HandleFunc("/course/{id}", GetCourseEndpoint).Methods("GET")
	log.Fatal(http.ListenAndServe(":8080", nil))
}
