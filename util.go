package main

import (
	"fmt"
)

func RetrieveCourse(code string) (Course, error) {
	if courseName, ok := courseMap[code]; ok {
		return Course{
			Code: code,
			Name: courseName,
		}, nil
	}
	return Course{}, fmt.Errorf("WARN:\t%s\t course code not found", code)
}
