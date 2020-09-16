#include <iostream>
#include <memory>
#include <string>

int main(int argc, char const *argv[])
{
    // ISO C++ forbids converting a string constant to ‘char*’
    char *p = "this is const string"; 
    char pStr[] = "this is test";

    // warning: ‘template<class> class std::auto_ptr’ is deprecated
    std::auto_ptr<std::string> pAuto( new std::string("hello"));

    //使用 unique_ptr 取代 auto_ptr
    std::unique_ptr<std::string> pUnique(new std::string("hellow"));


    //C语言风格的类型转换被弃用, static_cast、reinterpret_cast、const_cast 来进行类型转换。
    uint32_t *pInt = reinterpret_cast<uint32_t*>(new int(10));
    int *pTmpInt = new int(10);
    // uint32_t *pInt = static_cast<uint32_t*>(pTmpInt);


    return 0;
}
