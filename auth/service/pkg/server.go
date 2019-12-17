package pkg

import (
	"net/http"
	"time"

	"github.com/labstack/echo"
	echolog "github.com/onrik/logrus/echo"
	"github.com/sirupsen/logrus"

	"github.com/mtaylor91/demo-app/auth/service/pkg/signature"
)

type (
	Rule struct {
		Policy     string `json:"policy"`
		Effect     string `json:"effect"`
		Action     string `json:"action"`
		Resource   string `json:"resource"`
		Precedence int    `json:"precedence"`
	}

	Session struct {
		ID      string    `json:"id"`
		User    *string   `json:"user"`
		Epoch   int       `json:"epoch"`
		Rules   []Rule    `json:"rule"`
		Created time.Time `json:"created"`
		Updated time.Time `json:"updated"`
		Expires time.Time `json:"expires"`
	}
)

func RunServer() {
	logrus.SetFormatter(&logrus.JSONFormatter{})

	e := echo.New()
	e.Logger = echolog.NewLogger(logrus.StandardLogger(), "")

	e.Use(signature.Verifier)

	e.GET("/", func(c echo.Context) error {
		return c.String(http.StatusOK, "Hello, world!!!")
	})

	e.Logger.Fatal(e.Start(":3000"))
}
