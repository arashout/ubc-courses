package main

import (
	"encoding/json"
	"log"
	"net/http"
	"os"
)

type Course struct {
	Code string `json:"code"`
	Name string `json:"name,omitempty"`
}

// Global courses map
var courseMap map[string]string

const port = "8000"

func readCourses(filepath string) {
	fp, err := os.Open(filepath)
	if err != nil {
		log.Fatal(err.Error())
	}

	jsonParser := json.NewDecoder(fp)
	if err = jsonParser.Decode(&courseMap); err != nil {
		log.Fatal(err.Error())
	}
}

func main() {
	readCourses("data/courses_shortened_names.json")

	router := NewRouter()

	log.Println("Listening on: " + port)
	log.Fatal(http.ListenAndServe(":"+port, router))
}
