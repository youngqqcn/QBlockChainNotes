# C++11/14/17 新特性总结


- initializer_list

```
	std::vector<int> vctInts({92, 12, 39, 46, 92, 84, -1, 0, -234});
```

- auto 

```
	std::vector<int> vctInts({92, 12, 39, 46, 92, 84, -1, 0, -234});
	for (const auto& item : vctInts)
	{
		std::cout << item << std::endl;
	}

```

- decltype

用于模板函数的参数返回类型声明
```cpp
template <typename T, typename U>
auto MyFunc(T t, U u) -> decltype(t + u)
{
	return t + u;
}

```

用于对lambda函数类型自动推导

```cpp
	auto func = [](int a, double b, const std::string& strTmp)->std::string {
		boost::format fmt("%1%  %2%  %3%");
		fmt % a% b% strTmp;
		return fmt.str();
	};

	/*
	auto func2 = [](int a, double b, const std::string& strTmp)->std::string {
		char buf[1024] = { 0 };
		memset(buf, 0, sizeof(buf));
		sprintf_s(buf, "%d %.8f %s", a, b, strTmp.c_str());
		return std::string(buf);
	};
	*/

	std::map<int, decltype(func)> fucMap;

	fucMap.insert( std::make_pair(0,   func) );
	//fucMap.insert( std::make_pair(1, );

	auto it = fucMap.find(0);
	BOOST_CHECK_EQUAL( fucMap.end()== it, false);
	std::cout << it->second(10, 1.23, std::string("hello")) << std::endl;

```

- override 和 final

override 用于来声明重写父类虚函数
final 用来修饰一个类是,表明一个类禁止被继承; 用来修饰虚函数时, 表明虚函数不能被重写




- 函数返回类型后置 (用于模板函数)

- 模板别名:  using

```cpp

typedef std::vector<std::map<std::string, std::string>>::iterator  itMaps;
using itMaps = std::vector<std::map<std::string, std::string>>::iterator  ;

```

using可以用于模板的别名定义, typedef 则不可以
```cpp
template<typename T>
using it12Items = std::array<T, 12>;   

```


- nullptr
用来取代  `NULL`
```cpp

0 == nullptr;  //true
NULL == nullptr;  //true


```


- 智能指针

```
shared_ptr
unique_ptr
weak_ptr
```



- 异常规范  

```cpp

foo()noexcept
foo()noexcept(false)
foo()noexcept(true)


```


- explicit

C++11之前仅限制单个参数的构造函数做隐式转换
C+++11开始不限于单个参数的构造函数



- 可变参数模板
一般用递归的方式逐步减少参数的个数 , 递归终止于0个参数

```

//递归结束
void XPrint()
{
}


template< typename T, typename ...Types>
void XPrint(const T& first,  const Types&... otherArgs)
{
	PlainPrint(first);
	XPrint( otherArgs... );
}



BOOST_AUTO_TEST_CASE(test_variadic_templates)
{
	std::cout << "hello  ............" << std::endl;

	XPrint(2, 5.231, std::string("hello"), "niuniu", std::complex(5, 1));

}

```


- 右值引用和移动语义

注意自己实现移动拷贝(move ctor)的时候(有指针), 收尾时需要将被move的对象的指针设置为NULL

```

std::vector<std::string> vctInts;
vctInts.push_back(std::move( std::string("hello") ));

```

- 原生字符串支持

  ```c++
  //std::string  strFilePath1 = "C:\\Program Files (x86)\\Tencent\\QQ\\gf-config.xml"; //ok
  
  //std::string  strFilePath1 = R"(D:\gradle-6.0-bin.zip)"; //ok
  
  std::string  strFilePath1 = R"(C:\Program Files (x86)\Tencent\QQ\gf-config.xml)"; //ok
  
  std::filesystem::path p1( strFilePath1 ); //filesystem是 C++17标准
  if (filesystem::exists(p1)){
      std::cout << "exists" << std::endl;
  }else{
      std::cout << "not exists" << std::endl;
  }
  
  std::ifstream infstream( strFilePath1, ios::in | ios::binary);
  if(infstream.is_open())
  {
      char buf[1024] { 0 };
      memset(buf, 0, sizeof(buf));
  
      while (!infstream.eof())
      {
          infstream.getline(buf, 1024);
          std::cout << buf << std::endl;
      }
  
      infstream.close();
  }
  else
  {
      std::cout << "open file failed." << std::endl;
  }
  ```

  


- filesystem 文件系统

  


- chrono  时间
- regex 正则表达式



以下内容, 移至 [C++11并发编程](./C++11并发编程.md) 中做介绍

- atomic 原子操作

  >  https://en.cppreference.com/w/cpp/atomic
  >
  > 关于std::memory_order: https://www.cnblogs.com/lizhanzhe/p/10893016.html

- std::thread


- std::mutex 
- std::future 
- std::atomic
- std::async

