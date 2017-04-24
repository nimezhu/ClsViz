package main

//go:generate go-bindata-assetfs -pkg main index.tmpl config.json

import (
	"encoding/json"
	"errors"
	"flag"
	"io"
	"io/ioutil"
	"log"
	"net/http"
	"os"
	"strconv"

	"github.com/gorilla/mux"

	"html/template"

	"github.com/nimezhu/snowjs"
)

func getInput(args []string) ([]byte, error) {
	var data []byte
	var err error
	switch len(args) {
	case 0:
		data, err = ioutil.ReadAll(os.Stdin)
		break
	case 1:
		data, err = ioutil.ReadFile(args[0])
		break
	default:
		return nil, errors.New("no data input")
	}
	return data, err
}

var help = flag.Bool("help", false, "print help")
var port = flag.Int("port", 8080, "server port")
var config = flag.String("cfg", "config.json", "config json file")

func checkErr(err error) {
	if err != nil {
		panic(err)
	}
}
func main() {
	router := mux.NewRouter()
	flag.Parse()
	if *help {
		flag.PrintDefaults()
		return
	}
	data, err := getInput(flag.Args())
	checkErr(err)
	router.HandleFunc("/data", func(w http.ResponseWriter, r *http.Request) {
		//w.Header().Add("Content-Type", "text/text")
		io.WriteString(w, string(data))
	})
	tmpl, err := Asset("index.tmpl")
	file, e := ioutil.ReadFile(*config)
	if e != nil {
		log.Println("can not read the json config file, using the default")
		file, _ = Asset("config.json")
	}
	var p interface{}
	err = json.Unmarshal(file, &p)
	checkErr(err)
	addStaticHandles(router, tmpl, p)
	log.Println("Listening...")
	log.Println("Please open http://127.0.0.1:" + strconv.Itoa(*port))
	log.Fatal(http.ListenAndServe(":"+strconv.Itoa(*port), router))
}

func templateHandlerFactory(in []byte, p interface{}) func(http.ResponseWriter, *http.Request) {
	f := func(res http.ResponseWriter, req *http.Request) {
		bytes1 := in
		tmpl := template.New("layout")
		tmpl, err := tmpl.Parse(string(bytes1))
		dir, _ := snowjs.AssetDir("templates")
		for _, d := range dir {
			bytes, err := snowjs.Asset("templates/" + d)
			if err != nil {
				log.Panicf("Unable to parse: template=%s, err=%s", d, err)
			}
			tmpl.New(d).Parse(string(bytes))
		}
		if err != nil {
			log.Println("error parse template: %s", err)
		}
		err = tmpl.Execute(res, p)
		if err != nil {
			log.Println("error executing template: %s", err)
		}
	}
	return f
}
func addStaticHandles(router *mux.Router, stdin []byte, p interface{}) error {
	router.HandleFunc("/", templateHandlerFactory(stdin, p))
	snowjs.AddHandlers(router, "")
	return nil
}
