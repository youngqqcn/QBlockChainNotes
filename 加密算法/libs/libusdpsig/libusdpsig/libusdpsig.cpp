// libusdpsig.cpp : 此文件包含 "main" 函数。程序执行将在此处开始并结束。
//

#include <iostream>
#include <stdio.h>
#include <iostream>
#include <stdlib.h>
#include <stdio.h>
#include <string>
#include <sstream>
#include <boost/property_tree/ptree.hpp>
#include <boost/property_tree/json_parser.hpp>
#include <time.h>


#include "cryptopp/keccak.h" //keccak
#include "cryptopp/sha3.h" //sha3_256
#include "openssl/sha.h"  //openssl sha256



#include "cryptopp/base64.h"  //base64 



#include "CCosmos.h" //cosmos



using namespace std;
using namespace boost::property_tree;



#include <type_traits>
#include <boost/multiprecision/cpp_int.hpp>
#include "secp256k1/secp256k1.h"
#include "secp256k1/secp256k1_recovery.h"
#include <boost/algorithm/string.hpp>
using u256 = boost::multiprecision::number<boost::multiprecision::cpp_int_backend<256, 256, boost::multiprecision::unsigned_magnitude, boost::multiprecision::unchecked, void>>;
//static const u256 c_secp256k1n("115792089237316195423570985008687907852837564279074904382605163141518161494337");

inline secp256k1_context const* getCtx()
{
	static std::unique_ptr<secp256k1_context, decltype(&secp256k1_context_destroy)> s_ctx{
		secp256k1_context_create(SECP256K1_CONTEXT_SIGN | SECP256K1_CONTEXT_VERIFY),
		&secp256k1_context_destroy
	};
	return s_ctx.get();
}


inline  std::string Bin2HexStr(const unsigned char *pBin, unsigned int len)
{
	std::string  strHex;
	for (unsigned int i = 0; i < len; i++)
	{
		char buf[10] = { 0 };
		memset(buf, 0, sizeof(buf));
		sprintf_s(buf, "%02x", pBin[i]);
		strHex += buf;

	}
	return strHex;
}

inline  std::vector<unsigned char>  Bin2ByteArray(const unsigned char *pBin, unsigned int len)
{
	std::vector<unsigned char>  vctBytes;
	
	for (unsigned int i = 0; i < len; i++)
	{
		vctBytes.push_back(pBin[i]);
	}
	return vctBytes;
}

inline  std::vector<unsigned char>  Bin2ByteArray(const std::string &strTmp, unsigned int len)
{
	std::vector<unsigned char>  vctBytes;

	for (unsigned int i = 0; i < strTmp.size(); i++)
	{
		vctBytes.push_back(strTmp[i]);
	}
	return vctBytes;

}

inline void PrintBytesArray(std::vector<unsigned char> &vctBytes)
{
	for (size_t i = 0; i < vctBytes.size(); i++)
	{
		//std::cout << vctBytes[i] << ",";
		printf("%d,", vctBytes[i]);
	}
	std::cout << endl;

}




inline string HexToBin(const string &strHexIn)
{
	if (strHexIn.size() % 2 != 0) return "";

	string strHex = (0 == strHexIn.find_first_of("0x")) ? (strHexIn.substr(2)) :(strHexIn);


	string strBin;
	strBin.resize(strHex.size() / 2);
	for (size_t i = 0; i < strBin.size(); i++)
	{
		uint8_t cTemp = 0;
		for (size_t j = 0; j < 2; j++)
		{
			char cCur = strHex[2 * i + j];
			if (cCur >= '0' && cCur <= '9')
			{
				cTemp = (cTemp << 4) + (cCur - '0');
			}
			else if (cCur >= 'a' && cCur <= 'f')
			{
				cTemp = (cTemp << 4) + (cCur - 'a' + 10);
			}
			else if (cCur >= 'A' && cCur <= 'F')
			{
				cTemp = (cTemp << 4) + (cCur - 'A' + 10);
			}
			else
			{
				return "";
			}
		}
		strBin[i] = cTemp;
	}

	return strBin;
}














