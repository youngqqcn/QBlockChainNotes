
// //yqq

// #include <iostream>
// #include <algorithm>
// #include <string>
// #include <thread>
// #include <mutex>
// #include <condition_variable>
// #include <queue>
// #include <random>
// #include <chrono>
// #include <future>
// #include <atomic>
// // #include <boost/lockfree/queue.hpp> 

// using namespace std;

// int main()
// {

//     std::queue<double>   qMsgs;
//     std::condition_variable cv;
//     std::mutex  mtx;
//     // std::atomic_bool atomIsFull;
//     // std::atomic_bool atomIsEmpty; 


//     const int nConsumers = 5;
//     const int nProducer = 3;

//     auto producer = [&](){
//         std::default_random_engine  e;
//         // std::uniform_int_distribution<int> ud(e);
//         std::normal_distribution<> nd(-2342.234932, 99999.999924);
//         while(true)
//         {
//             {
//             std::cout << " producer[" << std::this_thread::get_id() << "] producing one item" << std::endl;
//             std::unique_lock<std::mutex> lock(mtx);
//             for(int i = 0; i < nConsumers; i++)
//             {
//                 qMsgs.push(nd(e));
//             }
//             //cv.notify_one();
//             cv.notify_all();
//             atomItemCount ++;
//             }
            
//             std::this_thread::sleep_for(std::chrono::milliseconds(100));
//         }
//     };

//     auto consumer = [&]() {
//         std::cout << "thread " << std::this_thread::get_id() << "  started"  << std::endl;
//         while(!qMsgs.empty())
//         {
//             {
//             std::unique_lock<std::mutex>  lock(mtx);
//             // while( !atomIsFull && !atomIsEmpty  )
//             {
//                 cv.wait(lock);
//             }
//             std::cout <<  " consumer[" << std::this_thread::get_id() \
//                 << "] consuming: " <<  qMsgs.front()  << std::endl;
//             qMsgs.pop();
            
//             }
//             std::this_thread::yield();
           
//             // std::this_thread::sleep_for(std::chrono::milliseconds(100));
//         }
//     };


//     auto proFuture = std::async(producer);
//     std::vector<decltype(proFuture)> vctPros;
//     vctPros.push_back( std::move(proFuture) );
//     for(int i = 0; i < nProducer - 1; i++  )
//     {
//         vctPros.push_back(std::move( std::async(producer)  ));
//     }


//     auto f =  std::async(consumer);
//     std::vector<decltype(f)> vctFutures;
//     vctFutures.push_back(std::move(f));
//     for(int i = 0; i < nConsumers - 1; i++)
//     {
//         vctFutures.push_back(std::move(std::async(consumer) ));
//     }

//     while(true)
//     {
//         std::cout << "main thread  " << std::endl;
//         std::this_thread::sleep_for(std::chrono::seconds(10));
//     }

//     return 0;
// }
