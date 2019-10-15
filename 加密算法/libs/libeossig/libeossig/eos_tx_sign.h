#ifndef  __EOS_TX_SIGN__
#define  __EOS_TX_SIGN__



#ifdef MY_DLL_API
#define MY_DLL_API __declspec(dllexport)
#else
#define MY_DLL_API __declspec(dllimport)
#endif


namespace eos
{
#ifdef __cplusplus
	extern "C" {
#endif


		//************************************
		// Method:    EosTxSign
		// FullName:  EosTxSign
		// Access:    public 
		// Returns:    0:成功   非0: 失败
		// Qualifier:
		// Parameter: const unsigned char * pPrivKey     私钥(WIF经过转换后的字节形式)
		// Parameter: const unsigned int uPrivKeyLen     私钥长度 (必须是32字节)
		// Parameter: const unsigned char * pInData      要签名的数据
		// Parameter: const unsigned int uInDataLen      要签名的数据的长度(必须是64字节)
		// Parameter: unsigned char * pOutData			 签名结果
		// Parameter: unsigned int * puOutDataLen        签名结果的长度(65字节)
		//************************************
		/*
		int  EosTxSign(
			const unsigned char *pszPrivKey,
			const unsigned int uPrivKeyLen,
			const unsigned char *pInData,
			const unsigned int uInDataLen,
			char *pOutData,
			unsigned int *puOutDataLen
		);
		*/



		//************************************
		// Method:    EosTxSign
		// FullName:  EosTxSign
		// Access:    public 
		// Returns:    0:成功   非0: 失败
		// Qualifier:
		// Parameter: const unsigned char * pPrivKey     WIF格式的私钥
		// Parameter: const unsigned char * pInData      要签名的数据
		// Parameter: const unsigned int uInDataLen      要签名的数据的长度(必须是64字节)
		// Parameter: unsigned char * pOutData			 签名结果
		// Parameter: unsigned int * puOutDataLen        签名结果的长度(65字节)
		//************************************
		MY_DLL_API int  EosTxSignWithWIFKey(
			const char *pszWIFPrivKey,
			const unsigned char *pInData,
			const unsigned int uInDataLen,
			char *pOutData,
			unsigned int *puOutDataLen
		);


		//************************************
		// Returns:   int          0:成功     非0: 失败
		// Parameter: const char * pszWIFKey           WIF格式的私钥
		// Parameter: unsigned char * pDecodedKey      解码后的私钥
		// Parameter: unsigned int * puDecodedKeyLen   解码后的私钥长度(32字节)
		//************************************
		/*int DecodeWIFPrivKey(
			const char *pszWIFKey,
			unsigned char *pDecodedKey,
			unsigned int *puDecodedKeyLen
		);*/


#ifdef __cplusplus
	}
#endif



};


#endif // __EOS_TX_SIGN__