//简单json字符获取值
void Test_StrToJsonObj()
{
	//std::string strTmpJson = "{\"name\":\"yqq\", \"age\":99, \"isTest\":True}"; //抛异常 : error:<unspecified file>(1): expected value
	std::string strTmpJson = "{\"name\":\"yqq\", \"age\":99, \"isTest\":true}";
	std::stringstream ss(strTmpJson);
	boost::property_tree::ptree root;
	try
	{
		boost::property_tree::read_json(ss, root);
	}
	catch (const std::exception& e)
	{
		std::cout << "read_json  error:" << e.what() << std::endl;
	}


	for (auto it = root.begin(); it != root.end(); it++)
	{
		std::string ssTmp;
		std::cout << it->first << ":" << root.get<std::string>(it->first) << std::endl;
	}
}



void Test_StrToJsonObj2()
{
}



void TestSha256()
{
	//1.将json转为bytes形式 
	printf("--------------开始sha256算法测试---------------------");
	std::string strJson = "";
	printf("json 的 bytes 形式: ");
	for (size_t i = 0; i < strJson.size(); i++)
	{
		printf("%d,", strJson[i]);
	}
	
	std::cout << std::endl;
	std::cout << std::endl;
	std::cout << std::endl;



	unsigned char  *pJsonBuf = new unsigned char[strJson.size()];
	size_t uBufSize = strJson.size();
	memset(pJsonBuf, 0, uBufSize);
	memcpy(pJsonBuf, strJson.c_str(), uBufSize);

	printf("复制后的 的 bytes 形式: ");
	for (size_t i = 0; i < uBufSize; i++)
	{
		printf("%d,", pJsonBuf[i]);
	}
	std::cout << std::endl;
	std::cout << std::endl;
	std::cout << std::endl;




	//2.进行sha256哈希
	const size_t uSha256Size = 32;  //256 = 32 * 8
	unsigned  char *pSha256Out = new unsigned  char[uSha256Size]; //32 byte 即可
	memset(pSha256Out, 0, uSha256Size);

	//#define USE_KECCAK
	//#define USE_SHA3_256
#define  USE_OPENSSL_SHA256
#ifdef USE_KECCAK
	CryptoPP::Keccak_256 ctx;
	ctx.Update(pJsonBuf, uBufSize);
	ctx.Final(pSha256Out);
#endif
#ifdef USE_SHA3_256
	CryptoPP::SHA3_256 ctx;;
	ctx.Update(pJsonBuf, uBufSize);
	ctx.Final(pSha256Out);
#endif
#ifdef USE_OPENSSL_SHA256
	SHA256(pJsonBuf, uBufSize, pSha256Out);
#endif

	printf("sha256("")结果是: ");
	for (size_t i = 0; i < uSha256Size; i++)
	{
		printf("%d,", pSha256Out[i]);
	}
	std::cout << std::endl;
	std::cout << std::endl;
	std::cout << std::endl;

	//cosmos使用的sha256 对空字符串进行sha256 输出是 
	//[227 176 196 66 152 252 28 20 154 251 244 200 153 111 185 36 39 174 65 228 100 155 147 76 164 149 153 27 120 82 184 85]
	unsigned char uszRight[32] = { 227, 176, 196 ,66 ,152, 252, 28 ,20 ,154, 251, 244, 200, 153, 111, 185, 36, 39, 174, 65, 228, 100, 155, 147, 76, 164, 149, 153, 27, 120, 82, 184, 85 };
	if (0 == memcmp(uszRight, pSha256Out, 32))
	{
		printf("\n\n  sha256 测试成功!!\n");
	}
	else
	{
		printf("\n\n sha256 测试失败!!\n");
	}

	delete[]pSha256Out; pSha256Out = NULL;
	delete[]pJsonBuf; pJsonBuf = NULL;

	std::cout << "-----------------------结束sha256------------------------" << std::endl;
}


#include <openssl/evp.h>
#include <openssl/bio.h>
#include <openssl/buffer.h>

