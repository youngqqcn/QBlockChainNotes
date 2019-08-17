/*
	This file is part of cpp-ethereum.

	cpp-ethereum is free software: you can redistribute it and/or modify
	it under the terms of the GNU General Public License as published by
	the Free Software Foundation, either version 2 of the License, or
	(at your option) any later version.

	Foobar is distributed in the hope that it will be useful,
	but WITHOUT ANY WARRANTY; without even the implied warranty of
	MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
	GNU General Public License for more details.

	You should have received a copy of the GNU General Public License
	along with Foobar.  If not, see <http://www.gnu.org/licenses/>.
*/
/** @file Transaction.cpp
 * @author Gav Wood <i@gavwood.com>
 * @date 2014
 */

/*
author: yqq    
email:youngqqcn@gmail.com  
github: github.com/youngqqcn
date:2019-04-18
descriptions: 
	implement ehtereum transaction offline signature
	实现ethereum交易离线签名
*/


//#include <secp256k1.h>
#include "Common.h"
#include "RLP.h"
#include "secp256k1/secp256k1.h"
#include "secp256k1/secp256k1_recovery.h"
#include "secp256k1/secp256k1_ecdh.h"
#include "vector_ref.h"
#include "Exceptions.h"


#define MY_DLL_API __declspec(dllexport)
#include "Transaction.h"
using namespace std;
using namespace eth;


#define  INT_SINGED_TX_FILED_COUNT	(9)
#define  INT_SIG_V_OFFSET			(27)
#define  INT_SIG_INFO_SIZE			(65)  //32(r) + 32(s) + 1(v)


using Sig_t = h520;

struct SignatureStruct
{
	SignatureStruct() = default;
	SignatureStruct(Sig_t const& _s) { *(h520*)this = _s; }
	SignatureStruct(h256 const& _r, h256 const& _s, byte _v) : r(_r), s(_s), v(_v) {}
	operator Sig_t() const { return *(h520 const*)this; }

	/// @returns true if r,s,v values are valid, otherwise false
	bool isValid() const noexcept
	{
		{
			static const h256 s_max{ fromUserHex("0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141") };
			static const h256 s_zero;

			return (v <= 1 && r > s_zero && s > s_zero && r < s_max && s < s_max);
		}

	}

	h256 r;
	h256 s;
	byte v = 0;
};

typedef struct _SIG
{
	byte v;
	u256 r;
	u256 s;
}VRS_SIG;

static const u256 c_secp256k1n("115792089237316195423570985008687907852837564279074904382605163141518161494337");

inline secp256k1_context const* getCtx()
{
	static std::unique_ptr<secp256k1_context, decltype(&secp256k1_context_destroy)> s_ctx{
		secp256k1_context_create(SECP256K1_CONTEXT_SIGN | SECP256K1_CONTEXT_VERIFY),
		&secp256k1_context_destroy
	};
	return s_ctx.get();
}




