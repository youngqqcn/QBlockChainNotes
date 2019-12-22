/**
*Date: 2019/11/30 13:24
*Author:yqq
*Descriptions:

	C++11  C++14  C++17 的一些新的特性

*/
#ifdef _WIN32
#define _CRT_SECURE_NO_WARNINGS  
#endif
#include <cstdio>
#include <iostream>
#include <vector>
#include <array>
#include <complex>

#define  BOOST_TEST_MAIN
#include "boost/algorithm/string.hpp"
#include "boost/format.hpp"
#include "boost/test/included/unit_test.hpp"


using namespace std;



BOOST_AUTO_TEST_SUITE(test_cpp11)

BOOST_AUTO_TEST_CASE(test_char16_t)
{
	const char16_t* ch16Chinese = u"中文のああㅝㅒㅖㄸЩПЁξζ∰㏒";
	const char32_t* ch32Chinese = U"中文のああㅝㅒㅖㄸЩПЁξζ∰㏒";
	const wchar_t* wchChinese = L"中文のああㅝㅒㅖㄸЩПЁξζ∰㏒";
	std::wcout << ch16Chinese << std::endl;
	std::wcout << ch32Chinese << std::endl;
	std::cout << "--------" << std::endl;
	std::wcout << wchChinese << std::endl;
	wprintf(wchChinese);

	std::cout << "hello" << std::endl;
}


BOOST_AUTO_TEST_CASE(test_uniforminitialize)
{

	int d{ 10 };
	char ch {90};


	std::vector<int> a1{ 100, 99, 123 };
	std::cout << "size : " << a1.size() << std::endl;
	for (auto item : a1) {
		std::cout << item << std::endl;
	}
	
}


struct CTemp
{
	//CTemp(std::initializer_list<int> &initList) //error
	CTemp(std::initializer_list<int> initList) //ok
	{
		for (auto item : initList)
		{
			m_vctNumbers.push_back(item);
		}

		/*m_vctNumbers(initList);*/ //error
	}

	~CTemp() {}


	void Show()
	{
		for (auto item : m_vctNumbers)
		{
			std::cout << item << std::endl;
		}
	}

	//void Set(std::initializer_list<int>& ilstArgs) //不支持引用方式
	//void Set(std::initializer_list<int> *ilstArgs) //不支持指针
	void Set(std::initializer_list<int> ilstArgs)
	{
		m_vctNumbers.clear();
		//for (auto item : *ilstArgs)
		for (auto item : ilstArgs)
		{
			m_vctNumbers.push_back(item);
		}
	}

	std::vector<int> m_vctNumbers;
};



BOOST_AUTO_TEST_CASE(test_initialize_list)
{
	//该语法只能用于构造函数, 但是initializer_list可以当做模板来用
	CTemp  tmp{ 3, 9, 2, 88, 12, 93 }; 
	
	tmp.Show();

	tmp.Set({1, 3, 9, -134});

	tmp.Show();
}


template <typename T>
void MyTest(T a, T b)
{
	typedef std::array<T, 10> arr10;
	using arr11 = std::array<T, 11>;

	arr10 arrTst;
	arrTst[0] = a;
	arrTst[9] = b;

	std::cout << arrTst[9] << std::endl;

	arr11 arr11Tst;
	arr11Tst[0] = a;
	arr11Tst[10] = b;
	std::cout << arr11Tst[10] << std::endl;

}



template < typename T >
using arr20 = std::array<T, 20>;
//typedef arr20 = std::array<T, 20>; //错误, typedef不支持

BOOST_AUTO_TEST_CASE(test_using)
{

	//使用 typedef 取别名
	typedef std::vector<int>::iterator   vctit;
	using vctit2 = std::vector<int>::iterator ;


	std::vector<int> vctTst{1, 39, 99};
	vctit itBegin = vctTst.begin();
	vctit2 itBegin2 = vctTst.begin();
	std::cout << (itBegin == itBegin2) << std::endl;
	std::cout << *itBegin << std::endl;


	MyTest<int>( 7, 9);


	arr20<double> arr20Test{ 0.99923, 1.342, 9 };
	for (auto item : arr20Test)
	{
		std::cout << item << std::endl;
	}
}


////////////////////////////////////////////////////////////////////////
template <typename T, typename U>
auto MyFunc(T t, U u) -> decltype(t + u)
{
	return t + u;
}

struct CPear
{
	CPear(std::string strName) : m_strName(strName)
	{
	}
	
	std::string m_strName;
};

struct CPearApple
{
	CPearApple(std::string strName) :m_strName(strName)
	{

	}

	std::string m_strName;
};

struct CApple
{
	CApple(std::string strName) : m_strName(strName)
	{

	}


	CPearApple operator+ (const CPear& pear)
	{
		return CPearApple(pear.m_strName + m_strName);
	}

	std::string m_strName;
};


BOOST_AUTO_TEST_CASE(test_functionreturntype)
{
	std::complex a(1, -2);
	std::complex  b(2, -3);

	auto c  =  MyFunc( a , b );
	std::cout << c << std::endl;

	CPear pear("pear");
	CApple apple("apple");
	auto pearApple = MyFunc(apple, pear);


	std::cout << pearApple.m_strName << std::endl;

}
//////////////////////////////////////////////////////////////////




BOOST_AUTO_TEST_CASE(test_testlabdafunctype)
{

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

}



class MyComplex
{
public:
	MyComplex(int ir, int im = 0)
		: _m_ir(ir), _m_im(im)
	{
		_m_ino = 55 + ir;
	}

	//C++的数据限制是 "类" 级别的, 而不是对象级别, 
	//所以同一类的  一个对象 再成员函数中可以修改 另一个对象的私钥或保护成员
	MyComplex & operator + (const MyComplex& cplx)
	{
		_m_ir += cplx._m_ir;
		_m_im += cplx._m_im;
		std::cout << cplx._m_ino << std::endl;
		return *this;
	}


protected:
	int _m_ir;
	int _m_im;

private:
	int _m_ino;
};


class MyComplexEx
{
public:
	explicit MyComplexEx(int ir, int im = 0)
		: _m_ir(ir), _m_im(im)
	{
		_m_ino = 55 + ir;
	}

	//C++的数据限制是 "类" 级别的, 而不是对象级别, 
	//所以同一类的  一个对象 再成员函数中可以修改 另一个对象的私钥或保护成员
	MyComplexEx& operator + (const MyComplexEx& cplx)
	{
		_m_ir += cplx._m_ir;
		_m_im += cplx._m_im;
		std::cout << cplx._m_ino << std::endl;
		return *this;
	}


protected:
	int _m_ir;
	int _m_im;

private:
	int _m_ino;
};

BOOST_AUTO_TEST_CASE(test_explicit)
{
	MyComplex  mcplx(5, -1);
	mcplx = mcplx + 5;   //这样是可以的, 编译做了隐式转换
	//_m_ir = 10
	//_m_im
	MyComplexEx  mcplxEx(5, -1);
	//mcplxEx = mcplxEx + 5;   //这样是不可以的, 显示地限制了隐式转换
	
}


BOOST_AUTO_TEST_SUITE_END()