inline std::string Base64Encode(const char *input, int length, bool with_new_line)
{
	BIO * bmem = NULL;
	BIO * b64 = NULL;
	BUF_MEM * bptr = NULL;

	b64 = BIO_new(BIO_f_base64());
	if (!with_new_line) {
		BIO_set_flags(b64, BIO_FLAGS_BASE64_NO_NL);
	}
	bmem = BIO_new(BIO_s_mem());
	b64 = BIO_push(b64, bmem);
	BIO_write(b64, input, length);
	BIO_flush(b64);
	BIO_get_mem_ptr(b64, &bptr);

	char * buff = (char *)malloc(bptr->length + 1);
	memcpy(buff, bptr->data, bptr->length);
	buff[bptr->length] = 0;
	BIO_free_all(b64);


	std::string  strRet(buff);
	free(buff); buff = NULL;
	return strRet;
}

inline std::string Base64Decode(char * input, int length, bool with_new_line)
{
	BIO * b64 = NULL;
	BIO * bmem = NULL;
	char * buffer = (char *)malloc(length);
	memset(buffer, 0, length);

	b64 = BIO_new(BIO_f_base64());
	if (!with_new_line) {
		BIO_set_flags(b64, BIO_FLAGS_BASE64_NO_NL);
	}
	bmem = BIO_new_mem_buf(input, length);
	bmem = BIO_push(b64, bmem);
	BIO_read(bmem, buffer, length);

	BIO_free_all(bmem);

	std::string strRet;
	strRet.append(buffer, length);

	free(buffer); buffer = NULL;
	return strRet;
}




