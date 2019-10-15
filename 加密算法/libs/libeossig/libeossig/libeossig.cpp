// libusdpsig.cpp : 此文件包含 "main" 函数。程序执行将在此处开始并结束。
//

#include "pch.h"

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
#include "base58.hpp"
#include "cryptopp/keccak.h" //keccak
#include "cryptopp/sha3.h" //sha3_256
#include "openssl/sha.h"  //openssl sha256
#include "cryptopp/base64.h"  //base64 
#include <type_traits>
#include <boost/multiprecision/cpp_int.hpp>
#include "secp256k1/secp256k1.h"
#include "secp256k1/secp256k1_recovery.h"
#include <boost/algorithm/string.hpp>

using namespace std;
using namespace boost::property_tree;

//using u256 = boost::multiprecision::number<boost::multiprecision::cpp_int_backend<256, 256, boost::multiprecision::unsigned_magnitude, boost::multiprecision::unchecked, void>>;
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
	for (int i = 0; i < len; i++)
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

	string strHex;
	if (0 == strHexIn.find_first_of("0x"))
		strHex = strHexIn.substr(2);
	else
		strHex = strHexIn;


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




bool IsCanonical_DER(const std::string &strData)
{
	assert(strData.size() >= 65);
	bool b1 = !(strData[1] & 0x80);
	bool b2 = !(strData[1] == 0 && !(strData[2] & 0x80));
	bool b3 = !(strData[33] & 0x80);
	bool b4 =  !(strData[33] == 0 && !(strData[34] & 0x80));

	return b1 && b2 && b3 && b4;
}



bool IsCanonical_RS(const std::string &strData)
{
	assert(strData.size() >= 64);
	bool b1 = (strData[0] & 0x80) == 0;
	bool b2 = (strData[32] & 0x80) == 0;

	return b1 && b2;
}





#include "openssl/evp.h"
int get_digest(const EVP_MD *type, const char *s_buf, int s_len, unsigned char *d_buf, unsigned int *d_len, char *msg) {
	int i, ret = 0;
	EVP_MD_CTX ctx;
	EVP_MD_CTX_init(&ctx);
	EVP_DigestInit_ex(&ctx, type, NULL);
	EVP_DigestUpdate(&ctx, s_buf, s_len);
	EVP_DigestFinal_ex(&ctx, d_buf, d_len);
	EVP_MD_CTX_cleanup(&ctx);
	fprintf(stderr, "%s message:[%s]\ndigestlen:[%d]digest:[", msg, s_buf, *d_len);
	for (i = 0; i < *d_len; i++) {
		fprintf(stderr, "%02X", *(d_buf + i));
	}
	fprintf(stderr, "]\n");
	return ret;
}




