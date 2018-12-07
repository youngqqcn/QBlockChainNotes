// UseRedis.cpp : 定义控制台应用程序的入口点。
//
/**
*Date: 2018/12/07 22:26
*Author:yqq
*Descriptions:
	使用redis  模拟实现  游戏实时排行榜

注意:
	LINK error 2038 错误
		1.直接编译redis-server即可, 会生成相应的静态库,  注意本程序使用的是 release版静态库 还是  debug版静态库, 
		2.编译的时候注意设置  属性>>C++>>代码生成>>运行库 (Release设为MT,  Debug设置为 MdT)


	linux环境下:
		1.make  然后 make install
		2.将 动态库路径加入   ~/.profile中  然后  source ~/.profile  使其生效
		
		将/usr/local/lib 添加到环境变量中  , 编辑  ~/.profile 加入以下内容
			export APTH=$PATH:/usr/local/lib
			export LD_LIBRARY_PATH=/usr/local/lib:$LD_LIBRARY_PATH
*/

#include "stdafx.h"
#include <stdlib.h>
#include <time.h>
#include <memory>
#include <string>
#include <vector>
#include <windows.h>
#include "use_redis.h"

using namespace std;

Redis *gRh = NULL;
int testRedis();
int testOther();

DWORD WINAPI ShowRank(LPVOID lpThreadParameter);
BOOL bOver = FALSE;
const int PLAYER_COUNTS = 1000;
const int GAME_ROUNDS = 100;
void MyGame()
{
	/*
	1.生成100,000名游戏玩家
	2.随机每局(每次生成随机数)  ==> 每局的分数
	3.另外一个可执行程序  每隔 1s, 刷新一次分数排行榜

	思路:  使用 redis的   sorted set 即可
	zrevrange 
	*/

	redisContext * pConn = redisConnect("127.0.0.1", 6379);
	if (NULL == pConn)
	{
		printf("redisConnect err\n");
		return ;
	}


	//1.生成玩家
	redisReply *pRet = NULL;
	for (int i = 0; i < PLAYER_COUNTS; i++)
	{
		pRet = (redisReply *)redisCommand(pConn, "zadd players %d player%d", 0, i);
		if (NULL == pRet)
		{
			printf("生成玩家失败\n");
			return;
		}
	}

#ifdef MT
	HANDLE hThread = ::CreateThread(NULL, 0, ShowRank, NULL, 0, NULL);
	if (NULL == hThread)
	{
		printf("创建子线程失败\n");
		return;
	}
#endif

	//2.玩10000局
	srand((int)time(NULL));
	for (int i = 0; i < GAME_ROUNDS; i++)
	{
		for (int iPlayer = 0; iPlayer < PLAYER_COUNTS; iPlayer++)
		{
			int iScore = rand() % 100;
			pRet = (redisReply *)redisCommand(pConn, "zscore players player%d", iPlayer);
			if (NULL == pRet)
			{
				printf("获取历史分数失败\n");
				return;
			}
			int iOldScore = atoi(pRet->str);
			pRet = (redisReply *)redisCommand(pConn, "zadd players %d player%d", iOldScore + iScore, iPlayer);
			if (NULL == pRet)
			{
				printf("更新玩家分数失败\n");
				return;
			}
			
		}
	}

	bOver = TRUE;

#ifdef MT
	//等待子线程结束
	WaitForSingleObject(hThread, INFINITE);
#endif
}



//使用线程方式,  总是获取不到前五, 不知道什么原因, 后面再研究
#ifdef MT
DWORD WINAPI ShowRank(LPVOID lpvoid)
{

	redisContext * pConn = redisConnect("127.0.0.1", 6379);
	if (NULL == pConn)
	{
		printf("ShowRank() redisConnect err\n");
		return 0;
	}

	while (!bOver)
	{
		Sleep(1000);
		redisReply *pRet = (redisReply *)redisCommand(pConn, "zrevrange players 0 5 withscores");  //前5
		if (NULL != pRet)
		{
			printf("获取前五失败\n");
			continue;
			//return 0;
		}

		printf("=======================\n");
		for (int i = 0; i < pRet->elements && !bOver; i++)
		{
			std::cout << pRet->element[i]->str << std::endl;
		}
		printf("=======================\n");

	}
	printf("子线程正常退出");

	return 0;
}
#endif



int main()
{
	//testRedis();
	//testOther();

	MyGame();

	system("pause");
    return 0;
}






int testRedis()
{
	Redis *r = new Redis();
	if (!r->connect("127.0.0.1", 6379))
	{
		printf("connect error!\n");
		return 0;
	}
	r->set("name", "Andy");
	printf("Get the name is %s\n", r->get("name").c_str());

	gRh = r;
	delete r;
	return 0;
}


int testOther()
{
	redisContext * pConn = redisConnect("127.0.0.1", 6379);
	if (NULL == pConn)
	{
		printf("redisConnect err\n");
		return 0;
	}

	redisReply * pRet = (redisReply *)redisCommand(pConn, "sadd qvs 1 2 3 4 5");  //执行redis命令
	if (NULL == pRet)
	{
		printf("redisCommand err\n");
		return 0;
	}

	pRet = (redisReply *)redisCommand(pConn, "smembers qvs");
	if (NULL == pRet)
	{
		printf("redisCommand err\n");
		return 0;
	}

	for (int i = 0; i < pRet->elements; i++)
	{
		//str>str << std::endl;
		std::cout << pRet->element[i]->str << std::endl;
	}
}