void SigTest()
{

	//1.将json转为bytes形式 
	std::string strJson = "{\"account_number\":\"11\",\"chain_id\":\"testchain\",\"fee\":{\"amount\":[{\"amount\":\"20\",\"denom\":\"htdf\"}],\"gas\":\"200000\"},\"memo\":\"\",\"msgs\":[{\"Amount\":[{\"amount\":\"12\",\"denom\":\"htdf\"}],\"From\":\"usdp15havmvnt4ygfyfuqm32aecth7p8800f6pkf652\",\"To\":\"usdp15havmvnt4ygfyfuqm32aecth7p8800f6pkf652\"}],\"sequence\":\"0\"}";
	printf("----------------json 的 bytes 形式-------------------\n");
	PrintBytesArray(Bin2ByteArray(strJson, strJson.size()));
	std::cout << "----------------------------------" << std::endl << std::endl;



	unsigned char  *pJsonBuf = new unsigned char[strJson.size()];
	size_t uBufSize = strJson.size();
	memset(pJsonBuf, 0, uBufSize);
	memcpy(pJsonBuf, strJson.c_str(), uBufSize);


	for (size_t i = 0; i < uBufSize; i++)
	{
		printf("%d,", pJsonBuf[i]);
	}
	printf("\n\n");




	//2.进行sha256哈希
	const size_t uSha256Size = 32;  //256 = 32 * 8
	unsigned  char *pSha256Out = new unsigned  char[uSha256Size]; //32 byte 即可
	memset(pSha256Out, 0, uSha256Size);

//#define USE_KECCAK
//#define USE_SHA3_256
#define  USE_OPENSSL_SHA256
#ifdef USE_KECCAK
	CryptoPP::Keccak_256 ctx;
	ctx.Update(pJsonBuf, uBufSize);
	ctx.Final(pSha256Out);
#endif
#ifdef USE_SHA3_256
	CryptoPP::SHA3_256 ctx;;
	ctx.Update(pJsonBuf, uBufSize);
	ctx.Final(pSha256Out);
#endif
#ifdef USE_OPENSSL_SHA256
	SHA256(pJsonBuf, uBufSize, pSha256Out);
#endif

	for (size_t i = 0; i < uSha256Size; i++)
	{
		printf("%d,", pSha256Out[i]);
	}
	printf("\n\n");

	unsigned char uszSha256Right[] = { 184, 225, 149, 250, 132, 123, 49, 17, 200, 7, 198, 68, 35, 238, 167, 36, 108, 145, 87, 250, 47, 109, 153, 88, 237, 192, 192, 11, 129, 30, 195, 133};
	if (0 == memcmp(uszSha256Right, pSha256Out, 256/8))
	{
		std::cout << "-----------> sha256结果对比成功 , sha256算法测试成功!!" << std::endl;
	}
	else
	{
		std::cout << "-----------> sha256结果对比失败, sha256算法测试失败!!" << std::endl;
		return;
	}






	//3.进行签名
	//6cf864e7da189eb0f6db4c382336d3c83fc88c45dd65fa056062be26641a3728
	unsigned char uszPrivKey[] = { 108,248,100,231,218,24,158,176,246,219,76,56,35,54,211,200,63,200,140,69,221,101,250,5,96,98,190,38,100,26,55,40};
	std::string strPrivKey = Bin2HexStr(uszPrivKey, sizeof(uszPrivKey));

	auto* ctx = getCtx();

	secp256k1_ecdsa_recoverable_signature rawSig;
	memset(&rawSig.data, 0, 65);
	if (!secp256k1_ecdsa_sign_recoverable(ctx, &rawSig, pSha256Out, uszPrivKey, nullptr, nullptr))
	{
		std::cout << "secp256k1_ecdsa_sign_recoverable 失败" << std::endl;
		return;
	}

	int iRecid = 0;
	unsigned char uszSigData[520 / 8] = { 0 }; memset(uszSigData, 0, sizeof(uszSigData));
	secp256k1_ecdsa_recoverable_signature_serialize_compact(ctx, uszSigData, &iRecid, &rawSig);


	string strR = Bin2HexStr(uszSigData, 32);
	string strS = Bin2HexStr(uszSigData +  32,  32);

	std::cout << "r:" << Bin2HexStr(uszSigData, 32) << std::endl;
	std::cout << "s:" << Bin2HexStr(uszSigData + 32, 32) << std::endl;

	if (strR == "03bbd7a6053720552b9b8e6caec3cd168a5f779db411504e46e2afc824b83995" 
		&& strS == "2f0441e14c77a8c01d2dbce33d0139e4e66bc81d23fe24696522e773f8f85750")
	{
		std::cout << "------------> r, s  对比成功,  签名成功!!!" << std::endl;
	}
	else
	{
		std::cout << "------------>  r, s  对比失败,  签名签名!!!" << std::endl;
		return;
	}



	//只要r,s  不要 v
	unsigned char uszRS[64] = { 0 }; memset(uszRS, 0, sizeof(uszRS));
	memcpy(uszRS, uszSigData, 64);

#if 0
	//对r,s 进行 base64编码
	CryptoPP::Base64Encoder encoder(NULL, false /*不要插入换行符*/, 0xffffffff);   //不要断行
	encoder.Put(uszRS, sizeof(uszRS));
	encoder.MessageEnd();

	CryptoPP::lword uBase64Size = encoder.MaxRetrievable();
	unsigned char *pBase64Out = new unsigned char[(size_t)uBase64Size + 1];
	memset(pBase64Out, 0, (size_t)(uBase64Size + 1));

	encoder.Get(pBase64Out, (size_t)uBase64Size);

	ostringstream  oss;
	oss << pBase64Out;

	std::string strRSBase64 = oss.str();
#else
	std::string strRSBase64 = Base64Encode((const char *)uszRS, sizeof(uszRS), false);
	std::string strRSDecode = Base64Decode((char *)strRSBase64.data(), strRSBase64.size(), false);
	if (0 == memcmp(uszRS, strRSDecode.data(), sizeof(uszRS)))
	{
		std::cout << "openssl base64 编解码测试成功!" << std::endl;
	}
	else
	{
		std::cout << "openssl baset64 编解码测试失败" << std::endl;
	}
	//std::string strRSBase64 = cosmos::BytesToBase64(uszRS, sizeof(uszRS));
	//strRSBase64.replace("\n", "");
	//strRSBase64 = boost::algorithm::replace_all_copy(strRSBase64, "\n", "");

#endif

	std::cout << "rs的base64编码:" << std::endl << strRSBase64 << std::endl;

	std::string strRSBase64Right = "A7vXpgU3IFUrm45srsPNFopfd520EVBORuKvyCS4OZUvBEHhTHeowB0tvOM9ATnk5mvIHSP+JGllIudz+PhXUA==";

	if (strRSBase64Right == strRSBase64)
	{
		std::cout << "------------> rs的base编码 测试成功!!" << std::endl;
	}
	else
	{
		std::cout << "------------> rs的base编码 测试失败 !!" << std::endl;
		return;
	}




	delete[]pSha256Out; pSha256Out = NULL;
	delete[]pJsonBuf; pJsonBuf = NULL;
	//delete[]pBase64Out; pBase64Out = NULL;


	std::cout << std::endl << std::endl << "---------------恭喜! 所有测试都成功!---------------------------" << std::endl << std::endl;
}




