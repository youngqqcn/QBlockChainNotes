## 编写链码-helloworld

### 本地依赖安装(window, linux, mac都可以)

- `GOPATH`可以包含多个路径: 第一个路径用来存放依赖包; 第二个路径设置为项目路径.

- 国内使用`go get`命令获取依赖速度很慢, 可以使用gopm进行加速

  ```
  #安装到GOPATH/bin目录, 如果需要在命令行中直接使用,需将环境变量GOBIN设置为 GOPATH/bin, 并添加至环境变量中
  go get -u github.com/gpmgo/gopm
  
  #使用gopm 安装 fabric
  gopm get -g github.com/hyperledger/fabric
  
  #更多gopm命令使用, 参考: https://www.jianshu.com/p/a7c3aeb0948d
  ```

### 编写链代码

创建目录 helloworld, 并将目录路径添加至 `GOPATH`

- helloworld.go

  ```
  package main
  
  import (
  	"github.com/hyperledger/fabric/core/chaincode/shim"
  	"github.com/hyperledger/fabric/protos/peer"
  	"log"
  )
  
  type HelloWorld struct {
  }
  
  func (this *HelloWorld) Init( stub shim.ChaincodeStubInterface) peer.Response {
  
  
  	args := stub.GetStringArgs()
  
  	err := stub.PutState(args[0], []byte(args[1]))
  	if err != nil {
  		shim.Error(err.Error())
  	}
  	return  shim.Success(nil)
  }
  
  
  func (this *HelloWorld)Invoke(stub shim.ChaincodeStubInterface) peer.Response  {
  
  	fn, args := stub.GetFunctionAndParameters()
  	if fn == "set"{
  		return this.set(stub, args)
  	}else if fn == "get"{
  		return this.get(stub, args)
  	}
  	return shim.Error("Invoke func error")
  }
  
  func (this *HelloWorld)set(stub shim.ChaincodeStubInterface,  args  []string)  peer.Response {
  	err := stub.PutState(args[0], []byte(args[1]))
  	if err != nil{
  		return shim.Error(err.Error())
  	}
  	return shim.Success(nil)
  }
  
  func (this *HelloWorld)get(stub shim.ChaincodeStubInterface, args []string) peer.Response  {
  
  	value, err := stub.GetState(args[0])
  	if err != nil{
  		return shim.Error(err.Error())
  	}
  	return shim.Success(value)
  }
  
  
  func main(){
  	err := shim.Start(new(HelloWorld))
  	if err != nil {
  		log.Println(err)
  		return
  	}
  }
  ```

- 本地测试: helloworld_test.go   

  ```
  package main
  
  import (
  	"testing"
  	"github.com/hyperledger/fabric/core/chaincode/shim"
  	"fmt"
  
  )
  
  
  
  
  func checkInit(t *testing.T, stub *shim.MockStub, args [][]byte) {
  	res := stub.MockInit("1", args)
  	if res.Status != shim.OK {
  		fmt.Println("Init failed", string(res.Message))
  		t.FailNow()
  	}
  }
  
  func checkQuery(t *testing.T, stub *shim.MockStub, name string) {
  	res := stub.MockInvoke("1", [][]byte{[]byte("get"), []byte(name)})
  	if res.Status != shim.OK {
  		fmt.Println("Query", name, "failed", string(res.Message))
  		t.FailNow()
  	}
  	if res.Payload == nil {
  		fmt.Println("Query", name, "failed to get value")
  		t.FailNow()
  	}
  
  	fmt.Println("Query value", name, "was ", string(res.Payload))
  
  }
  
  func checkInvoke(t *testing.T, stub *shim.MockStub, args [][]byte) {
  	res := stub.MockInvoke("1", args)
  	if res.Status != shim.OK {
  		fmt.Println("Invoke", args, "failed", string(res.Message))
  		t.FailNow()
  	}
  }
  
  func Test_Helloworld(t *testing.T) {
  
  	hello := new(HelloWorld)
  	stub := shim.NewMockStub("hello", hello)
  
  	checkInit(t, stub, [][]byte{[]byte("str"), []byte("helloworld")})
  	checkQuery(t, stub, "str")
  
  	checkInvoke(t, stub, [][]byte{[]byte("set"), []byte("str"), []byte("helloworld-1111")})
  	checkQuery(t, stub, "str")
  }
  
  ```

- 本地测试

  ```
  cd helloworld  
  go test -v  helloworld.go helloworld_test.go
  
  输出如下:
  === RUN   Test_Helloworld
  Query value str was  helloworld
  Query value str was  helloworld-1111
  --- PASS: Test_Helloworld (0.00s)
  PASS
  ok
  ```


## 部署链码

>  环境: Ubuntu 18.04

- 将 helloworld 复制到 fabric-samples/chaincode目录下

- 终端1--启动网络

  ```
  cd	chaincode-docker-devmode
  
  docker-compose -f docker-compose-simple.yaml up
  
  ```

  > 如果启动出错,删除所有的docker容器
  >
  > `docker rm -f $(docker ps -aq)`
  > `docker-compose -f docker-compose-simple.yaml down`   #停止网络

- 终端2 --编译并启动链码

  ```
  #启动chaincode容器
  docker exec -it chaincode bash
  
  #进入链码目录
  cd helloworld
  
  #编译
  go build
  
  #启动链码
  CORE_PEER_ADDRESS=peer:7052 CORE_CHAINCODE_ID_NAME=mycc:0 ./helloworld
  ```

  > 当peer:7051 启动链码时报错: `ERRO 003 Received error from server, ending chaincode stream: rpc error: code = Unimplemented desc = unknown service protos.ChaincodeSupport` 
  >
  > 是因为版本问题, 解决方法:
  >
  > https://stackoverflow.com/questions/48007519/unimplemented-desc-unknown-service-protos-chaincodesupport

- 终端 3 -- 操作链码

  ```
  #启动cli容器
  docker exec -it cli bash
  
  #安装链码
  peer chaincode install -p chaincodedev/chaincode/helloworld -n mycc -v 0
  
  #实例化链码
  peer chaincode instantiate -n mycc -v 0 -c '{"Args":["str","helloworld"]}' -C myc
  
  #查询链码
  peer chaincode query -n mycc -c '{"Args":["get","str"]}' -C myc 
  
  #调用链码中的set方法
  peer chaincode invoke -n mycc -c '{"Args":["set", "str", "helloworld youngqq"]}' -C myc
  
  #查询链码
  peer chaincode query -n mycc -c '{"Args":["get","str"]}' -C myc 
  
  ```



## 代码分析

```go
//fabric/core/chaincode/shim/interfaces.go

// Chaincode interface must be implemented by all chaincodes. The fabric runs
// the transactions by calling these functions as specified.
type Chaincode interface {
	// Init is called during Instantiate transaction after the chaincode container
	// has been established for the first time, allowing the chaincode to
	// initialize its internal data
	Init(stub ChaincodeStubInterface) pb.Response

	// Invoke is called to update or query the ledger in a proposal transaction.
	// Updated state variables are not committed to the ledger until the
	// transaction is committed.
	Invoke(stub ChaincodeStubInterface) pb.Response
}
```