int eth::Transaction::Sign(const EthTxData &ethTxData, const char * pszPrivKey,  unsigned char *pOutBuf, unsigned int uBufLen, unsigned int *puOutLen)
{
	//1.准备数据
	uint	m_uChainId  = ethTxData.uChainId;							//chainid
	u256	m_u256Nonce(std::string(ethTxData.pszNonce));				//nonce, 此值应是发送地址的交易集中的最大nonce值加1,
	u256	m_u256Value(std::string(ethTxData.pszValue));				//金额(wei),  1(eth)=10^18(wei), 单位:wei
	u256	m_u256GasPrice(std::string(ethTxData.pszGasPrice));			//gasprice, 一次操作所需gas, 单位:wei
	u256	m_u256GasStart(std::string(ethTxData.pszGasStart));			//gasstart,也成 gaslimit, 单位:wei
	Address	m_addrTo(fromUserHex(std::string(ethTxData.pszAddrTo)));	//to,  目的地址
	VRS_SIG m_vrsSig = VRS_SIG{ (byte)m_uChainId, 0, 0 };				//v,r,s  签名信息;  TODO: 如果私链的chainId过大, 存在问题

	bytes	m_bytesData;	//data,  附加数据,默认为空
	for (unsigned int i = 0; i < ethTxData.uDataLen; i++)
	{
		m_bytesData.push_back(ethTxData.pData[i]);
	}

	h256 rawHash;
	if (true)
	{
		try
		{
			RLPStream s;
			s.appendList((ETHChainID::None == m_uChainId) ? 6 : 9);
			s << m_u256Nonce << m_u256GasPrice << m_u256GasStart << m_addrTo << m_u256Value << m_bytesData;

			if (ETHChainID::None == m_uChainId)
			{
				rawHash = sha3(s.out());
			}
			else if (ETHChainID::Mainnet == m_uChainId
				|| ETHChainID::Rinkeby == m_uChainId
				|| ETHChainID::Goerli == m_uChainId
				|| ETHChainID::Ropsten == m_uChainId
				|| ETHChainID::Kovan == m_uChainId)
			{
				s << m_vrsSig.v << m_vrsSig.r << m_vrsSig.s;
				rawHash = sha3(s.out());
			}
			else
			{
				std::cout << "错误的chainId" << std::endl;
				return ETH_ERRCODE::ETH_ERR_ErrChainID;
			}
		}
		catch (std::exception &e)
		{
			std::cout << e.what() << std::endl;
			return  ETH_ERRCODE::ETH_ERR_BadRLP;
		}

	}


	//2.进行签名
	Secret privKey(fromUserHex(std::string(pszPrivKey)));
	if (true)
	{
		h256 _hash = rawHash;
		Secret _priv = privKey;
		std::cout << "--------------" << std::endl;
		std::cout << "sha3:" << _hash << std::endl;
		std::cout << "--------------" << std::endl;
		Secret& _k = _priv;


		auto* ctx = getCtx();

		secp256k1_ecdsa_recoverable_signature rawSig;
		memset(&rawSig.data, 0, INT_SIG_INFO_SIZE);
		if (!secp256k1_ecdsa_sign_recoverable(ctx, &rawSig, _hash.data(), _k.data(), nullptr, nullptr))
		{
			std::cout << "secp256k1_ecdsa_sign_recoverable 失败" << std::endl;
			return ETH_ERRCODE::ETH_ERR_SECP256K1_ECDSA_SIGN_RECOVERABLE_faild;
		}


		std::string strRawSig1 = Bin2HexStr((unsigned char *)&rawSig, INT_SIG_INFO_SIZE);
		std::cout << "rawsig1 hex:" << strRawSig1 << std::endl;


		Sig_t s;
		int iRecid = 0;
		memset((unsigned char *)s.data(), 0, INT_SIG_INFO_SIZE);
		secp256k1_ecdsa_recoverable_signature_serialize_compact(ctx, s.data(), &iRecid, &rawSig);

		SignatureStruct& ss = *reinterpret_cast<SignatureStruct*>(&s);
		ss.v = static_cast<byte>(iRecid);
		if (ss.s > c_secp256k1n / 2)
		{
			ss.v = static_cast<byte>(ss.v ^ 1);
			ss.s = h256(c_secp256k1n - u256(ss.s));
		}
		//assert(ss.s <= c_secp256k1n / 2);
		if (ss.s > c_secp256k1n / 2)
		{
			return ETH_ERR_INVALID_SIG;
		}

		m_vrsSig.r = (u256)(ss.r);
		m_vrsSig.s = (u256)(ss.s);
		if (ETHChainID::None == m_uChainId)
		{
			m_vrsSig.v = INT_SIG_V_OFFSET;
		}
		else
		{
			m_vrsSig.v = (byte)ss.v + 8 + m_vrsSig.v * 2 + INT_SIG_V_OFFSET;
		}


#if ETH_ADDRESS_DEBUG
		std::cout << "-------------------------- 签名信息 -------------------------------" << endl;
		cout << "RawHash: " << rawHash << endl;
		std::cout << "nonce: " << m_u256Nonce << endl;
		std::cout << "私钥: " << _priv << endl;
		std::cout << "r: " << m_vrsSig.r << std::endl;
		std::cout << "s: " << m_vrsSig.s << std::endl;
		std::cout << "v: " << (int)m_vrsSig.v << std::endl;
		std::cout << "-----------------------------------------------------------------" << endl;
#endif


		if (false == ss.isValid())
		{
			std::cout << "签名无效" << std::endl;
			return ETH_ERRCODE::ETH_ERR_INVALID_SIG;
		}
		std::cout << "签名有效" << std::endl;
	}


	//3.获取签名后的rlp编码格式的数据
	try
	{
		RLPStream s;
		s.appendList(INT_SINGED_TX_FILED_COUNT);
		s << m_u256Nonce << m_u256GasPrice << m_u256GasStart << m_addrTo << m_u256Value << m_bytesData;
		s << m_vrsSig.v << m_vrsSig.r << m_vrsSig.s;

		int iRet = s.getData(pOutBuf, uBufLen, puOutLen);
		if (0 != iRet)
		{
			std::cout << "getData error" << std::endl;
			return ETH_ERR_BadRLP;
		}
		std::cout << "getData成功" << std::endl;


		std::string strHex;
		for (unsigned int i = 0; i < *puOutLen; i++)
		{
			char buf[10] = { 0 };
			memset(buf, 0, sizeof(buf));
			sprintf(buf, "%02x", pOutBuf[i]);
			strHex += buf;
		}
		std::cout << "签名后的数据:" << strHex << std::endl;

	}
	catch (std::exception &e)
	{
		std::cout << e.what() << std::endl;
		return ETH_ERR_BadRLP;
	}

	return ETH_ERRCODE::ETH_NO_ERROR;
}