void CosmosTest_RawTx()
{
	cosmos::CsRawTx  csRawTx;
	csRawTx.uAccountNumber =  12;
	strcpy_s(csRawTx.szChainId, STR_MAINCHAIN);
	strcpy_s(csRawTx.szFeeDenom, STR_USDP);
	strcpy_s(csRawTx.szMemo, "");
	strcpy_s(csRawTx.szMsgDenom, STR_USDP);
	strcpy_s(csRawTx.szMsgFrom, "usdp15havmvnt4ygfyfuqm32aecth7p8800f6pkf652");
	strcpy_s(csRawTx.szMsgTo, "usdp1vmsfd7rly9chhjpaalr55q5886lnva99ghlesg");
	csRawTx.uMsgAmount = 66;
	csRawTx.uGas = 200000;
	csRawTx.uFeeAmount = 20;
	csRawTx.uSequence = 5;


	std::string strJson;
	if(false == csRawTx.ToString(strJson))
	{
		std::cout << "错误信息:" << strJson << std::endl;
		return;
	}

	std::string strJsonRight = "{\"account_number\":\"12\",\"chain_id\":\"mainchain\",\"fee\":{\"amount\":[{\"amount\":\"20\",\"denom\":\"usdp\"}],\"gas\":\"200000\"},\"memo\":\"\",\"msgs\":[{\"Amount\":[{\"amount\":\"66\",\"denom\":\"usdp\"}],\"From\":\"usdp15havmvnt4ygfyfuqm32aecth7p8800f6pkf652\",\"To\":\"usdp1vmsfd7rly9chhjpaalr55q5886lnva99ghlesg\"}],\"sequence\":\"5\"}";

	std::cout << "rawtx string: " << strJson << std::endl;
	std::cout << std::endl;
	if (strJsonRight == strJson)
	{
		std::cout << "json 对比成功,  测试 CsRawTx 成功!" << std::endl;
	}
	else
	{
		std::cout << "json 对比失败,  测试 CsRawTx 失败!" << std::endl;
	}


}


