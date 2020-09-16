#include <boost/thread/thread.hpp> 
#include <iostream> 

void hello() 
{ 
    std::cout <<         "Hello world, I''m a thread!"  << std::endl; 
} 

int main(int argc, char* argv[]) 
{ 
    boost::thread thrd(&hello); 
    thrd.join(); 
    return 0; 

}
