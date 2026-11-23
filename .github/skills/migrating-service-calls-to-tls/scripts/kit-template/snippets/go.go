// Go: calling {{PRODUCER}} with your client certificate.
package main

import (
	"crypto/tls"
	"crypto/x509"
	"fmt"
	"net/http"
	"os"
)

func main() {
	cert, err := tls.LoadX509KeyPair("/etc/tls/{{PRODUCER}}/client.crt", "/etc/tls/{{PRODUCER}}/client.key")
	if err != nil {
		panic(err)
	}
	caPEM, err := os.ReadFile("/etc/tls/{{PRODUCER}}/ca-bundle.pem")
	if err != nil {
		panic(err)
	}
	roots := x509.NewCertPool()
	roots.AppendCertsFromPEM(caPEM)
	client := &http.Client{Transport: &http.Transport{TLSClientConfig: &tls.Config{
		Certificates: []tls.Certificate{cert},
		RootCAs:      roots,
		MinVersion:   tls.VersionTLS12,
		// Never set the skip-verification option.
	}}}
	resp, err := client.Get("{{ENDPOINT}}")
	if err != nil {
		panic(err)
	}
	defer resp.Body.Close()
	fmt.Println(resp.StatusCode)
}