void CosmosTest_BroadcastTx()
{

	cosmos::CsRawTx  csRawTx;
	csRawTx.uAccountNumber = 12;
	strcpy_s(csRawTx.szChainId, STR_MAINCHAIN);
	strcpy_s(csRawTx.szFeeDenom, STR_USDP);
	strcpy_s(csRawTx.szMemo, "");
	strcpy_s(csRawTx.szMsgDenom, STR_USDP);
	strcpy_s(csRawTx.szMsgFrom, "usdp15havmvnt4ygfyfuqm32aecth7p8800f6pkf652");
	strcpy_s(csRawTx.szMsgTo, "usdp1vmsfd7rly9chhjpaalr55q5886lnva99ghlesg");
	csRawTx.uMsgAmount = 66;
	csRawTx.uGas = 200000;
	csRawTx.uFeeAmount = 20;
	csRawTx.uSequence = 5;


	cosmos::CsBroadcastTx  csBTx;
	csBTx.csRawTx = csRawTx;
	csBTx.strType = STR_BROADCAST_TYPE;
	csBTx.strMsgType = STR_BROADCAST_MSG_TYPE;
	csBTx.strPubKeyType = STR_BROADCAST_PUB_KEY_TYPE;
	csBTx.strPubkeyValue = "A9wn8etkGR2CeeEzkHqGq17gxFtWajDa/aqmPCUVt9cN";
	csBTx.strSignature = "HnBXVHouML/jR45/Ln5GOu6JQdPekB8J/x7H5h6VX357g6iqkuFawFwKItTugVg2Y2QUMD/DYDjJHm1znao9Kw==";


	std::string strTmp;
	if (false == csBTx.ToString(strTmp))
	{
		std::cout << "错误信息:" << strTmp << std::endl;
		return;
	}

	std::cout << "json str:" << strTmp << std::endl;
	std::cout << std::endl;
	std::cout << std::endl;
	std::cout << std::endl;


	std::string strHex;
	if (false == csBTx.ToHexStr(strHex))
	{
		std::cout << "错误信息:" << strHex << std::endl;
		return;
	}

	std::cout << "broadcasttx hex str: " << strHex << std::endl;

	std::string  strHexRight = "7b2274797065223a22617574682f5374645478222c2276616c7565223a7b226d7367223a5b7b2274797065223a2268746466736572766963652f73656e64222c2276616c7565223a7b2246726f6d223a227573647031356861766d766e7434796766796675716d333261656374683770383830306636706b66363532222c22546f223a227573647031766d73666437726c79396368686a7061616c72353571353838366c6e7661393967686c657367222c22416d6f756e74223a5b7b2264656e6f6d223a2275736470222c22616d6f756e74223a223636227d5d7d7d5d2c22666565223a7b22616d6f756e74223a5b7b2264656e6f6d223a2275736470222c22616d6f756e74223a223230227d5d2c22676173223a22323030303030227d2c227369676e617475726573223a5b7b227075625f6b6579223a7b2274797065223a2274656e6465726d696e742f5075624b6579536563703235366b31222c2276616c7565223a224139776e3865746b475232436565457a6b4871477131376778467457616a44612f61716d504355567439634e227d2c227369676e6174757265223a22486e425856486f754d4c2f6a5234352f4c6e35474f75364a516450656b42384a2f7837483568365658333537673669716b7546617746774b4974547567566732593251554d442f4459446a4a486d317a6e616f394b773d3d227d5d2c226d656d6f223a22227d7d";
	//if (true == boost::algorithm::equals(strHex, strHexRight))
	if (strHexRight == strHex)
	{
		std::cout << "对比成功!  CsBroadcastTx 测试成功  " << std::endl;
	}
	else
	{
		std::cout << "对比失败!  CsBroadcastTx 测试失败" << std::endl;
	}
}


