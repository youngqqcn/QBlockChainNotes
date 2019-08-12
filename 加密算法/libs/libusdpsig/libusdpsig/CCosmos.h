/************************************************************************
作者: yqq
日期: 2019-05-08  14:25
说明: Cosmos类币的签名库  支持 (USDP, HTDF)
************************************************************************/

#ifndef _CCOSMOS_H_
#define  _CCOSMOS_H_


#include <iostream>
#include <string>
#include <vector>

#include "cryptopp/base64.h"  //base64 


#include <boost/format.hpp>
#include <boost/algorithm/string.hpp>
using namespace std;

namespace cosmos
{




#define  UINT_MAX_FEE_AMOUNT	(100)		//最大交易手续费
#define  UINT_MIN_FEE_AMOUNT	(1)			//最大交易手续费
#define  UINT_MAX_GAS_AMOUNT	(200000000) //最大gas
#define  UINT_MIN_GAS_AMOUNT	(200)		//最大gas
#define  UINT_ADDR_LEN			(43)		//地址长度 
#define  UINT_PRIV_KEY_LEN		(32)		//128 (r , s) 签名信息, 组装后的长度
#define  UINT_PUB_KEY_LEN		(33)		//公钥长度(33字节)
#define  UINT_SIG_RS_LEN		(64)		//128 (r , s) 签名信息, 组装后的长度

#define  STR_MAINCHAIN			"mainchain"
#define  STR_TESTCHAIN			"testchain"

#define  STR_USDP				"usdp"
#define  STR_HTDF				"htdf"

#define  STR_BROADCAST_TYPE		"auth/StdTx"
#define  STR_BROADCAST_MSG_TYPE "htdfservice/send"
#define  STR_BROADCAST_PUB_KEY_TYPE "tendermint/PubKeySecp256k1"



	enum ErrorCode
	{
		NO_ERROR  = 0,
		ARGS_ERROR = 1001,
		ECCSIGN_STEP1_ERROR = 1005,
		ECCSIGN_STEP2_ERROR = 1006
	};



typedef unsigned long long int uint64_t;
typedef unsigned int uint32_t;


// BASE64编码
inline std::string BytesToBase64(const CryptoPP::byte *s, unsigned int s_len)
{
	std::string encoded;

	CryptoPP::StringSource ss(s, s_len, true, new CryptoPP::Base64Encoder(new CryptoPP::StringSink(encoded), false/*不要插入换行符*/, 0xFFFFF));
	return encoded;
}


inline std::string BytesToBase64(const std::string &s)
{
	std::string encoded;

	CryptoPP::StringSource ss(s,  true, new CryptoPP::Base64Encoder(new CryptoPP::StringSink(encoded), false/*不要插入换行符*/, 0xFFFFF));
	return encoded;
}

inline std::string BytesToBase64(const char *pszIn)
{
	std::string encoded;

	CryptoPP::StringSource ss(pszIn,  true, new CryptoPP::Base64Encoder(new CryptoPP::StringSink(encoded), false/*不要插入换行符*/, 0xFFFFF));
	return encoded;
}




// BASE64解码
inline std::string Base64ToBytes(const CryptoPP::byte *s, unsigned int s_len)
{
	std::string decoded;

	CryptoPP::StringSource ss(s, s_len, true, new CryptoPP::Base64Decoder(new CryptoPP::StringSink(decoded)));
	return decoded;
}

inline std::string Base64ToBytes(const char  *pszIn)
{
	std::string decoded;

	CryptoPP::StringSource ss(pszIn,  true, new CryptoPP::Base64Decoder(new CryptoPP::StringSink(decoded)));
	return decoded;
}



inline std::string Base64ToBytes(const std::string &s)
{
	std::string decoded;

	CryptoPP::StringSource ss(s,  true, new CryptoPP::Base64Decoder(new CryptoPP::StringSink(decoded)));
	return decoded;
}



	
/*要签名的数据
{
	"account_number": "12",		//需从节点获取
	"chain_id": "mainchain",	//testchain或mainchain
	"fee": {
		"amount": [{
			"amount": "20",		//手续费金额
			"denom": "usdp"		//币种	
		}],
		"gas": "200000"			//gasprice??
	},
	"memo": "",					//备注
	"msgs": [{	
		"Amount": [{
			"amount": "66",		//转账金额
			"denom": "usdp"		//币种
		}],
		"From": "usdp15havmvnt4ygfyfuqm32aecth7p8800f6pkf652",	//源地址
		"To": "usdp1vmsfd7rly9chhjpaalr55q5886lnva99ghlesg"		//目的地址
	}],
	"sequence": "4"				//交易次数? 
}
*/
struct CsRawTx
{
	uint64_t	uAccountNumber;
	char		szChainId[128];
	uint64_t	uFeeAmount;
	char		szFeeDenom[128];
	uint64_t	uGas;
	char		szMemo[1024];
	uint64_t	uMsgAmount;
	char		szMsgDenom[128];
	char		szMsgFrom[128];
	char		szMsgTo[128];
	uint64_t	uSequence;

