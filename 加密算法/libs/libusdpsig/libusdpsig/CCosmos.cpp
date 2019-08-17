
/************************************************************************
作者: yqq
日期: 2019-05-08  14:25
说明: Cosmos类币的签名库  支持 (USDP, HTDF)
************************************************************************/
#include "CCosmos.h"


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



int cosmos::ECDSA_Sign(
	unsigned char *pszIn, 
	unsigned int uInLen, 
	unsigned char *pszPrivKey, 
	unsigned int uPrivKeyLen, 
	unsigned char *pszOut,
	unsigned int uOutBufLen,
	unsigned int *puOutDataLen, 
	char *pszErrMsg)
{
	//1.检查参数
	if (NULL == pszErrMsg)
	{
		return  cosmos::ARGS_ERROR;
	}

	if (NULL == pszIn)
	{
		strcpy(pszErrMsg , "pszIn is null.");
		return  cosmos::ARGS_ERROR;
	}

	if (0 == uInLen)
	{
		strcpy(pszErrMsg, "uInLen is 0.");
		return  cosmos::ARGS_ERROR;
	}

	if (NULL == pszPrivKey)
	{
		strcpy(pszErrMsg, "pszPrivKey is null.");
		return cosmos::ARGS_ERROR;
	}

	if ( UINT_PRIV_KEY_LEN != uPrivKeyLen)
	{
		sprintf(pszErrMsg, "priv-key len is not %d bytes.", UINT_PRIV_KEY_LEN);
		return cosmos::ARGS_ERROR;
	}

	if (NULL == pszOut)
	{
		strcpy(pszErrMsg, "pszOut is null.");
		return  cosmos::ARGS_ERROR;
	}

	if (uOutBufLen < UINT_SIG_RS_LEN)
	{
		sprintf(pszErrMsg, "uOutBufLen less than %d. Must more than %d.", UINT_SIG_RS_LEN, UINT_SIG_RS_LEN);
		return cosmos::ARGS_ERROR;
	}

	if (NULL == puOutDataLen)
	{
		strcpy(pszErrMsg, "puOutDataLen is null");
		return  cosmos::ARGS_ERROR;
	}


	//2.进行签名
	auto* ctx = getCtx();

	secp256k1_ecdsa_recoverable_signature rawSig;
	memset(&rawSig.data, 0, 65);
	if (!secp256k1_ecdsa_sign_recoverable(ctx, &rawSig, pszIn, pszPrivKey, nullptr, nullptr))
	{
		strcpy(pszErrMsg, "secp256k1_ecdsa_sign_recoverable  faield.");
		return cosmos::ECCSIGN_STEP1_ERROR;
	}

	int iRecid = 0;
	unsigned char uszSigRSData[UINT_SIG_RS_LEN] = { 0 }; 
	memset(uszSigRSData, 0, sizeof(uszSigRSData));
	secp256k1_ecdsa_recoverable_signature_serialize_compact(ctx, uszSigRSData, &iRecid, &rawSig);


	//返回数据
	memcpy(pszOut, uszSigRSData, UINT_SIG_RS_LEN);
	*puOutDataLen = UINT_SIG_RS_LEN;


	return cosmos::NO_ERROR;
}