//真实交易数据测试
void MakeRealSig()
{
	cosmos::CsRawTx  csRawTx;
	csRawTx.uAccountNumber = 12;
	strcpy_s(csRawTx.szChainId, STR_MAINCHAIN);
	strcpy_s(csRawTx.szFeeDenom, STR_USDP);
	strcpy_s(csRawTx.szMemo, "");
	strcpy_s(csRawTx.szMsgDenom, STR_USDP);
	strcpy_s(csRawTx.szMsgFrom, "usdp15havmvnt4ygfyfuqm32aecth7p8800f6pkf652");
	strcpy_s(csRawTx.szMsgTo, "usdp1vmsfd7rly9chhjpaalr55q5886lnva99ghlesg");
	csRawTx.uMsgAmount = 66;
	csRawTx.uGas = 200000;
	csRawTx.uFeeAmount = 20;
	csRawTx.uSequence = 5;


	cosmos::CsBroadcastTx  csBTx;
	csBTx.csRawTx = csRawTx;
	csBTx.strType = STR_BROADCAST_TYPE;
	csBTx.strMsgType = STR_BROADCAST_MSG_TYPE;
	csBTx.strPubKeyType = STR_BROADCAST_PUB_KEY_TYPE;
	csBTx.strPubkeyValue = "A9wn8etkGR2CeeEzkHqGq17gxFtWajDa/aqmPCUVt9cN";



	std::string strOut;
	if (false == csRawTx.ToString(strOut))
	{
		std::cout << "错误:" << strOut << std::endl;
		return;
	}
	std::cout << "json:  " << std::endl << strOut << std::endl;
	std::string strJsonRight = "{\"account_number\":\"12\",\"chain_id\":\"mainchain\",\"fee\":{\"amount\":[{\"amount\":\"20\",\"denom\":\"usdp\"}],\"gas\":\"200000\"},\"memo\":\"\",\"msgs\":[{\"Amount\":[{\"amount\":\"66\",\"denom\":\"usdp\"}],\"From\":\"usdp15havmvnt4ygfyfuqm32aecth7p8800f6pkf652\",\"To\":\"usdp1vmsfd7rly9chhjpaalr55q5886lnva99ghlesg\"}],\"sequence\":\"5\"}";
	if (strJsonRight == strOut)
	{
		std::cout << "json 对比成功 !" << std::endl;
	}
	else
	{
		std::cout << "json 对比失败 !" << std::endl;
	}


	unsigned char uszShaData[256/8] = { 0 };
	memset(uszShaData, 0, sizeof(uszShaData));
	SHA256((unsigned char *)strOut.data(), strOut.size(), uszShaData );

	std::string strSha256 = Bin2HexStr(uszShaData, sizeof(uszShaData));
	std::cout << "sha256 output: " << std::endl << strSha256 << std::endl << std::endl << std::endl;

	if (strSha256 == "5645a602d7d980a41d0f4cc62afb45b37160c97ac484bf16d4a071d1357764e4")
	{
		std::cout << "SHA256 结果对比成功!" << std::endl << std::endl;
	}
	else
	{
		std::cout << "SHA256 结果对比失败!!" << std::endl << std::endl;
	}


	std::string strPrivKey = HexToBin(std::string("6cf864e7da189eb0f6db4c382336d3c83fc88c45dd65fa056062be26641a3728"));
	

	unsigned char uszSigOut[64] = { 0 }; memset(uszSigOut, 0, sizeof(uszSigOut));
	unsigned int uSigOutLen = 0;
	char szMsgBuf[1024] = { 0 }; memset(szMsgBuf, 0, sizeof(szMsgBuf));
	int iRet = cosmos::ECDSA_Sign(uszShaData, sizeof(uszShaData) , (unsigned char *)strPrivKey.data(), strPrivKey.size(), uszSigOut, sizeof(uszSigOut), &uSigOutLen, szMsgBuf );
	if (cosmos::NO_ERROR != iRet)
	{
		std::cout << "签名错误:" << szMsgBuf << std::endl << std::endl;
		return;
	}
	std::string strTmpSig = Bin2HexStr(uszSigOut, uSigOutLen);

	std::cout << "签名结果:" << std::endl << strTmpSig << std::endl << std::endl;

	if (strTmpSig == "1e7057547a2e30bfe3478e7f2e7e463aee8941d3de901f09ff1ec7e61e955f7e7b83a8aa92e15ac05c0a22d4ee815836636414303fc36038c91e6d739daa3d2b")
	{
		std::cout << "对比签名结果成功!" << std::endl;

		std::cout << "测试签名 成功!!" << std::endl;
	}
	else
	{
		std::cout << "对比签名结果失败!" << std::endl << std::endl;
	}
	//csBTx.strSignature = "HnBXVHouML/jR45/Ln5GOu6JQdPekB8J/x7H5h6VX357g6iqkuFawFwKItTugVg2Y2QUMD/DYDjJHm1znao9Kw==";

}




//输入: 十六进制字符串形式的私钥
//输出: 十六进制字符串形式的公钥
int PrivKeyToCompressPubKey(const std::string &_strPrivKey, std::string &strPubKey)
{
	std::string strPrivKey = HexToBin(_strPrivKey);

	secp256k1_pubkey  pubkey;
	memset(pubkey.data, 0, sizeof(pubkey.data));

	auto* ctx = getCtx();

	if (!secp256k1_ec_pubkey_create(ctx, &pubkey, (unsigned char *)strPrivKey.data()))
	{
		return 1;
	}

	unsigned char output[1024] = { 0 }; memset(output, 0, sizeof(output));
	size_t  outputlen = 33;
	secp256k1_ec_pubkey_serialize(ctx, output, &outputlen, &pubkey, SECP256K1_EC_COMPRESSED);

	if (33 != outputlen)
	{
		return 1;
	}

	strPubKey = Bin2HexStr(output, outputlen);
	return 0;
}





