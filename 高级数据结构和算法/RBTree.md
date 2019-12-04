



# RBTree



```cpp
#pragma once



#include <iostream>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <string>
#include <algorithm>
#include <vector>
#include <list>
#include <map>
#include <fstream>
#include <filesystem>

#include <boost/format.hpp>
#include <boost/algorithm/string.hpp>
#include <boost/filesystem.hpp>


using namespace std;

template <typename T>
struct MyRBTree
{
protected:

	enum RBColor{RED, BLACK};

	template <typename NodeDataType>  //必须声明模板
	struct TreeNode
	{
		NodeDataType	data;
		TreeNode		*pRight;
		TreeNode		*pLeft;
		TreeNode		*pParent;

		RBColor			color;
	};

protected:
	TreeNode<T>		*pRoot;
	size_t			nSize;




public:
	MyRBTree()
	{
		pRoot = nullptr;
		nSize = 0;
	}

	virtual ~MyRBTree()
	{
		//后续遍历(先释放子节点, 最后),释放空间
		if (nullptr != pRoot)
		{
			Destroy();
		}

	}

public:
	//插入
	void Insert(const T&  value)
	{
		_Insert(pRoot, value);
		pRoot->color = RBColor::BLACK;
	}


	//删除
	void Delete(const T& value)
	{
		_Remove(pRoot, value);
	}

	//查找 
	bool Find(const T& value)
	{
		return   (nullptr == _Find(pRoot, value)) ? false : true;
	}

	//前序遍历
	std::string Preorder()
	{
		std::string strOrder;
		_Preorder(pRoot, strOrder);
		return strOrder;
	}

	//中序遍历
	std::string  Inorder()
	{
		std::string strOrder;
		_Inorder(pRoot, strOrder);
		return strOrder;
	}

	//后序遍历
	std::string  Postorder()
	{
		std::string strOrder;
		_Postorder(pRoot, strOrder);
		return strOrder;
	}


	//销毁
	void Destroy()
	{
		_Destroy(pRoot);
		pRoot = nullptr;
	}


protected:


	void _Destroy(TreeNode<T> *pNode)
	{
		if (nullptr == pNode)
			return;

		_Destroy(pNode->pLeft);
		_Destroy(pNode->pRight);

		delete pNode;
		pNode = nullptr;
	}



	//这里是指针的引用
	//如果用的是指针, 再改变左右子树时, 需要解引用拷贝
	//void _Remove(TreeNode<T> * &pNode, const T& value)
	//{
	//	if (nullptr == pNode)
	//	{
	//		return;
	//	}
	//	else if (pNode->data < value)
	//	{
	//		_Remove(pNode->pRight, value);
	//	}
	//	else if (pNode->data > value)
	//	{
	//		_Remove(pNode->pLeft, value);
	//	}
	//	else // 找到了
	//	{
	//		//如果有左右子树
	//		if (nullptr != pNode->pLeft && nullptr != pNode->pRight)
	//		{
	//			//找到右子树中最小的节点
	//			TreeNode<T> *pTmp = pNode->pRight;
	//			for (; nullptr != pTmp->pLeft; pTmp = pTmp->pLeft) {};

	//			pNode->data = pTmp->data;
	//			_Remove(pNode->pRight, pTmp->data);
	//		}
	//		else if (nullptr == pNode->pLeft)
	//		{
	//			TreeNode<T> *pTmp = pNode;
	//			pNode = pNode->pRight;
	//			//*pNode = *(pNode->pRight); //如果函数参数是  指针类型, 而不是指针引用类型, 则需要进行拷贝

	//			delete pTmp;
	//			return;
	//		}
	//		else if (nullptr == pNode->pRight)
	//		{
	//			TreeNode<T> *pTmp = pNode;
	//			pNode = pNode->pLeft;
	//			*pNode = *(pNode->pLeft);
	//			delete pTmp;
	//			return;
	//		}

	//	}
	//}



	TreeNode<T>* _Find(TreeNode<T> *pNode, const T& value)
	{
		if (nullptr == pNode)
			return nullptr;

		if (value == pNode->data)
			return pNode;
		else if (value > pNode->data)
			return _Find(pNode->pRight, value);
		else
			return _Find(pNode->pLeft, value);
	}

	void _Insert(TreeNode<T> * &pNode, const T& value)
	{
		//递归终止条件

		//空树
		if (nullptr == pNode)
		{
			pNode = new TreeNode<T>();
			pNode->data = value;
			pNode->pLeft = nullptr;
			pNode->pRight = nullptr;
			pNode->color = RBColor::RED;
			return;
		}

		//开始递归
		if (pNode->data < value)
		{
			_Insert(pNode->pRight, value);
		}
		else
		{
			_Insert(pNode->pLeft, value);
		}


		//插入完成后, 进行调整,以符合红黑树性质

		if ( _IsRed(pNode->pRight) && !_IsRed(pNode->pLeft) )
		{
			_LeftRotate(pNode);
		}

		if (_IsRed(pNode->pLeft) && _IsRed(pNode->pLeft->pLeft))
		{
			_RightRotate(pNode);
		}

		if (_IsRed(pNode->pLeft) && _IsRed(pNode->pRight))
		{
			_FlipColor(pNode);
		}
	}

	//左旋
	void _LeftRotate(TreeNode<T> * &pNode)
	{
		//旋转
		TreeNode<T> *pTmp = pNode->pRight;
		pNode->pRight = pTmp->pLeft;
		pTmp->pLeft = pNode;

		//颜色调整
		pTmp->color = pNode->color;
		pNode->color = RBColor::RED;

		pNode = pTmp;
	}

	//右旋
	void _RightRotate(TreeNode<T> * &pNode)
	{
		//旋转
		TreeNode<T> *pTmp = pNode->pLeft;
		pNode->pLeft = pTmp->pRight;
		pTmp->pRight = pNode;

		//颜色调整 
		pTmp->color = pNode->color;
		pNode->color = RBColor::RED;

		pNode = pTmp;
	}

	bool _IsRed(const TreeNode<T> * const pNode)
	{
		if (nullptr == pNode) return false;
		return  RBColor::RED == pNode->color;
	}


	/*
	 颜色翻转
	*/
#define REVERSE_COLOR(color) ((RBColor::RED == color) ? (RBColor::BLACK) : (RBColor::RED))
	void _FlipColor(TreeNode<T> * &pNode)
	{
		pNode->color = REVERSE_COLOR(pNode->color);
		pNode->pRight->color = REVERSE_COLOR(pNode->pRight->color);
		pNode->pLeft->color = REVERSE_COLOR(pNode->pLeft->color);
	}
#undef REVERSE_COLOR




	void _Preorder(const TreeNode<T>* const pNode, std::string &strOrder)
	{
		//递归终止条件
		if (nullptr == pNode)
			return;

		if (!strOrder.empty()) strOrder += " ";
		strOrder += boost::str(boost::format("%d") % pNode->data);

		_Preorder(pNode->pLeft, strOrder);
		_Preorder(pNode->pRight, strOrder);
	}

	void _Inorder(const TreeNode<T>* const pNode, std::string &strOrder)
	{
		//递归终止条件
		if (nullptr == pNode)
			return;

		_Inorder(pNode->pLeft, strOrder);

		if (!strOrder.empty()) strOrder += " ";
		strOrder += boost::str(boost::format("%d") % pNode->data);

		_Inorder(pNode->pRight, strOrder);
	}

	void _Postorder(const TreeNode<T>* const pNode, std::string &strOrder)
	{
		//递归终止条件
		if (nullptr == pNode)
			return;

		_Postorder(pNode->pLeft, strOrder);
		_Postorder(pNode->pRight, strOrder);

		if (!strOrder.empty()) strOrder += " ";
		strOrder += boost::str(boost::format("%d") % pNode->data);
	}



public:
	void OutputGraph(const std::string &strDotFilePath, const char *pszDotExePath = nullptr)
	{
		std::ofstream  outFile(strDotFilePath, ios::out );
		if (!outFile.is_open())
		{
			std::cout << "open file " << strDotFilePath << "  failed." << std::endl;
			return;
		}

		outFile << "digraph G {" << endl;

		_OutputGraph(outFile, pRoot);

		outFile << "}" << endl;

		outFile.close();


	}

protected:
	void _OutputGraph(std::ofstream & outFile, const TreeNode<T> * const pNode)
	{
		if (nullptr == pNode)
			return;


		std::string strNodeAttr;
		if (_IsRed(pNode)){
			strNodeAttr = "shape=record,  style=filled, fillcolor=red, fontcolor=black";
		}
		else{
			strNodeAttr = "shape=record, color=black, style=filled, fillcolor=\"#B5B5B5\"";
		}

		outFile << pNode->data << "[label = \"<f0> | <f1> " << pNode->data << " | <f2> \"," << strNodeAttr << " ];" << endl;

		if (nullptr != pNode->pLeft)
		{
			_OutputGraph(outFile, pNode->pLeft);
			outFile << pNode->data << ":f0:sw->" << pNode->pLeft->data << ":f1;" << endl;
		}
		
		if(nullptr != pNode->pRight)
		{
			_OutputGraph(outFile, pNode->pRight);
			outFile << pNode->data << ":f2:se->" << pNode->pRight->data << ":f1;" << endl;
		}
	}


};




```





