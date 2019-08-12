// SHA1WithRSA.cpp : 此文件包含 "main" 函数。程序执行将在此处开始并结束。
//

#include "pch.h"

#include <stdio.h>
#include <string.h>
#include <string>
//#include <openssl/sha.h>
#include <iostream>
#include "crypto_utils.h"
using namespace std;



#define N_SHA_DIGEST_LENGTH  (256/8)


#define  STR_TEST "good"
#define  STR_SHA256_RIGHT_RESULT "770e607624d689265ca6c44884d0807d9b054d23c473c106c72be9de08b7376c"

int SHA256_Test()
{

	unsigned char uszRetData[N_SHA_DIGEST_LENGTH];
	memset(uszRetData, 0, sizeof(uszRetData));
	char szTest[] = STR_TEST;

	//SHA1((unsigned char*)&string, strlen(string), (unsigned char*)&digest);
	SHA256((unsigned char*)&szTest, strlen(szTest), (unsigned char*)&uszRetData);

	char szSha256[N_SHA_DIGEST_LENGTH * 2 + 1];
	memset(szSha256, 0, sizeof(szSha256));

	for (int i = 0; i < N_SHA_DIGEST_LENGTH; i++)
	{
		sprintf(&szSha256[i * 2], "%02x", (unsigned int)uszRetData[i]);
	}

	printf("SHA256 digest: %s\n", szSha256);


	if (0 == strcmp(szSha256, STR_SHA256_RIGHT_RESULT))
	{
		printf("SHA256 算法匹配成功!\n");
	}
	else
	{
		printf("SHA256 算法匹配失败!\n");
	}

	return 0;

}




int Base64_Test()
{
	const char *pszTest = "good";

	std::string strEncoded =  CryptoUtils::Base64Encode(pszTest, strlen(pszTest), false);
	std::cout << "Base64 Encoded:" << strEncoded << std::endl;

	std::string strDecoded = CryptoUtils::Base64Decode(strEncoded.c_str(), strEncoded.length(), false);
	std::cout << "Base64 Decoded:" <<  strDecoded  << std::endl;

	return 0;
}




#if 1
#define  STR_PRIV_KEY_FILE_PATH "rsa_private_key.pem"
#define  STR_PUB_KEY_FILE_PATH "rsa_public_key.pem"
#else
#define  STR_PRIV_KEY_FILE_PATH "private_pkcs8.pem"
#define  STR_PUB_KEY_FILE_PATH "public_pkcs8.pem"
#endif

//RSA 加密测试
int RSA_Enc_Test()
{

	unsigned char out[2048] = STR_TEST;
	unsigned char rsa[2048] = { 0 };
	memset(rsa, 0, sizeof(rsa));
	int outlen = 0, rsalen = 0;
	int ret = 0;
	printf("in [%s]\n", out);
	/* ret=my_rsa_prikey_encrypt("prikey.pem",out,strlen(out),rsa,&rsalen);
	if(ret<0)
	{
	printf("my_rsa_prikey_encrypt err [%d]\n",ret);
	return -1;
	}
	printf("my_rsa_prikey_encrypt ok,rsalen is [%d]\n",rsalen);
	memset(out,0,sizeof(out));
	ret=my_rsa_public_decrypt("pubkey.pem",rsa,rsalen,out,&outlen);
	if(ret<0)
	{
	printf("my_rsa_public_decrypt err [%d]\n",ret);
	return -2;
	}
	*/

	ret = CryptoUtils::RSA_EncrptByPubkey((char *)STR_PUB_KEY_FILE_PATH, out, strlen((char *)out) ,rsa, &rsalen);
	if (ret < 0)
	{
		printf("my_rsa_public_encrypt err [%d]\n", ret);
		return -1;
	}
	printf("my_rsa_prikey_encrypt ok,rsalen is [%d]\n", rsalen);
	memset(out, 0, sizeof(out));
	ret = CryptoUtils::RSA_DecrptByPrivkey(STR_PRIV_KEY_FILE_PATH, rsa, rsalen, out, &outlen);
	if (ret < 0)
	{
		printf("my_rsa_prikey_decrypt err [%d]\n", ret);
		return -2;
	}


	//printf("out [%s]\n", out);
	return 0;


}


//RSA签名测试

