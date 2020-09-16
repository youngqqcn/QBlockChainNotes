//yqq

#include <iostream>
#include <algorithm>
#include <string>
#include <regex>

using namespace std;

int main()
{

    std::string fnames[] = {"foo.txt", "bar.txt", "test", "a0.txt", "AAA.txt"};

    //std::regex txt_regex("[a-z]+\\.txt");
    std::regex txt_regex(R"([a-z]+\.txt)"); // C++11 的原生字符串
    for (const auto &fname: fnames)
    {
        std::cout << fname << ": " << std::regex_match(fname, txt_regex) << std::endl;
    }


    


    return 0;
}
