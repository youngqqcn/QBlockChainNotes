#include<iostream>
#include"mem.h"

using std::cout;
using std::endl;

int main()
{
	MemCachedClient mc;
	int result = mc.Insert("mem_key","hello yqq!");   
	string get_value =  mc.Get("mem_key");

	cout << "get_value: " << get_value << endl;
	return 1;
};