#define  STR_RSA_SIG_HEX_STR_RIGHT_RESULT "c74afa572f7c093275be4bf474b6adeb75775312d474dc6f6754f843b2addd7769c13881faad62e40f14370743849516a2b1e834f5a8070b6a1352cc6b28961d8ee7b09b4e1c00d09ea614c0d94486ce8849332480b99616669943fba73c9a992677f2100a5f687cea44fc92ee13341c2a6fdde9ddbb2c4768b633a73b60795d8ec3e54006626010dcb45694224b7b7bdf316d8eeafd18a7143448cf9c739f42f0604bc0d478735d994036d065e145a51d7bbada928bbf9b304d1847f896508b6a44350b798c2d04d4a356954bfb24aa4b0f74bf386916826a6c752565c48b7c528c89092281f8110a383608ca5c28db8b04e5a7b2b68619a704861e332da4ed"
#define  STR_RSA_SIG_BASE64_ENCODED_RIGHT_RESULT "x0r6Vy98CTJ1vkv0dLat63V3UxLUdNxvZ1T4Q7Kt3XdpwTiB+q1i5A8UNwdDhJUWorHoNPWoBwtqE1LMayiWHY7nsJtOHADQnqYUwNlEhs6ISTMkgLmWFmaZQ/unPJqZJnfyEApfaHzqRPyS7hM0HCpv3enduyxHaLYzpztgeV2Ow+VABmJgENy0VpQiS3t73zFtjur9GKcUNEjPnHOfQvBgS8DUeHNdmUA20GXhRaUde7rakou/mzBNGEf4llCLakQ1C3mMLQTUo1aVS/skqksPdL84aRaCamx1JWXEi3xSjIkJIoH4EQo4NgjKXCjbiwTlp7K2hhmnBIYeMy2k7Q=="


int RSA_Sig_Test()
{

	unsigned char uszInData[2048] = STR_TEST;
	unsigned char uszOutData[2048] = { 0 };
	memset(uszOutData, 0, sizeof(uszOutData));
	//int my_rsa_prikey_sign(char *filename, unsigned char *src, int srclen, unsigned char *des, int *deslen);
	int iRet = -1;


	printf("=============================================\n\n");
	unsigned int uOutLen = 0;
	iRet = CryptoUtils::SHA256WithRSA_Sign(STR_PRIV_KEY_FILE_PATH, uszInData, strlen((char *)uszInData), uszOutData, &uOutLen );
	if (iRet != 0)
	{
		printf("签名失败!\n");
		printf("my_rsa_prikey_sign error [%d]\n", iRet);
		printf("=============================================\n\n");
		return -1;
	}
	printf("签名成功!\n\n");
	printf("=============================================\n\n");

	char szSig[1024] = { 0 };
	memset(szSig, 0, sizeof(szSig));
	for (unsigned int i = 0; i < uOutLen; i++)
	{
		sprintf(&szSig[i * 2], "%02x", (unsigned int)uszOutData[i]);
	}
	printf("签名的十六进制字符形式: %s\n", szSig);
	printf("=============================================\n\n");

	if (0 != strcmp(szSig, STR_RSA_SIG_HEX_STR_RIGHT_RESULT))
	{
		printf("签名的十六进制字符串, 比对失败!\n");
		printf("=============================================\n\n");
	}
	printf("签名的十六进制字符串, 比对成功!\n");
	printf("=============================================\n\n");



	//int my_rsa_public_verify(char *filename, unsigned char *src, int srclen, unsigned char *sign, int signlen);
	iRet = CryptoUtils::SHA256WithRSA_Verify(STR_PUB_KEY_FILE_PATH, uszInData, strlen((char *)uszInData), uszOutData, uOutLen );
	if (iRet != 0)
	{
		printf("my_rsa_public_verify error [%d]\n", iRet);
		printf("验签失败!\n");
		printf("=============================================\n\n");
		return -1;
	}
	printf("验签成功!\n");
	printf("=============================================\n\n");


	std::string strB64Encoded = CryptoUtils::Base64Encode((const char *)uszOutData, uOutLen, false);

	if (0 != strB64Encoded.compare(STR_RSA_SIG_BASE64_ENCODED_RIGHT_RESULT))
	{
		printf("签名数据的base64编码字符, 比对失败!\n");
		printf("=============================================\n\n");
	}
	printf("签名数据的base64编码字符, 比对成功!\n");
	printf("=============================================\n\n");
	
	std::cout << "base64编码后: " << strB64Encoded << std::endl;
	printf("=============================================\n\n");


	return 0;
}









void AES_Test()
{
	unsigned char *puszKey = (unsigned char *)"9999999999999999";
	unsigned char *puszIV = (unsigned char *)"qqqqqqqqqqqqqqqq";
	unsigned char *puszTest = (unsigned char *)"good";
	int nInDataLen = strlen((char *)puszTest);
	unsigned int nEncOutLen = 0;
	unsigned char szEncData[1024];
	memset(szEncData, 0, sizeof(szEncData));

	CryptoUtils::AES_128_CBC_Encrypt(puszTest, nInDataLen, puszKey, puszIV, szEncData, &nEncOutLen );


	std::cout << CryptoUtils::Base64Encode((const char *)(szEncData), nEncOutLen, false) << std::endl;


	unsigned char szDecData[1024];
	memset(szDecData, 0, sizeof(szDecData));
	unsigned int nDecLen = 0;
	CryptoUtils::AES_128_CBC_Decrypt(szEncData, nEncOutLen, puszKey, puszIV, szDecData, &nDecLen);

	szDecData[nDecLen] = '\0';
	std::cout << szDecData << std::endl;
}



int main()
{
	//Base64_Test(); //base64测试用例
	//SHA256_Test();  //SHA256测试用例
	//RSA_Enc_Test(); //RSA加密测试用例
	//RSA_Sig_Test(); //RSA签名测试用例
	AES_Test();

	std::cout << "Hello World!\n";
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
