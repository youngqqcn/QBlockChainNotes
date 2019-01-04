package main

import "sync"

//下面的代码有什么问题

type UserAges struct {
	ages map[string]int
	sync.Mutex
}

func (ua *UserAges) Add(name string, age int) {
	ua.Lock()
	defer ua.Unlock()
	ua.ages[name] = age
}

func (ua *UserAges) Get(name string) int {
	if age, ok := ua.ages[name]; ok {
		return age
	}
	return -1
}

//type UserAges struct {
//	ages map[string]int
//	sync.Mutex
//}
//
//func (ua *UserAges) Add(name string, age int) {
//	ua.Lock()
//	defer ua.Unlock()
//	ua.ages[name] = age
//}

/*
func (ua *UserAges) Get(name string) int {
	if age, ok := ua.ages[name]; ok {
		return age
	}
	return -1
}
*/
//
//func (ua *UserAges) Get(name string) int {
//	ua.Lock()
//	defer ua.Unlock()
//	if age, ok := ua.ages[name]; ok {
//		return age
//	}
//	return -1
//}
//
//
//func main()  {
//
//	var user UserAges
//
//	user.ages = make(map[string]int, 0)
//	user.Add("yqq", 19)
//
//	go func() {
//		for{
//			name := strconv.Itoa( rand.Int())
//			user.Add(name, 18)
//		}
//	}()
//
//	for{
//		fmt.Println( user.Get("yqq") )
//	}
//}

/*
func main()  {

	var user UserAges

	wg := sync.WaitGroup{}
	wg.Add(2)

	user.ages = make(map[string]int, 0)
	user.Add("yqq", 19)
	go func() {
		for{
			name := strconv.Itoa( rand.Int())
			user.Add(name, 18)
		}
		wg.Done()
	}()

	go func(){
		for{
			fmt.Println( user.Get("yqq") )
		}
		wg.Done()
	}()

	wg.Wait()

}
*/

/*
golang中 以下类型不是线程安全的:


 */
