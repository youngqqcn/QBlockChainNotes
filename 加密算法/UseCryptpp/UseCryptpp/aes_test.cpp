#include "stdafx.h"
#include "aes_test.h"

void aes_test_2()
{
	cout << "key length: " << AES::DEFAULT_KEYLENGTH << endl;
	cout << "key length (min): " << AES::MIN_KEYLENGTH << endl;
	cout << "key length (max): " << AES::MAX_KEYLENGTH << endl;
	cout << "block size: " << AES::BLOCKSIZE << endl;

	AutoSeededRandomPool rnd;

	//产生一个随机数的密钥
	SecByteBlock key(0x00, AES::DEFAULT_KEYLENGTH);
	rnd.GenerateBlock(key, key.size());

	//产生一个随机的初始向量
	SecByteBlock iv(AES::BLOCKSIZE);
	rnd.GenerateBlock(iv, iv.size());

	byte plainText[] = "Hello! How are you.";
	size_t messageLen = std::strlen((char*)plainText) + 1;

	//加密字符串
	CFB_Mode<AES>::Encryption cfbEncryption(key, key.size(), iv);
	cfbEncryption.ProcessData(plainText, plainText, messageLen);

	cout << endl << "加密结果(十六进制表示):" << endl;
	//显示加密结果至cout
	StringSource strSource1(plainText, messageLen, true, new HexEncoder(new FileSink(cout)));

	//解密字符串
	CFB_Mode<AES>::Decryption cfbDecryption(key, key.size(), iv);
	cfbDecryption.ProcessData(plainText, plainText, messageLen);

	cout << endl << "解密结果(十六进制表示):" << endl;
	//显示解密结果至cout
	StringSource strSource2(plainText, messageLen, true, new HexEncoder(new FileSink(cout)));
	cout << endl;


}


void  aes_test() {

	unsigned char key[] = { 0x01,0x02,0x03,0x04,0x05,0x06,0x07,0x08,	0x01,0x02, 0x03,0x04,0x05,0x06,0x07,0x08 };//AES::DEFAULT_KEYLENGTH
	unsigned char iv[] = { 0x01,0x02,0x03,0x03,0x03,0x03,0x03,0x03,	0x03,0x03, 0x01,0x02,0x03,0x03,0x03,0x03 };
	int keysize = 16;

	string	message = "Hello World!";
	string	strEncTxt;
	string	strDecTxt;

	//CBC - PADDING
	//AES-CBC Encrypt(ONE_AND_ZEROS_PADDING)
	CBC_Mode<AES>::Encryption  Encryptor1(key, keysize, iv);
	StringSource(message, true, new StreamTransformationFilter(Encryptor1, new StringSink(strEncTxt)) );
	 
	std::cout << "strEncTxt:" << strEncTxt << std::endl;

	//AES-CBC Decrypt
	CBC_Mode<AES>::Decryption Decryptor1(key, keysize, iv);
	StringSource(strEncTxt, true, new StreamTransformationFilter(Decryptor1,new StringSink(strDecTxt)) );
	std::cout << "strDecTxt:" << strDecTxt << std::endl;

	std::cout << " ---------------------------------" << std::endl;
	//CTR - NO_PADDING
	//AES-CTR Encrypt
	strEncTxt = "";
	strDecTxt = "";
	CTR_Mode<AES>::Encryption  Encryptor2(key, keysize, iv);
	StringSource(message, true, new StreamTransformationFilter(Encryptor2,new StringSink(strEncTxt), BlockPaddingSchemeDef::BlockPaddingScheme::NO_PADDING));
	std::cout << "strEncTxt:" << strEncTxt << std::endl;

	//AES-CTR Decrypt
	CTR_Mode<AES>::Decryption Decryptor2(key, keysize, iv);
	StringSource(strEncTxt, true, new StreamTransformationFilter(Decryptor2, new StringSink(strDecTxt), BlockPaddingSchemeDef::BlockPaddingScheme::NO_PADDING));
	std::cout << "strDecTxt:" << strDecTxt << std::endl;

}