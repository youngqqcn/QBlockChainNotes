//yqq

#include <iostream>
#include <algorithm>
#include <array>
#include <list>
#include <forward_list>

using namespace std;

int main()
{

    std::array<int, 4> arr = {1, 2, 4, 5};
    if( arr.empty() )
    {
        std::cout << "is empty" << std::endl;
    }

    std::cout << "size : " << arr.size() << std::endl;


    for(auto &item : arr)
    {
        std::cout << item << std::endl;
    }



    std::forward_list<std::string>  flstStrings;
    flstStrings.push_front("hello1");
    flstStrings.push_front("hello2");
    flstStrings.push_front("hello3");
    flstStrings.push_front("hello4");

    for(auto item : flstStrings)
    {
        std::cout << item << std::endl;
    }




    std::sort(arr.begin(), arr.end(), [](int a, int b) -> bool {
        return a > b; // > : 大的在前   < : 小的在前
    });
    std::for_each(arr.begin(), arr.end(), [](int n){
        std::cout <<  n  << " \t ";
    });
    std::cout << std::endl;
    
    


    return 0;
}
