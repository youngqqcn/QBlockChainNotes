
// UsePython3LibDlg.cpp: 实现文件
//

#include "stdafx.h"
#include "UsePython3Lib.h"
#include "UsePython3LibDlg.h"
#include "afxdialogex.h"

#include <Python.h>
#include <string>
#include <thread>

using namespace std;



#ifdef _DEBUG
#define new DEBUG_NEW
#endif


// 用于应用程序“关于”菜单项的 CAboutDlg 对话框

class CAboutDlg : public CDialogEx
{
public:
	CAboutDlg();

// 对话框数据
#ifdef AFX_DESIGN_TIME
	enum { IDD = IDD_ABOUTBOX };
#endif

	protected:
	virtual void DoDataExchange(CDataExchange* pDX);    // DDX/DDV 支持

// 实现
protected:
	DECLARE_MESSAGE_MAP()
};

CAboutDlg::CAboutDlg() : CDialogEx(IDD_ABOUTBOX)
{
}

void CAboutDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialogEx::DoDataExchange(pDX);
}

BEGIN_MESSAGE_MAP(CAboutDlg, CDialogEx)
END_MESSAGE_MAP()


// CUsePython3LibDlg 对话框



CUsePython3LibDlg::CUsePython3LibDlg(CWnd* pParent /*=nullptr*/)
	: CDialogEx(IDD_USEPYTHON3LIB_DIALOG, pParent)
{
	m_hIcon = AfxGetApp()->LoadIcon(IDR_MAINFRAME);
}

void CUsePython3LibDlg::DoDataExchange(CDataExchange* pDX)
{
	CDialogEx::DoDataExchange(pDX);
}

BEGIN_MESSAGE_MAP(CUsePython3LibDlg, CDialogEx)
	ON_WM_SYSCOMMAND()
	ON_WM_PAINT()
	ON_WM_QUERYDRAGICON()
	ON_BN_CLICKED(IDOK, &CUsePython3LibDlg::OnBnClickedOk)
	//ON_MESSAGE( WM_GENADDR, &CUsePython3LibDlg::OnGenAddr)  //自定义消息
END_MESSAGE_MAP()


// CUsePython3LibDlg 消息处理程序

BOOL CUsePython3LibDlg::OnInitDialog()
{
	CDialogEx::OnInitDialog();

	// 将“关于...”菜单项添加到系统菜单中。

	// IDM_ABOUTBOX 必须在系统命令范围内。
	ASSERT((IDM_ABOUTBOX & 0xFFF0) == IDM_ABOUTBOX);
	ASSERT(IDM_ABOUTBOX < 0xF000);

	CMenu* pSysMenu = GetSystemMenu(FALSE);
	if (pSysMenu != nullptr)
	{
		BOOL bNameValid;
		CString strAboutMenu;
		bNameValid = strAboutMenu.LoadString(IDS_ABOUTBOX);
		ASSERT(bNameValid);
		if (!strAboutMenu.IsEmpty())
		{
			pSysMenu->AppendMenu(MF_SEPARATOR);
			pSysMenu->AppendMenu(MF_STRING, IDM_ABOUTBOX, strAboutMenu);
		}
	}

	// 设置此对话框的图标。  当应用程序主窗口不是对话框时，框架将自动
	//  执行此操作
	SetIcon(m_hIcon, TRUE);			// 设置大图标
	SetIcon(m_hIcon, FALSE);		// 设置小图标

	// TODO: 在此添加额外的初始化代码
	SetWindowText(_T("门罗币(XMR)子地址批量生成小工具 v1.0  2020_03_31 by yqq"));

	return TRUE;  // 除非将焦点设置到控件，否则返回 TRUE
}

void CUsePython3LibDlg::OnSysCommand(UINT nID, LPARAM lParam)
{
	if ((nID & 0xFFF0) == IDM_ABOUTBOX)
	{
		CAboutDlg dlgAbout;
		dlgAbout.DoModal();
	}
	else
	{
		CDialogEx::OnSysCommand(nID, lParam);
	}
}

// 如果向对话框添加最小化按钮，则需要下面的代码
//  来绘制该图标。  对于使用文档/视图模型的 MFC 应用程序，
//  这将由框架自动完成。

