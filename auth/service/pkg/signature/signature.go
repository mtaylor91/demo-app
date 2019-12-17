package signature

import (
	"bytes"
	"crypto/rand"
	"encoding/base64"
	"errors"
	"io"
	"net/http"
	"strings"
	"text/template"

	"golang.org/x/crypto/ed25519"
)

const (
	DemoAppV0SigEd25519 = "DEMOAPP-V0-SIG-ED25519"

	AuthorizationPrefix = DemoAppV0SigEd25519 + " "

	AuthorizationHeader = "Authorization"

	HostHeader = "Host"

	DomainHeader = "X-Demo-App-Domain"

	AlgorithmHeader = "X-Demo-App-Algorithm"

	TimestampHeader = "X-Demo-App-Timestamp"

	AccessKeyHeader = "X-Demo-App-Access-Key"

	SessionIdHeader = "X-Demo-App-Session-Id"

	SessionExpiresHeader = "X-Demo-App-Session-Expires"

	SessionSignatureHeader = "X-Demo-App-Session-Signature"

	SessionSigningKeyHeader = "X-Demo-App-Session-Signing-Key"

	RequestChecksumHeader = "X-Demo-App-Request-Checksum"
)

var (
	b64 = base64.StdEncoding

	headers = map[string]string{
		"Host":              HostHeader,
		"Domain":            DomainHeader,
		"Algorithm":         AlgorithmHeader,
		"Timestamp":         TimestampHeader,
		"AccessKey":         AccessKeyHeader,
		"SessionId":         SessionIdHeader,
		"SessionExpires":    SessionExpiresHeader,
		"SessionSignature":  SessionSignatureHeader,
		"SessionSigningKey": SessionSigningKeyHeader,
		"RequestChecksum":   RequestChecksumHeader,
	}

	requestStringToSignTemplateString string

	requestStringToSignTemplate *template.Template

	requestSignatureParameters = []string{
		"Host",
		"Domain",
		"Algorithm",
		"Timestamp",
		"AccessKey",
		"SessionId",
		"SessionExpires",
		"SessionSignature",
		"SessionSigningKey",
		"Resource",
		"Action",
		"RequestChecksum",
	}

	sessionStringToSignTemplateString string

	sessionStringToSignTemplate *template.Template

	sessionSignatureParameters = []string{
		"Domain",
		"AccessKey",
		"SessionId",
		"SessionExpires",
		"SessionSigningKey",
	}
)

type (
	AccessKey string

	SecretKey string

	Signature string

	RequestVerification struct {
		Host              string
		Domain            string
		Algorithm         string
		Timestamp         string
		AccessKey         string
		SessionId         string
		SessionExpires    string
		SessionSignature  string
		SessionSigningKey string
		Resource          string
		Action            string
		RequestChecksum   string
	}

	SessionVerification struct {
		Domain            string
		AccessKey         string
		SessionId         string
		SessionExpires    string
		SessionSigningKey string
	}
)

func init() {
	initRequestStringToSignTemplate()
	initSessionStringToSignTemplate()
}

func initSessionStringToSignTemplate() {
	var builder strings.Builder

	for _, headerKey := range sessionSignatureParameters {
		builder.WriteString(headerKey + "={{ ." + headerKey + " }}\n")
	}

	sessionStringToSignTemplateString = builder.String()
	sessionStringToSignTemplate = template.Must(
		template.New("sessionStringToSign").Parse(
			sessionStringToSignTemplateString,
		),
	)
}

func initRequestStringToSignTemplate() {
	var builder strings.Builder

	for _, headerKey := range requestSignatureParameters {
		builder.WriteString(headerKey + "={{ ." + headerKey + " }}\n")
	}

	requestStringToSignTemplateString = builder.String()
	requestStringToSignTemplate = template.Must(
		template.New("requestStringToSign").Parse(
			requestStringToSignTemplateString,
		),
	)
}

func Authorization(signature Signature) string {
	return AuthorizationPrefix + string(signature)
}

func KeyPair() (AccessKey, SecretKey, error) {
	publicKey, privateKey, err := ed25519.GenerateKey(rand.Reader)
	if err != nil {
		return "", "", err
	}

	accessKey := AccessKey(b64.EncodeToString(publicKey))
	secretKey := SecretKey(b64.EncodeToString(privateKey))

	return accessKey, secretKey, nil
}

func DecodeAccessKey(accessKey AccessKey) (ed25519.PublicKey, error) {
	decoded, err := b64.DecodeString(string(accessKey))
	if err != nil {
		return nil, err
	}

	return ed25519.PublicKey(decoded), nil
}

