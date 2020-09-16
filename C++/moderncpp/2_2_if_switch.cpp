//yqq

#include <iostream>
#include <algorithm>
#include <vector>

using namespace std;
int main()
{
    std::vector<int> vctNums ({1, 2, 3, 4});
    auto it2 = std::find(vctNums.begin(), vctNums.end(), 2); //vctNums.find(2);
    if(vctNums.end() != it2)
    {
        *it2 = 4;
    }

    for_each(vctNums.begin(), vctNums.end(), [](int n){
        std::cout << n << std::endl;
    });


    std::cout << "------use c++17--------" << std::endl;
    // c++17 可以将在if语句中声明临时变量
    if(auto it = std::find(vctNums.begin(), vctNums.end(), 3 ); it != vctNums.end())
    {
        *it = 99;
    }
    
    std::for_each(vctNums.begin(), vctNums.end(), [](int n){
        std::cout << n << std::endl;
    }); 

    return 0;
}
