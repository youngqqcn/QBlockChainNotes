package main

import (
	"testing"
	"net/http/httptest"
	"net/http"
	"github.com/stretchr/testify/assert"
	"github.com/gin-gonic/gin"
)

/**
*作者: yqq
*日期: 2019/1/27  16:41
*描述: 测试

*/

func TestPingRoute(t *testing.T){
	gin.SetMode(gin.ReleaseMode)

	router := setupRouter()
	recoder := httptest.NewRecorder()
	req, _ := http.NewRequest("GET", "/ping", nil)
	router.ServeHTTP(recoder, req)

	assert.Equal(t, http.StatusOK, recoder.Code)
	assert.Equal(t, "Pong", recoder.Body.String())

}