void EOSSigTest()
{

#if 0
	//1.将json转为bytes形式 
	//std::string strJson = "{\"account_number\":\"11\",\"chain_id\":\"testchain\",\"fee\":{\"amount\":[{\"amount\":\"20\",\"denom\":\"htdf\"}],\"gas\":\"200000\"},\"memo\":\"\",\"msgs\":[{\"Amount\":[{\"amount\":\"12\",\"denom\":\"htdf\"}],\"From\":\"usdp15havmvnt4ygfyfuqm32aecth7p8800f6pkf652\",\"To\":\"usdp15havmvnt4ygfyfuqm32aecth7p8800f6pkf652\"}],\"sequence\":\"0\"}";
	std::string strJson = "817b4e2f1a5feac19ff628df4d38b48d93c6f3cb1b4fafc17de63825fe823490";
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
#endif


	std::string strHexDigest = "0x0251bfdfb21cc79f0b86b23ff47442ad9a1bc4336da83b71c194a524b984e9bf";
	std::string strBinHexDigest = HexToBin(strHexDigest);

	




	for (int n = 0; ; n++)
	{


		//2.进行sha256哈希
		const size_t uSignDataSize = 32;  //256 = 32 * 8
		unsigned  char *pSignData = new unsigned  char[uSignDataSize]; //32 byte 即可
		memset(pSignData, 0, uSignDataSize);
		memcpy(pSignData, strBinHexDigest.data(), strBinHexDigest.size() );


		const size_t uNonceShaDataSize = 32;  //256 = 32 * 8
		unsigned  char *pCustomNonceData = new unsigned  char[uNonceShaDataSize]; //32 byte 即可
		memset(pCustomNonceData, 0, uNonceShaDataSize);


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
		std::string  strTmpBinHexDigest = strBinHexDigest;
		if (n > 0)
		{
			strTmpBinHexDigest.append(n, 0);
		}
		unsigned char *pDigest = (unsigned char *)strTmpBinHexDigest.c_str();
		SHA256(pDigest, strTmpBinHexDigest.size(), pCustomNonceData);
#endif

		//std::cout << "sha:" << Bin2HexStr(pSha256Out, 256 / 8) << std::endl;
		/*for (size_t i = 0; i < uSha256Size; i++)
		{
			printf("%d,", pSha256Out[i]);
		}
		printf("\n\n");
		*/





		//3.进行签名
		unsigned char uszPrivKey[] = { 111, 173, 7, 191, 113, 102, 175, 50, 200, 100, 236, 115, 13, 248, 168, 62, 168, 126, 235, 134, 115, 247, 88, 232, 1, 240, 54, 224, 16, 0, 114, 63 };
		std::string strPrivKey = Bin2HexStr(uszPrivKey, sizeof(uszPrivKey));

		auto* ctx = getCtx();

		secp256k1_ecdsa_recoverable_signature rawSig;
		memset(&rawSig.data, 0, 65);
		if (!secp256k1_ecdsa_sign_recoverable(ctx, &rawSig, pSignData, uszPrivKey, nullptr, pCustomNonceData))
		{
			std::cout << "secp256k1_ecdsa_sign_recoverable 失败" << std::endl;
			return;
		}

		int iRecid = 0;
		unsigned char uszSigData[520 / 8] = { 0 }; memset(uszSigData, 0, sizeof(uszSigData));
		secp256k1_ecdsa_recoverable_signature_serialize_compact(ctx, uszSigData, &iRecid, &rawSig);


		



		string strR = Bin2HexStr(uszSigData, 32);
		string strS = Bin2HexStr(uszSigData + 32, 32);

		std::cout << "r:" << Bin2HexStr(uszSigData, 32) << std::endl;
		std::cout << "s:" << Bin2HexStr(uszSigData + 32, 32) << std::endl;

		std::cout << "--------------" << std::endl;
		


		//TODO:

		delete[] pSignData; pSignData = NULL;
		delete[] pCustomNonceData;  pCustomNonceData = NULL;
		//delete[]pJsonBuf; pJsonBuf = NULL;
		//delete[]pBase64Out; pBase64Out = NULL;

		std::string strTmpSig;
		strTmpSig.append((char *)uszSigData, sizeof(uszSigData));
		if (!IsCanonical_RS(strTmpSig))
		{
			continue;
		}

		strTmpSig.insert(0, 1, (char)iRecid);

		std::cout << "符合要求的签名结果: " << Bin2HexStr((unsigned char *)strTmpSig.data(), strTmpSig.size()) << std::endl;

		break;
	}


	std::cout << std::endl << std::endl << "---------------恭喜! 所有测试都成功!---------------------------" << std::endl << std::endl;
}





