
// UsePython3LibDlg.h: 头文件
//

#pragma once


#define WM_GENADDR (WM_USER+100)

// CUsePython3LibDlg 对话框
class CUsePython3LibDlg : public CDialogEx
{
// 构造
public:
	CUsePython3LibDlg(CWnd* pParent = nullptr);	// 标准构造函数

// 对话框数据
#ifdef AFX_DESIGN_TIME
	enum { IDD = IDD_USEPYTHON3LIB_DIALOG };
#endif

	protected:
	virtual void DoDataExchange(CDataExchange* pDX);	// DDX/DDV 支持


// 实现
protected:
	HICON m_hIcon;

	// 生成的消息映射函数
	virtual BOOL OnInitDialog();
	afx_msg void OnSysCommand(UINT nID, LPARAM lParam);
	afx_msg void OnPaint();
	afx_msg HCURSOR OnQueryDragIcon();
	afx_msg LRESULT OnGenAddr(WPARAM wParam, LPARAM lParam);
	DECLARE_MESSAGE_MAP()
public:
	afx_msg void OnBnClickedOk();


private:

	CString m_cstrMasterAddr = _T("");
	CString  m_cstrPrivViewKey = _T("");
	CString  m_cstrAddrCount = _T("");
	UINT m_uAddrCount = 0;

};
