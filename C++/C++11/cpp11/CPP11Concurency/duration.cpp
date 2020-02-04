#include <condition_variable>
#include <mutex>
#include <chrono>
#include <iostream>
#include <thread>

std::condition_variable cv;
bool done = false;
std::mutex m;


void worker()
{
    for(int i = 0; i < 10; i++)
    {
        std::this_thread::sleep_for( std::chrono::milliseconds(300) );
        cv.notify_all(); //通知所有
        //cv.notify_one();
    }
    done  = true;
}


bool wait_loop()
{
  auto const timeout= std::chrono::steady_clock::now()+
      std::chrono::milliseconds(500);
  std::unique_lock<std::mutex> lk(m);
  while(!done)
  {
    std::cv_status   cvStatus  = cv.wait_until( lk, timeout );
    if(std::cv_status::timeout == cvStatus)
    {
        std::cout <<  std::this_thread::get_id()  << " timeout" << std::endl;
        break;
    }
    else if(std::cv_status::no_timeout == cvStatus)
    {
        std::cout << "waited condition_variable" << std::endl;
        break;
    }
    else{}

  }
  return done;
}

#if 0
int main()
{
    //wait_loop();
    std::thread t1(  wait_loop );
    std::thread t11(  wait_loop );
    std::thread t111(  wait_loop );
    std::thread  t2( worker );

    t1.join();
    t11.join();
    t111.join();
    t2.join();

    return 0;
}
#endif