std::string check_encode(unsigned char *pIRS, unsigned int _len = 65)
{
	//使用 K1
	std::string strCheck = Bin2HexStr(pIRS, _len);
	std:string strBinCheck  =  HexToBin(strCheck);
	//strBinCheck.append("K1", 2);
	strBinCheck.append(1, 0x4b);
	strBinCheck.append(1, 0x31);


	//char s_buf[] = "admin";
	unsigned char d_buf[10000]{ 0 };
	unsigned int d_len = 10000;
	get_digest(EVP_ripemd160(), strBinCheck.data(), strBinCheck.size(), d_buf, &d_len, "ripemd160");

	std::string strChkSum;
	strChkSum.append((const char *)d_buf, 4); //取前4个字节
	std::string strTmp = std::string((char *)pIRS, 65) + strChkSum;



	std::string text = strTmp;
	int len = text.size();
	unsigned char *encoded = new unsigned char[len * 137 / 100 + 1];
	memset(encoded, 0, len * 137 / 100 + 1);
	base58encode(text, len, encoded);
	printf("%s\n", encoded); // "StV1DL6CwTryKyV"

	std::string strRet  = std::string("SIG_K1_") +  std::string((char *)encoded);
	delete encoded;
	return strRet;
}


//测试成功 https://jungle.bloks.io/transaction/9e294c0e7ad1ca4bd1ff49d917d8ac7151ceaec1f0d20e1e5cc610bee0ae59eb
void EOSSigTestEx()
{


	std::string strHexDigest = "0x6aa8c53885c91dbc9de7910f2c5a5ad40d35c192a43ef5f3a70ff2dc1c98da0a";
	std::string strBinHexDigest = HexToBin(strHexDigest);


	for (int n = 0; ; n++)
	{


		//2.进行sha256哈希
		const size_t uSignDataSize = 32;  //256 = 32 * 8
		unsigned  char *pSignData = new unsigned  char[uSignDataSize]; //32 byte 即可
		memset(pSignData, 0, uSignDataSize);
		memcpy(pSignData, strBinHexDigest.data(), strBinHexDigest.size());


		const size_t uNonceShaDataSize = 32;  //256 = 32 * 8
		unsigned  char *pCustomNonceData = new unsigned  char[uNonceShaDataSize]; //32 byte 即可
		memset(pCustomNonceData, 0, uNonceShaDataSize);


#ifdef USE_OPENSSL_SHA256
		std::string  strTmpBinHexDigest = strBinHexDigest;
		if (n > 0)
		{
			strTmpBinHexDigest.append(n, 0);
		}
		unsigned char *pDigest = (unsigned char *)strTmpBinHexDigest.c_str();
		SHA256(pDigest, strTmpBinHexDigest.size(), pCustomNonceData);
#endif



		//3.进行签名
		unsigned char uszPrivKey[] = { 111, 173, 7, 191, 113, 102, 175, 50, 200, 100, 236, 115, 13, 248, 168, 62, 168, 126, 235, 134, 115, 247, 88, 232, 1, 240, 54, 224, 16, 0, 114, 63 };
		std::string strPrivKey = Bin2HexStr(uszPrivKey, sizeof(uszPrivKey));

		auto* ctx = getCtx();

		secp256k1_ecdsa_recoverable_signature rawSig;
		memset(&rawSig.data, 0, 65);
		if (!secp256k1_ecdsa_sign_recoverable(ctx, &rawSig, pSignData, uszPrivKey, nullptr, pCustomNonceData))
		{
			std::cout << "secp256k1_ecdsa_sign_recoverable 失败" << std::endl;
			return;
		}

		int iRecid = 0;
		unsigned char uszSigData[520 / 8] = { 0 }; memset(uszSigData, 0, sizeof(uszSigData));
		secp256k1_ecdsa_recoverable_signature_serialize_compact(ctx, uszSigData, &iRecid, &rawSig);



		string strR = Bin2HexStr(uszSigData, 32);
		string strS = Bin2HexStr(uszSigData + 32, 32);

		std::cout << "r:" << Bin2HexStr(uszSigData, 32) << std::endl;
		std::cout << "s:" << Bin2HexStr(uszSigData + 32, 32) << std::endl;

		std::cout << "--------------" << std::endl;



		//TODO:

		delete[] pSignData; pSignData = NULL;
		delete[] pCustomNonceData;  pCustomNonceData = NULL;
		//delete[]pJsonBuf; pJsonBuf = NULL;
		//delete[]pBase64Out; pBase64Out = NULL;

		std::string strTmpSig;
		strTmpSig.append((char *)uszSigData, sizeof(uszSigData) - 1/*去掉i*/);
		if (!IsCanonical_RS(strTmpSig))
		{
			continue;
		}

		strTmpSig.insert(0, 1, (char)(iRecid + 4 + 27));

		std::cout << "符合要求的签名结果: " << Bin2HexStr((unsigned char *)strTmpSig.data(), strTmpSig.size()) << std::endl;


		std::cout << check_encode((unsigned char*)strTmpSig.data(), strTmpSig.size()) << std::endl;

		break;
	}


	std::cout << std::endl << std::endl << "---------------恭喜! 所有测试都成功!---------------------------" << std::endl << std::endl;
}