	CsRawTx()
	{
		uAccountNumber = INTMAX_MAX; //((0x1 << 32) - 1);
		memset(szChainId, 0, sizeof(szChainId));
		uFeeAmount = 0;
		memset(szFeeDenom, 0, sizeof(szFeeDenom));
		uGas = 0;
		memset(szMemo, 0, sizeof(szMemo));
		uMsgAmount = 0;
		memset(szMsgDenom, 0, sizeof(szMsgDenom));
		memset(szMsgFrom, 0, sizeof(szMsgFrom));
		memset(szMsgTo, 0, sizeof(szMsgTo));
		uSequence = INTMAX_MAX;
	}

	CsRawTx(const CsRawTx & other)
	{
		uAccountNumber = other.uAccountNumber;
		memcpy(szChainId, other.szChainId, sizeof(szChainId));
		uFeeAmount = other.uFeeAmount;
		memcpy(szFeeDenom, other.szFeeDenom, sizeof(szFeeDenom));
		uGas = other.uGas;
		memcpy(szMemo, other.szMemo, sizeof(szMemo));
		uMsgAmount = other.uMsgAmount;

		memcpy(szMsgDenom, other.szMsgDenom, sizeof(szMsgDenom));
		memcpy(szMsgFrom, other.szMsgFrom, sizeof(szMsgFrom));
		memcpy(szMsgTo, other.szMsgTo, sizeof(szMsgTo));
		uSequence = other.uSequence;
	}

	CsRawTx& operator = (const CsRawTx &other)
	{
		uAccountNumber = other.uAccountNumber;
		memcpy(szChainId, other.szChainId, sizeof(szChainId));
		uFeeAmount = other.uFeeAmount;
		memcpy(szFeeDenom, other.szFeeDenom, sizeof(szFeeDenom));
		uGas = other.uGas;
		memcpy(szMemo, other.szMemo, sizeof(szMemo));
		uMsgAmount = other.uMsgAmount;

		memcpy(szMsgDenom, other.szMsgDenom, sizeof(szMsgDenom));
		memcpy(szMsgFrom, other.szMsgFrom, sizeof(szMsgFrom));
		memcpy(szMsgTo, other.szMsgTo, sizeof(szMsgTo));
		uSequence = other.uSequence;

		return *this;
	}

	bool ToString( std::string &strOut)
	{
		if (false == this->ParamsCheck(strOut))
		{
			return false;
		}
		strOut.clear();


		std::string  strJson;

		strJson += "{"; //root

		char buf[1024] = { 0 };

		//account_number
		memset(buf, 0, sizeof(buf));
		sprintf_s(buf, "\"account_number\":\"%llu\"", this->uAccountNumber);
		strJson += buf;
		strJson += ",";

		//chain_id
		memset(buf, 0, sizeof(buf));
		sprintf_s(buf, "\"chain_id\":\"%s\"", this->szChainId);
		strJson += buf;
		strJson += ",";

		//fee
		strJson += "\"fee\":{"; 
		memset(buf, 0, sizeof(buf));
		sprintf_s(buf, "\"amount\":[{\"amount\":\"%llu\",\"denom\":\"%s\"}],\"gas\":\"%llu\"", 
						this->uFeeAmount, this->szFeeDenom, this->uGas);
		strJson += buf;
		strJson += "}"; 
		strJson += ",";


		//memo
		memset(buf, 0, sizeof(buf));
		sprintf_s(buf, "\"memo\":\"%s\"", this->szMemo);
		strJson += buf;
		strJson += ",";

		//msgs  注意是 msgs  不是 msg
		memset(buf, 0, sizeof(buf));
		sprintf_s(buf, "\"msgs\":[{\"Amount\":[{\"amount\":\"%llu\",\"denom\":\"%s\"}],\"From\":\"%s\",\"To\":\"%s\"}]", 
					this->uMsgAmount, this->szMsgDenom, this->szMsgFrom, this->szMsgTo);
		strJson += buf;
		strJson += ",";

		//sequence
		memset(buf, 0, sizeof(buf));
		sprintf_s(buf, "\"sequence\":\"%llu\"", this->uSequence);
		strJson += buf;


		strJson += "}"; //root 

		strOut = strJson;
		return true;
	}


