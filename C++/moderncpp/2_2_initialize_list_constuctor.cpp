//yqq

#include <iostream>
#include <algorithm>
#include <initializer_list>
#include <vector>

using namespace std;



class MyClass
{
private:
    std::vector<int> _m_vctNumber;

public:
    MyClass(std::initializer_list<int> list)
    {
        for(auto &item : list)
        {
            _m_vctNumber.push_back(item);
        }
    }

    void Show()
    {
        for(const auto &item: _m_vctNumber)
        {
            std::cout << item << std::endl;
        }
    }

};



int main()
{
    MyClass  mcl({1, 4, 9});
    mcl.Show();


    return 0;
}
