//yqq

#include <iostream>
#include <algorithm>
#include <initializer_list>

using namespace std;


//变长模板参数


template<typename T>
void myprintf(T value)
{
    std::cout << value << std::endl;
}

template<typename T, typename... Args>
void myprintf(T value, Args... args)
{
    std::cout << value << std::endl;
    myprintf(args...);
}

template<typename T, typename... Args>
void myprintf2(T value, Args... args)
{
    std::cout << value << std::endl;

    // 如果还有, 继续递归
    if constexpr (sizeof...(args) > 0){ // C++17
        myprintf2(args...);
    }
}

template<typename T, typename... Args>
auto myprintf3(T value, Args... args)
{
    std::cout << value << std::endl;


    // 看不懂啥意思
    auto r = std::initializer_list<T>{( [&args] {
        std::cout << args << std::endl;
    }(), value)...};
    std::cout << "size is : " << r.size() << std::endl;
    std::cout << "initializer_list  is :" << std::endl;

    for_each(r.begin(), r.end(), [](T v){
        std::cout << v << std::endl;
    });
}

template <typename ... T>
auto Sum(T ... args)
{
    return (args + ...);
}


template <typename T, int nSize>
class MyBuf
{
public:
    virtual ~MyBuf(){}

private:
    T _m_data[nSize];
};



int main()
{
    myprintf(1, 2, "666", 234.9234, 'c', true);

    std::cout << "--------" << std::endl;
    myprintf2(1, 2, "666", 234.9234, 'c', true);
    std::cout << "--------" << std::endl;

    myprintf3(1, 2, "666", 234.9234, 'c', true);

    std::cout << "--------" << std::endl;
    std::cout <<"sum : " << Sum(9, 1, 99, 1.123) << std::endl;


    MyBuf<int, 100> buf;
    std::cout << "sizeof(buf) is " << sizeof(buf) << std::endl;

    std::cout <<"sizeof(char *) is " <<  sizeof(char *) << std::endl;
    std::cout << "sizeof(int): " << sizeof(int) << std::endl;
    std::cout << "sizeof(short): " << sizeof(short) << std::endl;
    std::cout << "sizeof(long): " << sizeof(long) << std::endl;
    std::cout << "sizeof(long long): " << sizeof(long long) << std::endl;
    std::cout << "sizeof(float): " << sizeof(float) << std::endl;
    std::cout << "sizeof(double): " << sizeof(double) << std::endl;


    return 0;
}
