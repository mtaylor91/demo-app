package signature

import (
	"testing"

	"net/http"
	"net/url"
	"time"

	"github.com/google/uuid"
	"github.com/stretchr/testify/assert"
)

func TestRequestSignature(t *testing.T) {

	sessionSigningKey, sessionSigningSecretKey, err := KeyPair()

	assert.NoError(t, err)

	requestorAccessKey, requestorSecretKey, err := KeyPair()

	assert.NoError(t, err)

	timestamp := time.Now().UTC()

	sessionID := uuid.New()

	sessionExpires := timestamp.Add(10 * time.Minute)

	checksum := "placeholder"

	request := &http.Request{
		Method: "GET",
		URL:    &url.URL{Path: "/users/mike.charles.taylor@gmail.com"},
		Header: http.Header{
			HostHeader: []string{
				"host.example.com",
			},
			DomainHeader: []string{
				"example.com",
			},
			AlgorithmHeader: []string{
				DemoAppV0SigEd25519,
			},
			AccessKeyHeader: []string{
				string(requestorAccessKey),
			},
			TimestampHeader: []string{
				timestamp.Format(time.RFC3339),
			},
			SessionIdHeader: []string{
				sessionID.String(),
			},
			SessionExpiresHeader: []string{
				sessionExpires.Format(time.RFC3339),
			},
			SessionSigningKeyHeader: []string{
				string(sessionSigningKey),
			},
			RequestChecksumHeader: []string{
				checksum,
			},
		},
	}

	sessionSigningPrivateKey, err := DecodeSecretKey(
		sessionSigningSecretKey,
	)

	assert.NoError(t, err)

	sessionSignature, err := SignSession(
		request.Header, sessionSigningPrivateKey,
	)

	assert.NoError(t, err)

	request.Header[SessionSignatureHeader] = []string{
		string(sessionSignature),
	}

	requestorPrivateKey, err := DecodeSecretKey(
		requestorSecretKey,
	)

	assert.NoError(t, err)

	requestSignature, err := SignRequest(
		request, checksum, requestorPrivateKey,
	)

	request.Header[AuthorizationHeader] = []string{
		Authorization(requestSignature),
	}

	validSession, err := VerifySession(request.Header)

	assert.NoError(t, err)

	assert.NotNil(t, validSession)

	validRequest, err := VerifyRequest(request, checksum)

	assert.NoError(t, err)

	assert.NotNil(t, validRequest)
}
