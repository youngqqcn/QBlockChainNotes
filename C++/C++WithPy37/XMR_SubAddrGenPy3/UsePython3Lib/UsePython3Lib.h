
// UsePython3Lib.h: PROJECT_NAME 应用程序的主头文件
//

#pragma once

#ifndef __AFXWIN_H__
	#error "在包含此文件之前包含“stdafx.h”以生成 PCH 文件"
#endif

#include "resource.h"		// 主符号


// CUsePython3LibApp:
// 有关此类的实现，请参阅 UsePython3Lib.cpp
//

class CUsePython3LibApp : public CWinApp
{
public:
	CUsePython3LibApp();

// 重写
public:
	virtual BOOL InitInstance();
	virtual int ExitInstance(); // return app exit code

// 实现

	DECLARE_MESSAGE_MAP()
};

extern CUsePython3LibApp theApp;
