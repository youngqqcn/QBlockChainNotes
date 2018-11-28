package main

import (
	"fmt"
	"math/rand"
	"time"
)

/**
*作者: yqq
*日期: 2018/11/28  11:38
*描述:
	通过接口实现多态

*/

type  Vehicle interface {
	SetSpeed(nSpeed int)
	Run()
}

type ElectricCar struct {
	nSpeed int
}

//比亚迪电动车
type  BYD struct {
	ElectricCar
	nBYDSerialId  int  //比亚迪电动车的序列号
}

func (car *BYD)SetSpeed(nSpeed int)  {
	car.nSpeed  = nSpeed
}

func (car BYD)Run()  {
	fmt.Printf("比亚迪电动车%d, 正在跑, 时速为%d\n", car.nBYDSerialId, car.nSpeed)
}


//特斯拉
type Tesla struct {
	ElectricCar
	nTeslaId  int  //特斯拉序列号
}

func (car *Tesla)SetSpeed(nSpeed int)  {
	car.nSpeed  = nSpeed
}

func (car Tesla)Run()  {
	fmt.Printf("特斯拉电动车%d, 正在跑, 时速为%d\n", car.nTeslaId, car.nSpeed)
}

func main() {

	var  car Vehicle

	for i := 0; i < 10; i++ {
		rand.Seed(time.Now().UnixNano())
		switch rand.Int() & 1 {
		case 0:
			car = &BYD{nBYDSerialId:100001}
			car.SetSpeed(rand.Int() % 200 + 200)
			car.Run()
		case 1:
			car = &Tesla{ElectricCar{0}, 100007}
			car.SetSpeed(rand.Int() % 500 + 500)
			car.Run()
		}

		time.Sleep(100)
	}

}
