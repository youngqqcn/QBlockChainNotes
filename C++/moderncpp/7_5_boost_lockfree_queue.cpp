//yqq

#include <iostream>
#include <algorithm>
#include <string>
#include <boost/lockfree/spsc_queue.hpp>
#include <boost/thread/thread.hpp>
#include <boost/container/vector.hpp>
#include <boost/thread/future.hpp>
#include <boost/random.hpp>
#include <boost/move/move.hpp>
#include <boost/container/deque.hpp>
// #include <boost/thread/a
#include <boost/thread/mutex.hpp>

using namespace std;

// void foo()
// {
//     for (int i = 0; i < 10; i++)
//     {
//         std::cout << "sub thread" << std::endl;
//     }
// }


int main()
{
    using boost::thread;
    using boost::container::vector;
    // using boost::
    // using boost::lockfree::queue ;
    using boost::lockfree::spsc_queue;
    // using boost::move;
    // using boost::random;

    spsc_queue<double> lockfreeQueue(100000000);
    // boost::container::deque<double> lockfreeQueue;
    const int cnProducer = 10, cnConsumer = 10;

    boost::mutex  mtx;

    vector<thread> vctProducer;
    const double pi = 3.14159261314;

    for (int i = 0; i < cnProducer; i++)
    {
        vctProducer.push_back( boost::move( thread([&pi, &lockfreeQueue, &mtx]() {
            for (int i = 0; i < 10000000; i++)
            {
                // std::cout << "sub thread" << std::endl;
                lockfreeQueue.push( pow(i, 3) * pi / 2  );

                // boost::lock_guard<boost::mutex>  lock(mtx);
                // lockfreeQueue.push_back( pow(i, 3) * pi / 2  );
            }
        })));
    }

    for(auto &thd : vctProducer)
    {
        thd.join();
    }


    return 0;
}


// g++ 7_5_boost_lockfree_queue.cpp -lpthread -lboost_thread