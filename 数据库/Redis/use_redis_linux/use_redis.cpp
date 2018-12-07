#include "use_redis.h"
#ifdef _WIN32
#include <windows.h>
#else
#include <unistd.h>
#endif


void showRank()
{
	redisContext * pConn = redisConnect("192.168.10.119", 6379);
	if (NULL == pConn)
	{
		printf("redisConnect err\n");
		return ;
	}

	while(1)
	{
#ifdef _WIN32
		Sleep(1000); //休眠1秒
#else //linux
		sleep(1); //休眠1秒
#endif
		redisReply *pRet = (redisReply *)redisCommand(pConn, "zrevrange players 0 5 withscores");
		if(NULL == pRet)
		{
			printf("获取前五失败\n");
			continue;
		}
		printf("======================\n");
		int i =0; 
		for(i = 0; i < pRet->elements; i++)
		{
			std::cout << pRet->element[i]->str << std::endl;
		}
		printf("======================\n");
	}
}




int main()
{
	showRank();
#if 0
	   Redis *r = new Redis();
	   if(!r->connect("192.168.10.119", 6379))
	   {
	   printf("connect error!\n");
	   return 0;
	   }
	   r->set("name", "Andy");
	   printf("Get the name is %s\n", r->get("name").c_str());
	   delete r;
#endif
	return 0;
}

