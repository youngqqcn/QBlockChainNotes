//yqq

#include <iostream>
#include <algorithm>
// #include <unordered_map>
#include <unordered_map>
#include <unordered_set>

using namespace std;


//  std::map / std::multimap / std::set / std::multiset   内部使用红黑树, 内部会进行排序  , 插入和搜索的时间复杂度为  O(log(n))
//  std::unordered_map / std::unordered_multimap  / std::unordered_set / std::unordered_multiset   是用 HashTable 实现,  插入和搜索的时间复杂度为  O(1)



int main()
{

    std::unordered_map<std::string, std::string>   mapInfo;
    mapInfo.insert( std::make_pair("boy1", "joke"));
    mapInfo.insert( std::make_pair("boy2", "Kobe"));
    mapInfo.insert( std::make_pair("boy3", "Map"));


    std::for_each(mapInfo.begin(), mapInfo.end(), [](auto item){ // C++14 支持自动推导
        std::cout <<  item.first  << " : " << item.second << std::endl;
    });


    std::unordered_multimap<std::string, std::string> mapMulMap; 
    mapMulMap.insert( std::make_pair("boy1", "joke"));
    mapMulMap.insert( std::make_pair("boy1", "Kobe"));
    mapMulMap.insert( std::make_pair("boy1", "Map"));
    std::for_each(mapMulMap.begin(), mapMulMap.end(), [](auto item){ // C++14 支持自动推导
        std::cout <<  item.first  << " : " << item.second << std::endl;
    });

    return 0;
}
