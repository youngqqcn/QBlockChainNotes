
#include <iostream>
#include <thread>
#include <queue>
#include <memory>
#include <mutex>
#include <condition_variable>
#include <string>
#include <sstream>
#include <chrono>
#include <atomic>

using namespace std;

template<typename T>
class threadsafe_queue
{
private:
  mutable std::mutex mut;  // 1 互斥量必须是可变的 
  std::queue<T> data_queue;
  std::condition_variable data_cond;
public:
  threadsafe_queue()
  {}
  threadsafe_queue(threadsafe_queue const& other)
  {
    std::lock_guard<std::mutex> lk(other.mut);
    data_queue=other.data_queue;
  }

  void push(T new_value)
  {
    std::lock_guard<std::mutex> lk(mut);
    data_queue.push(new_value);
    data_cond.notify_one();
  }

    /**
     * wait()会去检查这些条件(通过调用所提供的lambda函数)，
     * 当条件满足(lambda函数返回true)时返回。如果条件不满足(lambda函数返回false)，
     * wait()函数将解锁互斥量，并且将这个线程(上段提到的处理数据的线程)置于阻塞或等待状态。
     * 当准备数据的线程调用notify_one()通知条件变量时，处理数据的线程从睡眠状态中苏醒，
     * 重新获取互斥锁，并且再次检查条件是否满足。在条件满足的情况下，从wait()返回并继续持有锁；
     * 当条件不满足时，线程将对互斥量解锁，并且重新开始等待。这就是为什么用std::unique_lock而
     * 不使用std::lock_guard——等待中的线程必须在等待期间解锁互斥量，并在这之后对互斥量再次上锁，
     * 而std::lock_guard没有这么灵活。如果互斥量在线程休眠期间保持锁住状态，
     * 准备数据的线程将无法锁住互斥量，也无法添加数据到队列中；同样的，等待线程也永远不会知道条件何时满足。
     */
    void wait_and_pop(T& value)
    {
        std::unique_lock<std::mutex> lk(mut);
        data_cond.wait(lk,[this]{return !data_queue.empty();});
        value=data_queue.front();
        data_queue.pop();
    }

  std::shared_ptr<T> wait_and_pop()
  {
    std::unique_lock<std::mutex> lk(mut);
    data_cond.wait(lk,[this]{return !data_queue.empty();});
    std::shared_ptr<T> res(std::make_shared<T>(data_queue.front()));
    data_queue.pop();
    return res;
  }

  bool try_pop(T& value)
  {
    std::lock_guard<std::mutex> lk(mut);
    if(data_queue.empty())
      return false;
    value=data_queue.front();
    data_queue.pop();
    return true;
  }

  std::shared_ptr<T> try_pop()
  {
    std::lock_guard<std::mutex> lk(mut);
    if(data_queue.empty())
      return std::shared_ptr<T>();
    std::shared_ptr<T> res(std::make_shared<T>(data_queue.front()));
    data_queue.pop();
    return res;
  }

  bool empty() const
  {
    std::lock_guard<std::mutex> lk(mut);
    return data_queue.empty();
  }
};





#if 0
int main()
{
    threadsafe_queue<std::string>   q;
    // std::condition_variable condvarFinished;
    //std::atomic_flag  finishedFlag(false);
    std::atomic_bool   finishedFlag = false;

    std::thread   t1([&](){

        for(int i = 0; i < 1000; i++){
            std::ostringstream  fmts;
            fmts << "this is " << i;

            std::this_thread::sleep_for( std::chrono::microseconds( 10 ) );
            std::cout << "push " << i << std::endl;
            q.push(fmts.str());
        }

        finishedFlag = true;

        std::cout << "productor finished..." << std::endl;

    });


    std::thread t2([&](){

        while(!finishedFlag){
            std::string strTmp = "";
            q.wait_and_pop(strTmp);
            std::cout << "got :" << strTmp << std::endl;
        }

        std::cout << "consumer finished..." << std::endl;

    });

    if(t1.joinable())
        t1.join();
    
    if(t2.joinable())
        t2.join();

    return 0;
}
#endif
