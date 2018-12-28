#include "stdafx.h"
#include "des_test.h"


using namespace std;
using namespace CryptoPP;

//参考: https://blog.csdn.net/wangweitingaabbcc/article/details/11170131

void des_test()
{
	//主要是打印一些基本信息，方便调试：
	cout << "DES Parameters: " << endl;
	cout << "Algorithm name : " << DES::StaticAlgorithmName() << endl;

	unsigned char key[DES::DEFAULT_KEYLENGTH];
	unsigned char input[DES::BLOCKSIZE] = "12345";
	unsigned char output[DES::BLOCKSIZE];
	unsigned char txt[DES::BLOCKSIZE];

	cout << "input is: " << input << endl;

	//可以理解成首先构造一个加密器
	DESEncryption encryption_DES;

	//回忆一下之前的背景，对称加密算法需要一个密匙。加密和解密都会用到。
	//因此，设置密匙。
	encryption_DES.SetKey(key, DES::KEYLENGTH);
	//进行加密
	encryption_DES.ProcessBlock(input, output);

	//显示结果
	//for和for之后的cout可有可无，主要为了运行的时候看加密结果
	//把字符串的长度写成一个常量其实并不被推荐。
	//不过笔者事先知道字符串长，为了方便调试，就直接写下。
	//这里主要是把output也就是加密后的内容，以十六进制的整数形式输出。
	for (int i = 0; i < 5; i++)
	{
		cout << hex << (int)output[i] << ends;
	}
	cout << endl;

	//构造一个解密器
	DESDecryption decryption_DES;

	//由于对称加密算法的加密和解密都是同一个密匙，
	//因此解密的时候设置的密匙也是刚才在加密时设置好的key
	decryption_DES.SetKey(key, DES::KEYLENGTH);
	//进行解密，把结果写到txt中
	//decryption_DES.ProcessAndXorBlock( output, xorBlock, txt );
	decryption_DES.ProcessBlock(output, txt);

	//以上，加密，解密还原过程已经结束了。以下是为了验证：
	//加密前的明文和解密后的译文是否相等。
	if (memcmp(input, txt, 5) != 0)
	{
		cerr << "DES Encryption/decryption failed.\n";
		//abort();
	}
	else 
	{
		cout << "DES Encryption/decryption succeeded.\n";
	}

}