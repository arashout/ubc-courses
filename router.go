package main

import (
	"net/http"

	"github.com/gorilla/mux"
)

func NewRouter() *mux.Router {

	router := mux.NewRouter().StrictSlash(true)

	router.Methods("OPTIONS").HandlerFunc(
		func(w http.ResponseWriter, r *http.Request) {
			w.Header().Set("Access-Control-Allow-Origin", "https://ssc.adm.ubc.ca")
			w.Header().Set("Access-Control-Allow-Methods", "OPTIONS, GET")
			w.Header().Set("Access-Control-Allow-Headers", "Authorization, Lang, Content-Type")
		})

	for _, route := range routes {
		handler := Logger(route.HandlerFunc, route.Name)

		router.
			Methods(route.Method).
			Path(route.Pattern).
			Name(route.Name).
			Handler(handler)
	}

	return router
}
