package signature

import (
	"bytes"
	"crypto/sha256"
	"io/ioutil"

	"github.com/labstack/echo"
)

const (
	requestVerificationKey      = "SignatureRequestVerification"
	requestVerificationErrorKey = "SignatureRequestVerificationError"
	sessionVerificationKey      = "SignatureSessionVerification"
	sessionVerificationErrorKey = "SignatureSessionVerificationError"
)

func SignatureError(c echo.Context) error {
	return c.Get("SignatureError").(error)
}

func Verifier(handler echo.HandlerFunc) echo.HandlerFunc {
	return func(c echo.Context) error {
		request := c.Request()
		body, err := ioutil.ReadAll(request.Body)
		if err != nil {
			return err
		}

		sessionVerification, err := VerifySession(request.Header)
		sessionVerified(c, sessionVerification, err)

		checksumBytes := sha256.Sum256(body)
		checksum := b64.EncodeToString(checksumBytes[:])

		buffer := bytes.NewBuffer(body)
		request.Body = ioutil.NopCloser(buffer)
		c.SetRequest(request) // is this necessary?

		requestVerification, err := VerifyRequest(request, checksum)
		requestVerified(c, requestVerification, err)

		return handler(c)
	}
}

func RequestVerified(c echo.Context) (*RequestVerification, error) {
	v := c.Get(requestVerificationKey).(*RequestVerification)
	err := c.Get(requestVerificationErrorKey).(error)
	return v, err
}

func SessionVerified(c echo.Context) (*SessionVerification, error) {
	v := c.Get(sessionVerificationKey).(*SessionVerification)
	err := c.Get(sessionVerificationErrorKey).(error)
	return v, err
}

func requestVerified(c echo.Context, v *RequestVerification, err error) {
	c.Set(requestVerificationKey, v)
	c.Set(requestVerificationErrorKey, err)
}

func sessionVerified(c echo.Context, v *SessionVerification, err error) {
	c.Set(sessionVerificationKey, v)
	c.Set(sessionVerificationErrorKey, err)
}