func DecodeSecretKey(secretKey SecretKey) (ed25519.PrivateKey, error) {
	decoded, err := b64.DecodeString(string(secretKey))
	if err != nil {
		return nil, err
	}

	return ed25519.PrivateKey(decoded), nil
}

func SignRequest(
	request *http.Request,
	checksum string,
	privateKey ed25519.PrivateKey,
) (Signature, error) {
	var buffer bytes.Buffer

	verification := requestVerification(request, checksum)
	writeRequestStringToSign(&buffer, verification)
	signature := ed25519.Sign(privateKey, buffer.Bytes())
	return Signature(b64.EncodeToString(signature)), nil
}

func SignSession(
	header http.Header, privateKey ed25519.PrivateKey,
) (Signature, error) {
	var buffer bytes.Buffer

	verify := sessionVerification(header)
	if err := writeSessionStringToSign(&buffer, verify); err != nil {
		return "", err
	}

	signature := ed25519.Sign(privateKey, buffer.Bytes())
	return Signature(b64.EncodeToString(signature)), nil
}

func VerifyRequest(
	request *http.Request,
	checksum string,
) (*RequestVerification, error) {
	var buffer bytes.Buffer

	authorization := request.Header.Get(AuthorizationHeader)
	if authorization == "" {
		return nil, nil
	} else if !strings.HasPrefix(authorization, AuthorizationPrefix) {
		return nil, errors.New("Unsupported Authorization Type")
	}

	if checksum != request.Header.Get(RequestChecksumHeader) {
		return nil, errors.New("Request Checksum Mismatch")
	}

	accessKey := request.Header.Get(AccessKeyHeader)
	accessKeyBytes, err := b64.DecodeString(accessKey)
	if err != nil {
		return nil, errors.New("Invalid Access Key")
	}

	signature := strings.TrimPrefix(authorization, AuthorizationPrefix)
	signatureBytes, err := b64.DecodeString(signature)
	if err != nil {
		return nil, errors.New("Invalid Authorization Signature")
	}

	verification := requestVerification(request, checksum)
	must(writeRequestStringToSign(&buffer, verification))
	publicKey := ed25519.PublicKey(accessKeyBytes)
	valid := ed25519.Verify(publicKey, buffer.Bytes(), signatureBytes)
	if !valid {
		return nil, errors.New("Invalid Authorization Signature")
	}

	return verification, nil
}

func VerifySession(header http.Header) (*SessionVerification, error) {
	var buffer bytes.Buffer

	signingKey := header.Get(SessionSigningKeyHeader)
	signingKeyBytes, err := b64.DecodeString(signingKey)
	if err != nil {
		return nil, errors.New("Invalid Access Key")
	}

	signature := header.Get(SessionSignatureHeader)
	signatureBytes, err := b64.DecodeString(signature)
	if err != nil {
		return nil, errors.New("Invalid Session Signature")
	}

	verification := sessionVerification(header)
	must(writeSessionStringToSign(&buffer, verification))
	publicKey := ed25519.PublicKey(signingKeyBytes)
	valid := ed25519.Verify(publicKey, buffer.Bytes(), signatureBytes)
	if !valid {
		return nil, errors.New("Invalid Session Signature")
	}

	return verification, nil
}

func writeRequestStringToSign(
	output io.Writer,
	verify *RequestVerification,
) error {
	return requestStringToSignTemplate.Execute(output, verify)
}

func writeSessionStringToSign(
	output io.Writer,
	verify *SessionVerification,
) error {
	return sessionStringToSignTemplate.Execute(output, verify)
}

func requestVerification(
	r *http.Request, checksum string,
) *RequestVerification {
	return &RequestVerification{
		r.Header.Get(HostHeader),
		r.Header.Get(DomainHeader),
		r.Header.Get(AlgorithmHeader),
		r.Header.Get(TimestampHeader),
		r.Header.Get(AccessKeyHeader),
		r.Header.Get(SessionIdHeader),
		r.Header.Get(SessionExpiresHeader),
		r.Header.Get(SessionSignatureHeader),
		r.Header.Get(SessionSigningKeyHeader),
		strings.ToLower(r.Method),
		r.URL.Path,
		checksum,
	}
}

func sessionVerification(header http.Header) *SessionVerification {
	return &SessionVerification{
		header.Get(DomainHeader),
		header.Get(AccessKeyHeader),
		header.Get(SessionIdHeader),
		header.Get(SessionExpiresHeader),
		header.Get(SessionSigningKeyHeader),
	}
}

func must(err error) {
	if err != nil {
		panic(err)
	}
}
