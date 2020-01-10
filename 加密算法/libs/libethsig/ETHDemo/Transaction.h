//author: yqq
//date:2019-04-18
//desc: 
//     以太坊交易创建与签名,  参考 cpp-ethereum



#pragma once
#include <stdio.h>
#include <stdlib.h>
#include <string.h>
#include <string>
#include <iostream>


#ifdef MY_DLL_API
#define MY_DLL_API __declspec(dllexport)
#else
#define MY_DLL_API __declspec(dllimport)

#endif







#define  WEI		(1)
#define  KWEI		(1000 * WEI)
#define  MWEI		(1000 * KWEI)
#define  GWEI		(1000 * MWEI)
#define  MICROETHER (1000 * GWEI)				//微ether
#define  MILLIETHER (1000 * MICROETHER)			//毫ether
#define  ETHER		(1000 * MILLIETHER)			//ether

#define	 STR_GWEI_0_SUFFIX				("000000000")		//
#define  UINT_MAX_WITHDRAW_AMOUNT		(9999)
#define  FLOAT_MIN_WITHDRAW_AMOUNT		(0.00000001)



namespace eth
{
	enum ETHChainID
	{
		None = 0,
		Mainnet = 1,
		//EXPANSE = 2,  //暂时未使用
		Ropsten = 3,
		Rinkeby = 4,
		Goerli = 5,
		Kovan = 42,
		EthereumClassic=61, //增加ETC支持   2020-01-10 
		Geth_Private_Chains = 1337 //geth私链默认id
	};


	typedef struct _EthTxData
	{
		explicit _EthTxData()
		{
			uChainId = ETHChainID::None;
			pszNonce = NULL;
			pszGasStart = NULL;
			pszValue = NULL;
			pszGasPrice = NULL;
			pData = NULL;
			pszAddrTo = NULL;
		}

		ETHChainID			uChainId;				//chainId , 
		char				*pszNonce;				//nonce , 通过节点的 eth.getTransactionCount rpc接口获取nonce
		char				*pszValue;				//value, 金额, 单位:wei
		char				*pszGasPrice;			//gasprice,  单位:wei
		char				*pszGasStart;			//gasstart , 单为:wei
		unsigned char		*pData;					//data附加数据, 是十六进制编码的, 此字段默认为空!
		unsigned int		uDataLen;				//data长度
		//std::string		strAddrTo;				//目的地址    //不要使用 STL
		char				*pszAddrTo;				//目的地址
	}EthTxData;




	struct MY_DLL_API Transaction
	{
		enum ETH_ERRCODE
		{
			ETH_NO_ERROR = 0,

			ETH_ERR_BadRLP = 95,
			ETH_ERR_ErrChainID = 96, //错误的chainID
			ETH_ERR_SECP256K1_ECDSA_SIGN_RECOVERABLE_faild = 97, //函数调用失败
			ETH_ERR_INVALID_SIG = 99, //无效签名

		};

		/*enum FIELD_POS
		{
			pos_nonce = 0,
			pos_receive_addr,
			pos_value,
			pos_gaslimit,
			pos_gasprice,
			pos_data,
			pos_v,
			pos_r,
			pos_s
		};*/


		
		//@warning: DLL接口不要使用 STL, 即不要用(std::string, std::vector, std::list, ...等等)
		static int Sign(const EthTxData &ethTxData, const char *pszPrivKey, unsigned char *pOutBuf, unsigned int uBufLen,  unsigned int *puOutLen);


	};




	enum PricisionLevel
	{
		//LEVEL_WEI = 0,
		ETH_LEVEL_GWEI,
		//LEVEL_KWEI,
		//LEVEL_MWEI,
		//LEVEL_GWEI,
		//LEVEL_MICROETHER,
		//LEVEL_MILLIETHER,
		//LEVEL_ETHER
	};


	//功能描述: 将ether换算为 wei
	//注意:
	//dValue的最大值(不会导致整型溢出)计算方法:
	//>>> 1.0 * (2**64 - 1) / (10**9)
	//18446744073.709553      
	//保留小数点后8位, 即 0.00000001   , 如果超出则舍去!
	inline int EtherToWei(double dValue, std::string &strValueWei, PricisionLevel uPrecisionLevel = ETH_LEVEL_GWEI)
	{
		if (dValue > UINT_MAX_WITHDRAW_AMOUNT || dValue < FLOAT_MIN_WITHDRAW_AMOUNT)
		{
			return 1;
		}

		switch (uPrecisionLevel)
		{
		case ETH_LEVEL_GWEI:
		{
			unsigned long long int  ullValue = (unsigned long long int)(dValue * GWEI);
			char buf[100] = { 0 };
			memset(buf, 0, sizeof(buf));
			sprintf(buf, "%llu", ullValue);
			strValueWei = std::string(buf) + STR_GWEI_0_SUFFIX;  //补9个0
		}
		break;
		default:
			return 2;
			break;
		}

		if (strValueWei.empty())
		{
			return 3;
		}
		return 0;
	}

}