void PrivKeyToPubKeyCompress_TEST()
{

	
	/** Compute the public key for a secret key.
 *
 *  Returns: 1: secret was valid, public key stores
 *           0: secret was invalid, try again
 *  Args:   ctx:        pointer to a context object, initialized for signing (cannot be NULL)
 *  Out:    pubkey:     pointer to the created public key (cannot be NULL)
 *  In:     seckey:     pointer to a 32-byte private key (cannot be NULL)
 */
	//SECP256K1_API SECP256K1_WARN_UNUSED_RESULT int secp256k1_ec_pubkey_create(
	//	const secp256k1_context* ctx,
	//	secp256k1_pubkey *pubkey,
	//	const unsigned char *seckey
	//) SECP256K1_ARG_NONNULL(1) SECP256K1_ARG_NONNULL(2) SECP256K1_ARG_NONNULL(3);

	
	std::string strPrivKey = HexToBin(std::string("6cf864e7da189eb0f6db4c382336d3c83fc88c45dd65fa056062be26641a3728"));


	secp256k1_pubkey  pubkey;
	memset(pubkey.data, 0, sizeof(pubkey.data));


	auto* ctx = getCtx();

	if (!secp256k1_ec_pubkey_create(ctx, &pubkey, (unsigned char *)strPrivKey.data()))
	{
		std::cout << "invalid privkey" << std::endl;
		return;
	}
	std::cout << "pub created successed." << std::endl;
	std::cout << Bin2HexStr(pubkey.data, sizeof(pubkey.data)) << std::endl;
	

	std::cout << "starting pubkey compressing......." << std::endl;
	
	
	
	
/** Serialize a pubkey object into a serialized byte sequence.
 *
 *  Returns: 1 always.
 *  Args: ctx:        a secp256k1 context object.
 *  Out:  output:     a pointer to a 65-byte (if compressed==0) or 33-byte (if
 *                    compressed==1) byte array to place the serialized key in.
 *        outputlen:  a pointer to an integer which will contain the serialized
 *                    size.
 *  In:   pubkey:     a pointer to a secp256k1_pubkey containing an initialized
 *                    public key.
 *        flags:      SECP256K1_EC_COMPRESSED if serialization should be in
 *                    compressed format.
 */
	//SECP256K1_API int secp256k1_ec_pubkey_serialize(
	//	const secp256k1_context* ctx,
	//	unsigned char *output,
	//	size_t *outputlen,
	//	const secp256k1_pubkey* pubkey,
	//	unsigned int flags
	//) SECP256K1_ARG_NONNULL(1) SECP256K1_ARG_NONNULL(2) SECP256K1_ARG_NONNULL(3) SECP256K1_ARG_NONNULL(4);


	unsigned char output[1024] = { 0 }; memset(output, 0, sizeof(output));
	size_t  outputlen = 33;
	secp256k1_ec_pubkey_serialize(ctx, output, &outputlen, &pubkey, SECP256K1_EC_COMPRESSED);

	if (33 == outputlen)
	{
		std::cout << "pubkey compressed successed." << std::endl;
		std::cout << Bin2HexStr(output, outputlen) << std::endl;
	}
	else
	{
		std::cout << "pubkey compressed failed." << std::endl;
	}


}




int main()
{
	//TestSha256();
	//Test_StrToJsonObj();
	SigTest();
	//MakeRealSig();
	//CosmosTest_RawTx();
	//CosmosTest_BroadcastTx();
	//MakeRealSig();
	//PrivKeyToPubKeyCompress_TEST();


	std::cout << std::endl;
	std::cout << std::endl;
	std::cout << std::endl;
	std::cout << std::endl;
	std::cout << std::endl;

    //std::cout << "Hello World!\n"; 
}

// 运行程序: Ctrl + F5 或调试 >“开始执行(不调试)”菜单
// 调试程序: F5 或调试 >“开始调试”菜单

// 入门提示: 
//   1. 使用解决方案资源管理器窗口添加/管理文件
//   2. 使用团队资源管理器窗口连接到源代码管理
//   3. 使用输出窗口查看生成输出和其他消息
//   4. 使用错误列表窗口查看错误
//   5. 转到“项目”>“添加新项”以创建新的代码文件，或转到“项目”>“添加现有项”以将现有代码文件添加到项目
//   6. 将来，若要再次打开此项目，请转到“文件”>“打开”>“项目”并选择 .sln 文件
