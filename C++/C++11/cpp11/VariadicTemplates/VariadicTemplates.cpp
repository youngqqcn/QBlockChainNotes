/**
*Date: 2019/12/21  14:27
*Author:yqq
*Descriptions:  C++11 可变参数模板
*/
#ifdef _WIN32
#define _CRT_SECURE_NO_WARNINGS  
#endif
#include <cstdio>
#include <iostream>
#include <vector>
#include <array>
#include <complex>
#include <algorithm>
#include <ctime>

#define  BOOST_TEST_MAIN
#include "boost/algorithm/string.hpp"
#include "boost/format.hpp"
#include "boost/test/included/unit_test.hpp"



BOOST_AUTO_TEST_SUITE(test_cpp11)



template<typename T>
void PlainPrint(const T& arg)
{
	std::cout << arg << std::endl;
}

//函数模板不存在 "偏特化"
/*
template<>
void PlainPrint(const std::complex& cplx)
{
	std::cout << "复数: " << cplx << std::endl;
}
*/




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






//实现编译时期的求最大值得函数
//#define  mymax( a, b )   ( a > b ? a : b )


#ifdef max
#undef max
#endif


int mymaximum(int n) //递归结束
{
	return n;
}

template <typename ...Args>
int mymaximum(int nfirst, const Args&... arguments)
{
	return std::max(nfirst, mymaximum(arguments...));
}


BOOST_AUTO_TEST_CASE(test_variadic_maximum)
{

	std::cout << "maximum is : " <<
		mymaximum(9, 1, -1, 22, -12, 10, 11, -9, 5, -23, 19, 21, 22)
		<< std::endl;

	//std::cout << mymax(9, 10) << std::endl;
   //std::cout <<	std::max( 9, 10 ) << std::endl;

}




BOOST_AUTO_TEST_CASE(test_move)
{
	std::vector <std::string>   vctStrs;

	const int iTestCount = 500;

	{


#ifdef _WIN32
		DWORD   dwStart = ::GetTickCount();
#else
		clock_t  clkStart = clock();
#endif


		for (int i = 0; i < iTestCount; i++)
		{
			//vctStrs.push_back( std::move( std::string("helllo")  )); //默认使用 push_back(T&&)


			std::string strTmp("hello");

			vctStrs.push_back(strTmp); //使用   push_back(T &)

		}

#ifdef _WIN32
		DWORD   dwEnd = ::GetTickCount();
		std::cout << "duration: " << dwEnd - dwStart << std::endl;
#else
		clock_t  clkEnd = clock();
		std::cout << "duration: " << clkEnd - clkStart << std::endl;
#endif

	}


	{

#ifdef _WIN32
		DWORD   dwStart = ::GetTickCount();
#else
		clock_t  clkStart = clock();
#endif

		for (int i = 0; i < iTestCount; i++)
		{
			//std::string strTmp("hello");

			vctStrs.push_back(std::move(std::string("hello"))); // 使用 push_back(T&& )
		}


#ifdef _WIN32
		DWORD   dwEnd = ::GetTickCount();
		std::cout << "duration: " << dwEnd - dwStart << std::endl;
#else
		clock_t  clkEnd = clock();
		std::cout << "duration: " << clkEnd - clkStart << std::endl;
#endif

	}

}


BOOST_AUTO_TEST_CASE(test_initializer_list)
{

	std::vector<int> vctInts({92, 12, 39, 46, 92, 84, -1, 0, -234});
	for (const auto& item : vctInts)
	{
		std::cout << item << std::endl;
	}


}


BOOST_AUTO_TEST_SUITE_END()

