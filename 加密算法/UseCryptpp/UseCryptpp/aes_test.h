#pragma once
//For AES encrypt
#include "default.h" 
#include "cryptlib.h"
#include "filters.h"
#include "bench.h"
#include "osrng.h"
#include "hex.h"
#include "modes.h"
#include "files.h"

using namespace CryptoPP;
#pragma comment(lib, "cryptlib.lib") 

using namespace std;


void  aes_test();
void aes_test_2();