void CUsePython3LibDlg::OnPaint()
{
	if (IsIconic())
	{
		CPaintDC dc(this); // 用于绘制的设备上下文

		SendMessage(WM_ICONERASEBKGND, reinterpret_cast<WPARAM>(dc.GetSafeHdc()), 0);

		// 使图标在工作区矩形中居中
		int cxIcon = GetSystemMetrics(SM_CXICON);
		int cyIcon = GetSystemMetrics(SM_CYICON);
		CRect rect;
		GetClientRect(&rect);
		int x = (rect.Width() - cxIcon + 1) / 2;
		int y = (rect.Height() - cyIcon + 1) / 2;

		// 绘制图标
		dc.DrawIcon(x, y, m_hIcon);
	}
	else
	{
		CDialogEx::OnPaint();
	}
}

//当用户拖动最小化窗口时系统调用此函数取得光标
//显示。
HCURSOR CUsePython3LibDlg::OnQueryDragIcon()
{
	return static_cast<HCURSOR>(m_hIcon);
}



LRESULT CUsePython3LibDlg::OnGenAddr(WPARAM wParam, LPARAM lParam)
{
	try
	{
#ifdef _DEBUG
		Py_SetPythonHome(_T("D:\\python37_x64"));
#else
		Py_SetPythonHome(_T("./python37_x64"));
#endif
		Py_Initialize();//使用python之前，要调用Py_Initialize();这个函数进行初始化
		if (!Py_IsInitialized())
		{
			throw std::exception("Py_Initialize() 失败");
		}

		PyObject * pModule = NULL;//声明变量
		PyObject * pFunc_gen_addrs = NULL;// 声明变量
		pModule = PyImport_ImportModule("gen_xmr_addr");//这里是要调用的文件名hello.py
		if (pModule == NULL)
		{
			throw std::exception("获取python文件 gen_xmr_addr.py  失败");
		}

		pFunc_gen_addrs = PyObject_GetAttrString(pModule, "gen_addrs");//这里是要调用的函数名
		if (NULL == pFunc_gen_addrs)
		{
			throw std::exception("获取函数 pFunc_gen_addrs  失败");
		}


		USES_CONVERSION;
		std::string   strMasterAddr = W2A(m_cstrMasterAddr);// "46FpjHMeWLyM5mLhxMqUaz5AuQpobGfHScyQKGMMmnZFcSFTj6zJFNDUGyDR5SVadjAmxgBp8qv1u2vZsEs8Vo1T4uK16xE";
		std::string  strPrivViewKey = W2A(m_cstrPrivViewKey);// "53a60fee1ef4386838cf7d7c5e0b5a252287590fc544a3fda802e92cce3a880a";
		//int nAddrCount = 1000;
		PyObject *args = Py_BuildValue("ssi", strMasterAddr.c_str(), strPrivViewKey.c_str(), m_uAddrCount);


		PyObject* pRet = PyObject_CallObject(pFunc_gen_addrs, args);


		int iRet = 0xffff;
		PyArg_Parse(pRet, "i", &iRet);//转换返回类型


		if (0 != iRet)
		{
			throw std::exception("生成失败!");
		}
		else
		{
			throw std::exception("生成成功! 生成的文件在程序所在目录 , 请查看.");
			//AfxMessageBox(_T("生成成功! 生成的文件在程序所在目录 , 请查看."));
		}
	}
	catch (std::exception &e)
	{
		AfxMessageBox(CString(e.what()) );
	}
	catch (...)
	{
		AfxMessageBox(_T("未知错误"));
	}


	Py_Finalize(); // 与初始化对应

	GetDlgItem(IDC_EDIT_ADDRCOUNT)->EnableWindow(TRUE);
	GetDlgItem(IDC_EDIT_PRIVVIEWKEY)->EnableWindow(TRUE);
	GetDlgItem(IDC_EDIT_MASTERADDR)->EnableWindow(TRUE);
	GetDlgItem(IDOK)->EnableWindow(TRUE);
	GetDlgItem(IDOK)->SetWindowText(_T("开始生成"));

	return NULL;
}

