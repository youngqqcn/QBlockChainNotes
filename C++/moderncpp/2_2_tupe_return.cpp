//yqq

#include <iostream>
#include <algorithm>
#include <tuple>

using namespace std;

std::tuple<int, double, std::string> f() {
    return std::make_tuple(1, 2.3, "456");
}

int main()
{
    auto [x, y, z] = std::make_tuple(1, "sddd", 3.999);  //C++17 ok
    // auto [x, y, z] = f();
    std::cout << x << ", " << y << ", " << z << std::endl;

    return 0;
}
