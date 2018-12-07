#define _CRT_SECURE_NO_WARNINGS  

/**
*Date: 2018/12/07 22:17
*Author:yqq
*Descriptions:	
	每隔一秒刷新一下游戏玩家分数排行榜

	ShowRank 和  UseRedis  分开编译, 生成两个可执行文件
*/


#include "use_redis.h"
#ifdef _WIN32
#include <windows.h>
#else
#include <unistd.h>
#endif

const char *IP = "192.168.10.119";
const int PORT = 6379;

//显示玩家排行榜
void showRank()
{
	redisContext * pConn = redisConnect(IP, PORT);
	if (NULL == pConn)
	{
		printf("redisConnect err\n");
		return;
	}

	while (1)
	{
#ifdef _WIN32
		Sleep(1000); //休眠1秒
#else //linux
		sleep(1); //休眠1秒
#endif
		redisReply *pRet = (redisReply *)redisCommand(pConn, "zrevrange players 0 5 withscores"); //获取前五
		if (NULL == pRet)
		{
			printf("获取前五失败\n");
			continue;
		}
		printf("======================\n");
		int i = 0;
		for (i = 0; i < pRet->elements; i++)
		{
			std::cout << pRet->element[i]->str << std::endl;
		}
		printf("======================\n");
	}
}



#if  0 //分开编译, 生成新的可执行文件, 
int main()
{
	showRank();
#if 0
	Redis *r = new Redis();
	if (!r->connect("192.168.10.119", 6379))
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
#endif