void CUsePython3LibDlg::OnBnClickedOk()
{
	// TODO: 在此添加控件通知处理程序代码
	CString cstrMasterAddr = _T("");
	CString  cstrPrivViewKey = _T("");
	CString  cstrAddrCount = _T("");

	UINT uAddrCount = 0;
	GetDlgItem(IDC_EDIT_ADDRCOUNT)->GetWindowText(cstrAddrCount);
	GetDlgItem(IDC_EDIT_PRIVVIEWKEY)->GetWindowText(cstrPrivViewKey);
	GetDlgItem(IDC_EDIT_MASTERADDR)->GetWindowText(cstrMasterAddr);

	cstrAddrCount.Trim();
	cstrPrivViewKey.Trim();
	cstrMasterAddr.Trim();

	if (64 != cstrPrivViewKey.GetLength())
	{
		AfxMessageBox(_T("Private View Key 格式错误, 请重新输入"));
		return;
	}


	if (95 != cstrMasterAddr.GetLength())
	{
		AfxMessageBox(_T("Master Address 格式错误, 请重新输入"));
		return;
	}

	if (wchar_t('4') != cstrMasterAddr.GetAt(0))
	{
		AfxMessageBox(_T("Master Address 格式错误,必须是 '4' 开头, 请重新输入"));
		return;
	}

	TRY
	{
		//uAddrCount = _atoi64(strAddrCount);
		uAddrCount = (UINT)_ttoi64(cstrAddrCount);
		uAddrCount += 1;  //因为 index从   1 开始
	}
	CATCH(CException, e)
	{
		AfxMessageBox(_T("地址数量格式错误, 请重新输入"));
		return;
	}
	END_CATCH;


	if (uAddrCount > 200000)
	{
		AfxMessageBox(_T("地址数量太大,必须小于20万, 请重新输入"));
		return;
	}

	if (uAddrCount > 10000)
	{
		double nTime = double(uAddrCount) / double(10000)  * 60;
		char buf[100] = { 0 };
		sprintf_s(buf, "%.1f", nTime);
		if (IDCANCEL == AfxMessageBox(_T("大约需要 ") + CString(buf) + _T("秒"), MB_OKCANCEL))
		{
			return;
		}
	}




	m_cstrAddrCount = cstrAddrCount;
	m_cstrMasterAddr = cstrMasterAddr;
	m_cstrPrivViewKey = cstrPrivViewKey;
	m_uAddrCount = uAddrCount;


	GetDlgItem(IDC_EDIT_ADDRCOUNT)->EnableWindow(FALSE);
	GetDlgItem(IDC_EDIT_PRIVVIEWKEY)->EnableWindow(FALSE);
	GetDlgItem(IDC_EDIT_MASTERADDR)->EnableWindow(FALSE);

	GetDlgItem(IDOK)->EnableWindow(FALSE);
	GetDlgItem(IDOK)->SetWindowText(_T("生成中..."));


	//PostMessage(WM_GENADDR, 0, 0); // 主界面仍然有卡死的现象
	//SendMessage(WM_GENADDR, 0, 0); //阻塞

	//开启一个新的线程, 解决主界面 卡死的问题
	std::thread thrd( &CUsePython3LibDlg::OnGenAddr, this, 0, 0);
	thrd.detach();

#if 0
	PyObject * pFunc2 = NULL;// 声明变量
	PyObject * pFunc3 = NULL;// 声明变量
	pFunc1 = PyObject_GetAttrString(pModule, "main2");//这里是要调用的函数名
	PyObject* pRet = PyEval_CallObject(pFunc1, NULL);//调用无参数无返回值的python函数

	int res = 0;
	PyArg_Parse(pRet, "i", &res);//转换返回类型


	////2
	pFunc2 = PyObject_GetAttrString(pModule, "zip_file");//这里是要调用的函数名
	string readpath = R"(C:\Users\admin\Desktop\TestData)";
	string writepath = R"(C:\Users\admin\Desktop\TestData.zip)";
	PyObject* args = Py_BuildValue("ss", readpath.c_str(), writepath.c_str());//给python函数参数赋值

	PyObject_CallObject(pFunc2, args);//调用函数
	//3
	pFunc3 = PyObject_GetAttrString(pModule, "_getValue");//这里是要调用的函数名
	PyObject* args2 = Py_BuildValue("ii", 28, 103);//给python函数参数赋值

	PyObject* pRet = PyObject_CallObject(pFunc3, args2);//调用函数
	int res = 0;
	PyArg_Parse(pRet, "i", &res);//转换返回类型
#endif

	//system("pause");

}