//测试  ripedmd160 算法
void  TestRipemd160()
{
	char s_buf[] = "admin";
	unsigned char d_buf[10000]{ 0 };
	unsigned int s_len = strlen(s_buf);
	unsigned int d_len = 10000;
	get_digest(EVP_ripemd160(), s_buf, s_len, d_buf, &d_len, "ripemd160");
}


//

void TestBase58()
{
	std::string data =  "1f3b1ac9c7f4fda5044cae0f24042e6267be8a900e1bed35a39254e7fdd5a192622caef9ba81535f27ba4694a09b724d4379f7b56f6b12780486bc9c2fc9153732";
	data += "72352af3";

	std::string text = HexToBin(data);
	int len = text.length();
	unsigned char *encoded = new unsigned char[len * 137 / 100 + 1];
	//unsigned char *encoded = (unsigned char *)malloc(len * 137 / 100 );
	memset(encoded, 0, len*137 / 100 + 1 );
	base58encode(text, len, encoded);
	printf("%s", encoded); // "StV1DL6CwTryKyV"

	//free(encoded);
	//delete[] encoded;
	delete encoded;
}


void TestCheckEncode()
{
	std::string strData = "1f3b1ac9c7f4fda5044cae0f24042e6267be8a900e1bed35a39254e7fdd5a192622caef9ba81535f27ba4694a09b724d4379f7b56f6b12780486bc9c2fc9153732";
	std::string strBin = HexToBin(strData);
	
	std::string strRet = check_encode((unsigned char *)strBin.data(), 65);
	std::cout << strRet << std::endl;
}


//base58解码
//将  WIF格式的私钥 转为 原始字节形式
// 步骤:
//  1. 将 WIF格式私钥 Base58解码, 得到字节数组  privBytes[]
//  2. 截取  privBytes[1 : 33] 的32字节得到  privKey 
//          privBytes[0] 是版本号
//          privBytes[33 : 37] 的 4字节是  校验和
void TestBase58Decode()
{
	//std::string data = "L53fss9LH88FSQHQWMYXWBo7qNwVTGSXteSXcrUkfDmsASNuNDcv";
	std::string data = "5JfUC7k6yGs5RCoHeX464TqZnPWgdqrFfsETBzYGPB9ipDfNyzw";

	std::string text = data ;// HexToBin(data);
	int len = text.length();
	unsigned char *encoded = new unsigned char[len * 137 / 100 + 1];
	//unsigned char *encoded = (unsigned char *)malloc(len * 137 / 100 );
	memset(encoded, 0, len * 137 / 100 + 1);
	//base58encode(text, len, encoded);
	int iLen =  base58decode(text, len, encoded);

	std::cout << Bin2HexStr(encoded, iLen) << std::endl;


	std::string strPrivKey((char *)encoded + 1, 32);

	std::cout << "privKey:" << Bin2HexStr((unsigned char *)strPrivKey.data(), 32) << std::endl;
	

	//std::cout << string((char *)encoded) << std::endl;
	//printf("%s", encoded); // "StV1DL6CwTryKyV"

	//free(encoded);
	//delete[] encoded;
	delete encoded;
}


