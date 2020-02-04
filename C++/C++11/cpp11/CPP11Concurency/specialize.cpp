
/**
 *  模板偏特化
 */

#include <iostream>

using namespace std;

template<typename T1,typename T2>
class Test
{
public:
    Test(T1 i,T2 j):a(i),b(j){cout<<"模板类"<<endl;}
private:
    T1 a;
    T2 b;
};

//必须有  上面泛化  才能有下面的 偏特化
template<typename T1,typename T2> //这是范围上的偏特化
class Test<T1*,T2*>
{
public:
    Test(T1* i,T2* j):a(i),b(j){cout<<"指针偏特化"<<endl;}
private:
    T1* a;
    T2* b;
};

/*
int main()
{

    return 0;
}
*/