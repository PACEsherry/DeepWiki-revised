package main

import "fmt"

func Greet(name string) string {
    return fmt.Sprintf("Hello %s", name)
}

type Greeter struct {
    Name string
}

func (g Greeter) Greet() string {
    return fmt.Sprintf("Hello %s", g.Name)
} 