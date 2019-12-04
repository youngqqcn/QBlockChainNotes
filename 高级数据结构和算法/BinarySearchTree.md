# BinarySerachTree



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


#include <boost/format.hpp>


using namespace std;

template <typename T>
struct BinarySearchTree
{
protected:
	template <typename NodeDataType>  //必须声明模板
	struct TreeNode
	{
		NodeDataType	data;
		TreeNode		*pRight;
		TreeNode		*pLeft;
	};

protected:
	TreeNode<T>		*pRoot;
	size_t			nSize;




public:
	BinarySearchTree()
	{
		pRoot = nullptr;
		nSize = 0;
	}

	virtual ~BinarySearchTree()
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
	void _Remove(TreeNode<T> * &pNode, const T& value)
	{
		if (nullptr == pNode) 
		{
			return ;
		}
		else if (pNode->data < value) 
		{
			 _Remove(pNode->pRight, value);
		}
		else if (pNode->data > value)  
		{
			_Remove(pNode->pLeft, value);
		}
		else // 找到了
		{
			//如果有左右子树
			if (nullptr != pNode->pLeft && nullptr != pNode->pRight)
			{
				//找到右子树中最小的节点
				TreeNode<T> *pTmp = pNode->pRight;
				for (; nullptr != pTmp->pLeft; pTmp = pTmp->pLeft) {};
				
				pNode->data = pTmp->data;
				_Remove(pNode->pRight,  pTmp->data);
			}
			else if (nullptr == pNode->pLeft)
			{
				TreeNode<T> *pTmp = pNode;
				pNode = pNode->pRight;
				//*pNode = *(pNode->pRight); //如果函数参数是  指针类型, 而不是指针引用类型, 则需要进行拷贝

				delete pTmp;
				return;
			}
			else if (nullptr == pNode->pRight)
			{
				TreeNode<T> *pTmp = pNode;
				pNode = pNode->pLeft;
				*pNode = *(pNode->pLeft);
				delete pTmp;
				return ;
			}

		}
	}



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
	}


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
		std::ofstream  outFile(strDotFilePath, ios::out);
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
		strNodeAttr = "shape=record,  fillcolor=red, fontcolor=black";

		/*if (_IsRed(pNode)) {
			strNodeAttr = "shape=record,  style=filled, fillcolor=red, fontcolor=black";
		}
		else {
			strNodeAttr = "shape=record, color=black, style=filled, fillcolor=\"#B5B5B5\"";
		}*/

		outFile << pNode->data << "[label = \"<f0> | <f1> " << pNode->data << " | <f2> \"," << strNodeAttr << " ];" << endl;

		if (nullptr != pNode->pLeft)
		{
			_OutputGraph(outFile, pNode->pLeft);
			outFile << pNode->data << ":f0:sw->" << pNode->pLeft->data << ":f1;" << endl;
		}

		if (nullptr != pNode->pRight)
		{
			_OutputGraph(outFile, pNode->pRight);
			outFile << pNode->data << ":f2:se->" << pNode->pRight->data << ":f1;" << endl;
		}
	}


};



```





测试用例



```cpp
// BinarySearchTree.cpp : 定义控制台应用程序的入口点。
//

#define BOOST_TEST_MAIN
//#define BOOST_TEST_MODULE example
#include <boost/test/included/unit_test.hpp>
#include <iostream>

#include "stdafx.h"


#include <iostream>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <string>
#include <algorithm>
#include <vector>
#include <list>
#include <map>

#include "BinarySearchTree.hpp"

using namespace std;



BOOST_AUTO_TEST_SUITE(test1)
//
//BOOST_AUTO_TEST_CASE(test_insert) {
//	BinarySearchTree<int> bst;
//	bst.Insert(6);
//	bst.Insert(2);
//	bst.Insert(8);
//	bst.Insert(1);
//	bst.Insert(5);
//	bst.Insert(3);
//	bst.Insert(4);
//
//
//	std::string strPreOrder = bst.Preorder();
//	std::cout << "preorder: " << strPreOrder << std::endl;
//	BOOST_CHECK_EQUAL(strPreOrder , std::string("6 2 1 5 3 4 8"));
//
//
//	std::string strPostOrder = bst.Postorder();
//	std::cout << "postorder : " << strPostOrder << std::endl;
//	BOOST_CHECK_EQUAL( strPostOrder, std::string("1 4 3 5 2 8 6"));
//
//
//
//	std::string strInOrder = bst.Inorder();
//	std::cout << strInOrder << std::endl;
//	BOOST_CHECK_EQUAL(strInOrder , std::string("1 2 3 4 5 6 8"));
//
//	bst.Delete(2);
//
//	std::string strInOrder_AfterDelete = bst.Inorder();
//	std::cout <<  strInOrder_AfterDelete << std::endl;
//	BOOST_CHECK_EQUAL(strInOrder_AfterDelete, std::string("1 3 4 5 6 8"));
//
//
//	bst.Insert(7);
//	bst.Insert(11);
//	bst.Insert(10);
//	bst.Insert(13);
//
//	strInOrder = bst.Inorder();
//	std::cout << strInOrder << std::endl;
//	BOOST_CHECK_EQUAL(strInOrder, std::string("1 3 4 5 6 7 8 10 11 13"));
//
//
//	bst.Delete(8);
//
//	strInOrder = bst.Inorder();
//	std::cout << strInOrder << std::endl;
//	BOOST_CHECK_EQUAL(strInOrder, std::string("1 3 4 5 6 7 10 11 13"));
//}
//


//
//#include <ctime>
//BOOST_AUTO_TEST_CASE(test_random) 
//{
//
//	BinarySearchTree<int> bst;
//
//	srand(1573788896);
//
//	clock_t timeBegin = clock();
//	for (int i = 0; i < 5000000; i++)
//	{
//		int nRand = rand() % 4000000000;
//		if (!bst.Find(nRand))
//			bst.Insert(nRand);
//	}
//	clock_t timeEnd = clock();
//
//
//	//std::cout << bst.Inorder() << std::endl;
//
//	std::cout << "共耗时: " << timeEnd - timeBegin << endl;
//
//
//	//生成dot文件
//	bst.OutputGraph("test_binarysearchtree.dot", "D:\\Program Files (x86)\\Graphviz2.38\\bin");
//
//	//将dot文件转为 png文件
//	const char *pszCmd = "\"D:\\Program Files (x86)\\Graphviz2.38\\bin\\dot.exe\"   -Tsvg -o test_binarysearchtree.svg test_binarysearchtree.dot   ";
//	std::cout << pszCmd << std::endl;
//	system(pszCmd);
//
//}
//


#include <ctime>
BOOST_AUTO_TEST_CASE(test_random_2)
{
	clock_t timeBegin = clock();
	const int nMaxtimes = 10;
	BinarySearchTree<int> tst;
	for (int nTesttimes = 0; nTesttimes < 10; nTesttimes++)
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
	std::cout << "共耗时: " << (double)(timeEnd - timeBegin ) / 10.0<< endl;  //3828.2


	timeBegin = clock();
	for (int nTesttimes = 0; nTesttimes < nMaxtimes * 1000000; nTesttimes++)
	{
		srand(1573788896 + nTesttimes * 200);
		int nRand = rand() % 4000000000;
		if (tst.Find(nRand))
		{
			//std::cout << "found :" << nRand << std::endl;
		}

	}
	timeEnd = clock();
	std::cout << "共耗时: " << timeEnd - timeBegin << endl;  //


	/*
	共耗时: 3981.3
	共耗时: 8727
	*/
}


BOOST_AUTO_TEST_SUITE_END()



```