	bool  ParamsCheck( std::string &strErrMsg  )
	{
		if (INTMAX_MAX == this->uAccountNumber || 0 == this->uAccountNumber)
		{
			strErrMsg = boost::str(boost::format("invalid `account_number`: %llu , must between %llu and %llu.") % this->uAccountNumber % 0 % INTMAX_MAX);
			return false;
		}

		if(!(0 == strcmp(STR_MAINCHAIN, this->szChainId) || 0 == strcmp(STR_TESTCHAIN, this->szChainId) ))
		{
			strErrMsg = boost::str( boost::format("invalid `chain_id`: %s, must be '%s'or '%s' . ") % this->szChainId % STR_MAINCHAIN % STR_TESTCHAIN );
			return false;
		}

		if (UINT_MAX_FEE_AMOUNT < this->uFeeAmount || this->uFeeAmount < UINT_MIN_FEE_AMOUNT)
		{
			strErrMsg =  boost::str(boost::format("invalid `fee amount`, must between %d and %d.") % UINT_MIN_FEE_AMOUNT % UINT_MAX_FEE_AMOUNT  );
			return false;
		}

		if (UINT_MAX_GAS_AMOUNT < this->uGas || this->uGas < UINT_MIN_GAS_AMOUNT)
		{
			strErrMsg = boost::str(boost::format("invalid `fee gas` : %llu, must between %llu and %llu.") % this->uGas  % UINT_MIN_GAS_AMOUNT % UINT_MAX_GAS_AMOUNT );
			return false;
		}

		if (!(0 == strcmp(STR_USDP, this->szFeeDenom) || 0 == strcmp(STR_HTDF, this->szFeeDenom)))
		{
			strErrMsg = boost::str(boost::format("invalid `fee denom` : %s, must be `%s` or `%s`.") % this->szFeeDenom % STR_HTDF % STR_USDP );
			return false;
		}

		if (!(0 == strcmp(STR_USDP, this->szMsgDenom) || 0 == strcmp(STR_HTDF, this->szMsgDenom)))
		{
			strErrMsg = boost::str(boost::format("invalid `msgs amount denom` : %s, must be `%s` or `%s`.") % this->szMsgDenom % STR_HTDF % STR_USDP );
			return false;
		}

		//TODO: 利用 bech32解码地址, 如果bech32解码失败, 则地址错误   //2019-05-09
		if ( UINT_ADDR_LEN != strlen(this->szMsgFrom))
		{
			strErrMsg = boost::str(boost::format("invalid address `msg From`:%s, address length must be %d.") % this->szMsgFrom % UINT_ADDR_LEN );
			return false;
		}

		if ( UINT_ADDR_LEN != strlen(this->szMsgTo))
		{
			strErrMsg = boost::str(boost::format("invalid address `msg To`:%s, address length must be %d.") % this->szMsgTo % UINT_ADDR_LEN );
			return false;
		}

		//检查是否是 'usdp1'开头  或者 'htdf1'开头
		//if (!(this->szMsgFrom == strstr(this->szMsgFrom, this->szMsgDenmo)))
		if(false == boost::starts_with(this->szMsgFrom, std::string(this->szMsgDenom) + "1"))
		{
			//strErrMsg = "invalid address `From`.";
			strErrMsg = boost::str(boost::format( "invalid address `From`:%s.") % this->szMsgFrom);
			return false;
		}

		//检查是否是 'usdp'开头  或者 'htdf'开头
		//if (!(this->szMsgTo == strstr(this->szMsgTo, this->szMsgDenmo)))
		if(false == boost::starts_with(this->szMsgTo, std::string(this->szMsgDenom) + "1"))
		{
			strErrMsg = boost::str(boost::format( "invalid address `To`:%s.") % this->szMsgTo);
			return false;
		}


		if (INTMAX_MAX <= uSequence)
		{
			strErrMsg = "invalid `sequence` , TOO LARGE, this is tx number of the address in the node.";
			return false;
		}

		return true;
	}


};







/*
{
	"type": "auth/StdTx",
	"value": {
		"fee": {
			"amount": [{
				"amount": "20",
				"denom": "usdp"
			}],
			"gas": "200000"
		},
		"memo": "",
		"msg": [{
			"type": "htdfservice/send",   //写死的??
			"value": {
				"Amount": [{
					"amount": "66",
					"denom": "usdp"
				}],
				"From": "usdp15havmvnt4ygfyfuqm32aecth7p8800f6pkf652",
				"To": "usdp1vmsfd7rly9chhjpaalr55q5886lnva99ghlesg"
			}
		}],
		"signatures": [{
			"pub_key": {
				"type": "tendermint/PubKeySecp256k1",
				"value": "A9wn8etkGR2CeeEzkHqGq17gxFtWajDa/aqmPCUVt9cN"    //base64(pubKey)
			},
			"signature": "pnwGIegSXmDHnWHYtA9jBFkFBadmdx9mjNijeuRrwMQ+OJBphHlH/+i2bl/7OUT3usX1P1jR00vB43SS7IgPeQ=="    //base64(r[:] + s[:])
		}]
	}
}
*/
struct CsBroadcastTx
{
	std::string					strType;		//"auth/StdTx"