测试用例



```cpp
// RBTree.cpp : 定义控制台应用程序的入口点。
//

#include "stdafx.h"

/**
*@time: 2019-10-29 15:13:26
*@author: yqq
*@descriptions: 
*/

#define  BOOST_AUTO_TEST_MAIN
#include <boost/test/included/unit_test.hpp>


#include <iostream>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <string>
#include <algorithm>
#include <vector>
#include <list>
#include <map>
#include <iostream>


#include "RBTree.hpp"
#include "MyRBTree.hpp"
using namespace std;
//
//int main()
//{
//	int a[] = { 10, 40, 30, 60, 90, 70, 20, 50, 80 };
//	int check_insert = 0;    // "插入"动作的检测开关(0，关闭；1，打开)
//	int check_remove = 0;    // "删除"动作的检测开关(0，关闭；1，打开)
//	int i;
//	int ilen = (sizeof(a)) / (sizeof(a[0]));
//	RBTree<int>* tree = new RBTree<int>();
//
//	cout << "== 原始数据: ";
//	for (i = 0; i<ilen; i++)
//		cout << a[i] << " ";
//	cout << endl;
//
//	for (i = 0; i<ilen; i++)
//	{
//		tree->insert(a[i]);
//		// 设置check_insert=1,测试"添加函数"
//		if (check_insert)
//		{
//			cout << "== 添加节点: " << a[i] << endl;
//			cout << "== 树的详细信息: " << endl;
//			tree->print();
//			cout << endl;
//		}
//
//	}
//
//	cout << "== 前序遍历: ";
//	tree->preOrder();
//
//	cout << "\n== 中序遍历: ";
//	tree->inOrder();
//
//	cout << "\n== 后序遍历: ";
//	tree->postOrder();
//	cout << endl;
//
//	cout << "== 最小值: " << tree->minimum() << endl;
//	cout << "== 最大值: " << tree->maximum() << endl;
//	cout << "== 树的详细信息: " << endl;
//	tree->print();
//
//	// 设置check_remove=1,测试"删除函数"
//	if (check_remove)
//	{
//		for (i = 0; i<ilen; i++)
//		{
//			tree->remove(a[i]);
//
//			cout << "== 删除节点: " << a[i] << endl;
//			cout << "== 树的详细信息: " << endl;
//			tree->print();
//			cout << endl;
//		}
//	}
//
//	// 销毁红黑树
//	tree->destroy();
//
//	return 0;
//}


BOOST_AUTO_TEST_SUITE(test_rb_tree)
//
//BOOST_AUTO_TEST_CASE(test_rbtree)
//{
//	MyRBTree<int> rbt;
//	rbt.Insert(9);
//	rbt.Insert(4);
//	rbt.Insert(1);
//}
//
//

//
//BOOST_AUTO_TEST_CASE(test_rbtree_2)
//{
//	MyRBTree<double> rbt;
//	rbt.Insert(10);
//	rbt.Insert(7);
//	rbt.Insert(8);
//	rbt.Insert(15);
//	rbt.Insert(5);
//	rbt.Insert(6);
//	rbt.Insert(11);
//	rbt.Insert(13);
//	rbt.Insert(12);
//	rbt.Insert(19);
//
//
//	std::cout << rbt.Inorder() << std::endl;
//
//	//生成dot文件
//	rbt.OutputGraph("test.dot", "D:\\Program Files (x86)\\Graphviz2.38\\bin");
//
//	//将dot文件转为 png文件
//	const char *pszCmd = "\"D:\\Program Files (x86)\\Graphviz2.38\\bin\\dot.exe\"   -Tpng -o test.png  test.dot   ";
//	std::cout << pszCmd << std::endl;
//	system(pszCmd);
//
//	//打开图片
//	system( "test.png" );
//
//}



#include <time.h>

//
//BOOST_AUTO_TEST_CASE(test_rbtree_3)
//{
//	MyRBTree<double> rbt;
//
//	//srand(time(NULL));
//	srand(1573788896);
//	clock_t timeBegin = clock();
//
//	for (int i = 0; i < 5000000; i++ )
//	{
//		int nRand = rand() % 4000000000;
//		if( !rbt.Find(nRand ))
//			rbt.Insert( nRand );
//	}
//	clock_t timeEnd = clock();
//
//	//std::cout << rbt.Inorder() << std::endl;
//
//	std::cout << "共耗时: " << timeEnd - timeBegin << endl;
//
//
//	//生成dot文件
//	rbt.OutputGraph("test_rbtree_random_insert.dot", "D:\\Program Files (x86)\\Graphviz2.38\\bin");
//
//	//将dot文件转为 png文件
//	const char *pszCmd = "\"D:\\Program Files (x86)\\Graphviz2.38\\bin\\dot.exe\"   -Tsvg -o test_rbtree_random_insert.svg test_rbtree_random_insert.dot   ";
//	std::cout << pszCmd << std::endl;
//	system(pszCmd);
//
//	//打开图片
//	//system("test2.svg");
//
//}



#include <ctime>
BOOST_AUTO_TEST_CASE(test_random_2)
{
	clock_t timeBegin = clock();
	const int nMaxtimes = 10;
	MyRBTree<double> tst;

	for (int nTesttimes = 0; nTesttimes < nMaxtimes; nTesttimes++)
	{
		srand(1573788896 + nTesttimes * 100);

		for (int i = 0; i < 5000000; i++)
		{
			int nRand = rand() % 4000000000;
			if (!tst.Find(nRand))
				tst.Insert(nRand);
		}
	}
	clock_t timeEnd = clock();
	std::cout << "共耗时: " << (double)(timeEnd - timeBegin) / nMaxtimes << endl;  //3216



	timeBegin = clock();
	for (int nTesttimes = 0; nTesttimes < nMaxtimes * 100000; nTesttimes++)
	{
		srand(1573788896 + nTesttimes * 200);
		int nRand = rand() % 4000000000;
		if (tst.Find(nRand))
		{
			//std::cout << "found :" << nRand << std::endl;
		}

	}
	timeEnd = clock();
	std::cout << "共耗时: " << timeEnd - timeBegin  << endl;  //

	/*
	共耗时: 3218.8
	共耗时: 716
	*/

}



BOOST_AUTO_TEST_SUITE_END()



```

