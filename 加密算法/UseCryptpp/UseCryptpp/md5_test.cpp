#include "stdafx.h"
#include "md5_test.h"
#pragma comment(lib, "cryptlib.lib") 
using namespace CryptoPP;
using namespace std;


void MD5_test() {

	byte message[] = "HelloWorld!";
	byte mres[16];//MD5 128 bits=16bytes

	Weak::MD5 md5;
	md5.Update(message, 11);//strlen=11
	md5.Final(mres);

	for (int i = 0; i < 16; i++)
		printf("%02X", mres[i]);

	printf("\n");

}