	CsRawTx						csRawTx;
	std::string					strMsgType;		//"htdfservice/send"
	std::string					strPubKeyType;	//type
	std::string					strPubkeyValue;	//value
	std::string					strSignature;	//signature


	CsBroadcastTx()
	{
		strType				= STR_BROADCAST_TYPE; //"auth/StdTx";
		csRawTx				= CsRawTx();
		strMsgType			= STR_BROADCAST_MSG_TYPE;// "htdfservice/send";
		strPubKeyType		= STR_BROADCAST_PUB_KEY_TYPE ;//"tendermint/PubKeySecp256k1";
		strPubkeyValue		= "";
		strSignature		= "";
	}

	CsBroadcastTx(const CsBroadcastTx &other)
	{
		strType				= other.strType;
		csRawTx				= other.csRawTx;
		strMsgType			= other.strMsgType;
		strPubKeyType		= other.strPubKeyType;
		strPubkeyValue		= other.strPubkeyValue;
		strSignature		= other.strSignature;
	}


	CsBroadcastTx& operator = (const CsBroadcastTx &other)
	{
		strType = other.strType;
		csRawTx = other.csRawTx;
		strMsgType = other.strMsgType;
		strPubKeyType = other.strPubKeyType;
		strPubkeyValue = other.strPubkeyValue;
		strSignature = other.strSignature;

		return *this;
	}



	//转为json, 
	//如果参数检查失败返回 false, strRet携带错误信息
	//如果成功返回 true, strRet是json字符串(不含任何空格,除memo的value外) 且顺序固定不能变
	bool ToString( std::string &strRet )
	{
		std::string strErrMsg;
		if (false == this->ParamsCheck(strErrMsg))
		{
			strRet = strErrMsg;
			return false;
		}

		std::string strJson;
		strJson += "{"; //root

		//type
		strJson += "\"type\":\"" + strType + "\",";
		boost::trim(strJson);

		//value
		strJson += "\"value\":{";//value


		//msg
		strJson += boost::str( boost::format("\
			\"msg\":[{\
				\"type\":\"%s\",\
				\"value\":{\
					\"From\":\"%s\",\
					\"To\":\"%s\",\
					\"Amount\":[{\
						\"denom\":\"%s\",\
						\"amount\":\"%llu\"\
					}]\
				  }\
			}],") % this->strMsgType % this->csRawTx.szMsgFrom % this->csRawTx.szMsgTo \
				% this->csRawTx.szMsgDenom % this->csRawTx.uMsgAmount );


		//fee
		strJson += boost::str( boost::format( "\
				\"fee\":{\
					\"amount\":[{\
						\"denom\":\"%s\",\
						\"amount\":\"%llu\"\
					}],\
					\"gas\":\"%llu\"\
				}," ) % this->csRawTx.szFeeDenom % this->csRawTx.uFeeAmount % this->csRawTx.uGas);


		//signatures
		strJson += boost::str(boost::format("\
			\"signatures\":[{\
				\"pub_key\":{\
					\"type\":\"%s\",\
					\"value\":\"%s\"\
				},\
				\"signature\":\"%s\"\
			}],") % this->strPubKeyType % this->strPubkeyValue % this->strSignature );


		strJson = boost::algorithm::erase_all_copy(strJson, " ");  //去掉空格
		strJson = boost::algorithm::erase_all_copy(strJson, "\t" ); //去掉空格
		strJson = boost::algorithm::erase_all_copy(strJson, "\n"); //去掉空格
		

		//memo 中的空格不能去掉
		strJson += boost::str(boost::format("\"memo\":\"%s\"") % this->csRawTx.szMemo);


		strJson += "}"; //value


		strJson += "}"; //root


		strRet = strJson;
		return true;
	}