#include "eos_tx_sign.h"


//正常参数
void TestEosSignAPI_Case1()
{
	std::string strHexDigest = "0xb4611834077ee2a5be9480f210c6aa3c129e69e1ee25e2448870654b849a77c1";
	std::string strBinHexDigest = HexToBin(strHexDigest);

	char *pszWIFKey = "5JfUC7k6yGs5RCoHeX464TqZnPWgdqrFfsETBzYGPB9ipDfNyzw";

	char szOutData[1024] = { 0 };
	memset(szOutData, 0, sizeof(szOutData));
	unsigned int uOutDataLen = 0;
	int iRet = eos::EosTxSignWithWIFKey(pszWIFKey, (unsigned char *)strBinHexDigest.data(), strBinHexDigest.size(), szOutData, &uOutDataLen);
	if (0 != iRet)
	{
		printf(" EOS::EosTxSignWithWIFKey  failed.  error no: %d\n", iRet);
		return;
	}

	if (0 != strcmp(szOutData, "SIG_K1_K11vtuZpzujG3jHUAURVnypmg4YTDJPDXMzGJWySp7qzdJoFo4VaNpkc4A5jrH7FDzf1Zkw7PVjZHpkdBHd2Ca34X1vghP"))
		printf("签名结果比对失败!\n");
	else
		printf("签名结果比对成功!\n");

	printf("sig result:  %s\n", szOutData);
}



//私钥长度不对
void TestEosSignAPI_Case2()
{
	std::string strHexDigest = "0xb4611834077ee2a5be9480f210c6aa3c129e69e1ee25e2448870654b849a77c1";
	std::string strBinHexDigest = HexToBin(strHexDigest);

	char *pszWIFKey = "JfUC7k6yGs5RCoHeX464TqZnPWgdqrFfsETBzYGPB9ipDfNyzw"; 

	char szOutData[1024] = { 0 };
	memset(szOutData, 0, sizeof(szOutData));
	unsigned int uOutDataLen = 0;
	int iRet = eos::EosTxSignWithWIFKey(pszWIFKey, (unsigned char *)strBinHexDigest.data(), strBinHexDigest.size(), szOutData, &uOutDataLen);
	if (-1 != iRet)
	{
		printf("case 测试失败 \n");
		return;
	}
	else
	{
		printf("case 测试成功  \n");
		return;
	}
}

//签名数据长度不对
void  TestEosSignAPI_Case3()
{
	std::string strHexDigest = "0x611834077ee2a5be9480f210c6aa3c129e69e1ee25e2448870654b849a77c1";
	std::string strBinHexDigest = HexToBin(strHexDigest);

	char *pszWIFKey = "5JfUC7k6yGs5RCoHeX464TqZnPWgdqrFfsETBzYGPB9ipDfNyzw";

	char szOutData[1024] = { 0 };
	memset(szOutData, 0, sizeof(szOutData));
	unsigned int uOutDataLen = 0;
	int iRet = eos::EosTxSignWithWIFKey(pszWIFKey, (unsigned char *)strBinHexDigest.data(), strBinHexDigest.size(), szOutData, &uOutDataLen);
	if (-1 != iRet)
	{
		printf("case 测试失败 \n");
		return;
	}
	else
	{
		printf("case 测试成功 \n ");
		return;
	}
}




int main()
{
	//TestSha256();
	//Test_StrToJsonObj();
	//SigTest();
	//EOSSigTest();


	//TestCheckEncode();

	//TestBase58();
	//TestRipemd160();
	//EOSSigTestEx();
	//TestBase58Decode();


	//TestEosSignAPI_Case1();
	//TestEosSignAPI_Case2();
	TestEosSignAPI_Case3();

	std::cout << "Hello World!\n";
	system("pause");
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
