package random_test

import (
	"crypto/rand"
	"fmt"
	"math/big"
	"testing"

	"github.com/stretchr/testify/require"
)

func TestRandom(t *testing.T) {

	// reader, err := os.OpenFile("/dev/random", os.O_RDONLY, 0666)
	r, err := rand.Int(rand.Reader, big.NewInt(100000000))
	require.NoError(t, err)
	fmt.Println(r)

}