	//参数检查,
	//返回值: 
	//   成功: true  失败: false
	//   strErrMsg 携带错误信息
	bool ParamsCheck(std::string &strErrMsg)
	{

		if (false == this->csRawTx.ParamsCheck(strErrMsg))
		{
			strErrMsg += "CsBroadcastTx::ParamsCheck:";
			return false;
		}

		if ( STR_BROADCAST_MSG_TYPE != this->strMsgType)
		{
			strErrMsg = boost::str(boost::format("invalid `msg type` : '%s', must be '%s'.")
				                      % this->strMsgType % STR_BROADCAST_MSG_TYPE);
			return false;
		}

		if ( STR_BROADCAST_PUB_KEY_TYPE != this->strPubKeyType )
		{
			strErrMsg = boost::str(boost::format("invalid `pub_key type` : '%s', must be '%s'.") 
				                    % this->strPubKeyType% STR_BROADCAST_PUB_KEY_TYPE);
			return false;
		}

		if (strPubkeyValue.empty())
		{
			
			strErrMsg = boost::str(boost::format("invalid `pub_key value` is empty, must be base64(pubkey).") 
									% this->strPubKeyType % STR_BROADCAST_PUB_KEY_TYPE);
			return false;
		}

		string strTmpDecode;
		strTmpDecode = Base64ToBytes(strPubkeyValue);
		if (UINT_PUB_KEY_LEN != strTmpDecode.size())
		{
			strErrMsg = boost::str(boost::format("invalid `pub_key value` length is not %d. After base64 decode, pubkey's length must be %d.") 
									% UINT_PUB_KEY_LEN % UINT_PUB_KEY_LEN);
			return false;
		}


		strTmpDecode.clear();
		strTmpDecode =  Base64ToBytes(this->strSignature);
		if (UINT_SIG_RS_LEN != strTmpDecode.size())
		{
			strErrMsg = boost::str(boost::format("invalid `signature` length is not %d. After base64 decode, signature's length must be %d.")
				% UINT_SIG_RS_LEN % UINT_SIG_RS_LEN);
			return false;
		}

		return true;
	}


	//转为十六进制字符串,用于调用服务端的广播接口
	//返回值:
	//    成功:  true
	//    失败: 参数检查失败, strOut携带错误信息
	bool ToHexStr(std::string &strOut)
	{
		std::string strErrMsg;
		if (false == this->ParamsCheck(strErrMsg))
		{
			strOut = strErrMsg;
			return false;
		}

		std::string strRet;
		std::string strHex;
		if (false == this->ToString(strErrMsg)) //测试是否成功
		{
			strOut = strErrMsg;
			return false;
		}

		this->ToString(strHex);

		strRet = "";
		for (size_t i  = 0; i < strHex.size(); i++)
		{
			strRet += boost::str(boost::format("%02x") % ((int)strHex[i]));
		}
		strOut = strRet;

		return true;
	}


};


//************************************
// 说明: 对交易信息进行签名   输出  r,s 共 64字节
// Method:    ECDSA_SignRawTxWithPrivKey
// FullName:  cosmos::ECDSA_SignRawTxWithPrivKey
// Access:    public 
// Returns:   int   错误码:  成功:0    失败:-1
// Qualifier:  
// Parameter: unsigned char * pszIn     数据输入
// Parameter: unsigned int uInLen      输入数据的长度
// Parameter: unsigned char *pszPrivKey 私钥
// Parameter: unsigned int uPrivKeyLen   私钥长度   
// Parameter: unsigned char * pszOut   输出数据
// Parameter: unsigned int uOutBufLen   输出buf的长度
// Parameter: unsigned int * puOutDataLen  输出数据的实际长度
// Parameter: char * pszErrMsg          错误信息
//************************************

int ECDSA_Sign(
	unsigned char *pszIn, 
	unsigned int uInLen, 
	unsigned char *pszPrivKey,
	unsigned int  uPrivKeyLen,
	unsigned char *pszOut,
	unsigned int uOutBufLen, 
	unsigned int *puOutDataLen, 
	char *pszErrMsg);


//SHA256(pJsonBuf, uBufSize, pSha256Out);

//int OpenSSL_SHA256()





}
#endif // _CCOSMOS_H_
