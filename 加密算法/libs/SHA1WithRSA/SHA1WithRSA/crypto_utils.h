/****************************************************************
author: yqq
date: 2019-08-02
email: youngqqcn@gmail.com
descriptions: crypto tools
******************************************************************/



#ifndef __CRYPTO_UTILS__
#define __CRYPTO_UTILS__

extern "C" {
#include <openssl/rsa.h>
#include <openssl/err.h>
#include <openssl/pem.h> 

#include <openssl/evp.h>
#include <openssl/bio.h>
#include <openssl/buffer.h>


#include <openssl/aes.h>

};

#include<stdio.h>
#include<string.h>
#include <string>
#include <iostream>




namespace  CryptoUtils 
{

	//关于 几个函数的说明
	//https://linux.die.net/man/3/pem_read_rsa_pubkey


	//关于 OpenSSL EVP 库的详细解析  
	//https://blog.csdn.net/liao20081228/article/details/76285896

	//关于 OpenSSL BIO 库的详细解析 
	//https://blog.csdn.net/liao20081228/article/details/77193729
	//https://blog.csdn.net/liujiayu2/article/details/51860172


	//
	/*my_rsa_public_encrypt公钥加密与my_rsa_public_encrypt公钥解密配对
		公钥加密,读取pubkey.pem来做加密
		入参filename,保存公钥的文件名称，src待加密数据，加密数据长度
		出参des加密后数据，deslen加密数据长度
		src长度大于公钥长度时（RSA_size）,会分段加密。
		加密结果des比src长度大,所以需要给des分配比src更大的空间
		例如密钥长度（RSA_size）为128，src长度为1~117,加密结果为128个字节。src长度为118~234,加密结果为256字节
	*/
	int RSA_EncrptByPubkey(
		const char *pszPubKeyFilePath,
		const unsigned char *puszInData,
		int uInDataLen,
		unsigned char *puszOutData,
		int *puOutDataLen);




	/*私钥解密,读取prikey.pem来做解密
	入参filename,保存公钥的文件名称，src待解密数据，srclen解密数据长度
	出参des解密后数据，deslen解密数据长度*/
	int RSA_DecrptByPrivkey(
		const char *pszPrivKeyFilePath,
		const unsigned char *puszInData,
		int uInDataLen,
		unsigned char *puszOutData,
		int *puOutDataLen);

    int RSA_DecrptByPrivkeyEx(
		const char *pszPrivKeyFilePath,
		const unsigned char *puszInData,
		int uInDataLen,
		unsigned char *puszOutData,
		int *puOutDataLen,
        const unsigned char *puszPassword);


	/*my_rsa_prikey_encrypt私钥加密与my_rsa_public_decrypt公钥解密配对
			私钥加密,读取prikey.pem来做加密。
			入参filename,保存公钥的文件名称，src待加密数据，加密数据长度
			出参des加密后数据，deslen加密数据长度
			src长度大于公钥长度时（RSA_size）,会分段加密。
			加密结果des比src长度大,所以需要给des分配比src更大的空间
			例如密钥长度（RSA_size）为128，src长度为1~117,加密结果为128个字节。src长度为118~234,加密结果为256字节
			因此des的长度，应该比 RSA_size*（strlen(src)/(RSA_size-11)+1）大才行。
		*/
		//私钥加密
	int RSA_EncrptByPrivKey(
		const char *pszPrivKeyFilePath,
		const unsigned char *puszInData,
		int uInDataLen,
		unsigned char *puszOutData,
		int *puOutDataLen);

    int RSA_EncrptByPrivKeyEx(
		const char *pszPrivKeyFilePath,
		const unsigned char *puszInData,
		int uInDataLen,
		unsigned char *puszOutData,
		int *puOutDataLen,
        const unsigned char *puszPassword);


	/*
		公钥解密,读取public.pem来做解密
		入参filename,保存公钥的文件名称，src待解密数据，srclen解密数据长度
		出参des解密后数据，deslen解密数据长度
	*/
	//公钥解密
	int RSA_DecryptByPubkey(
		const char *pszPubKeyFilePath,
		const unsigned char *puszInData,
		int uInDataLen,
		unsigned char *puszOutData,
		int *puOutLen);


	/* my_EVP_rsa_prikey_sign私钥签名,使用EVP
		入参filename,私钥文件名称；
				src待签名数据；
				srclen待签名数据长度
		出参des签名结果,返回结果长度为秘钥长度值,需分配比秘钥长度更大的空间，以免内存越界
				deslen签名数据长度，初始化为des数组大小
	*/
	int SHA256WithRSA_Sign(
		const char *pszPrivKeyFilePath,
		const unsigned char *puszInData,
		unsigned int uInDataLen,
		unsigned char *puszOutSig,
		unsigned int *puOutSigLen);

    int SHA256WithRSA_Sign_Ex(
		const char *pszPrivKeyFilePath,
		const unsigned char *puszInData,
		unsigned int uInDataLen,
		unsigned char *puszOutSig,
		unsigned int *puOutSigLen,
        const unsigned char *pPassword);



	/* my_EVP_rsa_public_verify公钥签名验证,使用EVP
		入参filename,公钥文件名称
				src待验数据；
				srclen待验数据长度
			sign签名
				signlen签名长度
	*/
	//公钥签名EVP验证
	int SHA256WithRSA_Verify(
		const char *pszPubKeyFilePath,
		const unsigned char *puszInData,
		int uInDataLen,
		unsigned char *puszOutSig,
		unsigned int uOutSigLen);



	//base64编码
	//************************************
	// Method:    Base64Encode
	// FullName:  CryptoUtils::Base64Encode
	// Access:    public 
	// Returns:   std::string  编码后的字符串
	// Qualifier:
	// Parameter: const char * input
	// Parameter: int length   输入数据长度
	// Parameter: bool bWithNewLine   是否允许断行
	//************************************
	std::string Base64Encode(
		const char *pszInData, 
		int nInDataLen, 
		bool bWithNewLine);



	//base64解码
	//************************************
	// Method:    Base64Decode
	// FullName:  CryptoUtils::Base64Decode
	// Access:    public 
	// Returns:   std::string  解码后的数据
	// Qualifier:
	// Parameter: const char * pszInData  输入数据
	// Parameter: int nInDataLen   输入数据长度
	// Parameter: bool bWithNewLine 是否允许断行 
	//************************************
	std::string Base64Decode(
		const char * pszInData,  
		int nInDataLen, 
		bool bWithNewLine);



	//AES128的CBC模式加密
	int AES_128_CBC_Encrypt(
		const unsigned char *puszInData,
		int nInDataLen,
		const unsigned char *puszKey,
		unsigned char *puszIV,
		unsigned char *puszOutData,
		unsigned int *pOutDataLen);


	//AES128的CBC模式解密
	int AES_128_CBC_Decrypt(
		const unsigned char *puszInData,
		int nInDataLen,
		const unsigned char *puszKey,
		unsigned char *puszIV,
		unsigned char *puszOutData,
		unsigned int *pOutDataLen);

}

#endif//__CRYPTO_UTILS__
