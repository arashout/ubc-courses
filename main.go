package main

import (
	"fmt"
	"log"
	"net/http"
	"os"

	"github.com/gorilla/mux"
)

func GetCourseEndpoint(w http.ResponseWriter, req *http.Request) {
	fmt.Fprintln(w, "Course Endpoint")
}

func main() {
	port := os.Getenv("PORT")

	if port == "" {
		log.Fatal("$PORT must be set")
	}

	router := mux.NewRouter()
	router.HandleFunc("/course/{id}", GetCourseEndpoint).Methods("GET")
	log.Fatal(http.ListenAndServe(":"+port, nil))
}
