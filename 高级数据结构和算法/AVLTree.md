



# AVLTree



```cpp
#pragma once

/**
*@time: 2019-10-28 18:43:40
*@author: yqq
*@descriptions: 平衡二叉树
*/

//参考 : https://www.tutorialspoint.com/cplusplus-program-to-implement-avl-tree


#include <iostream>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <string>
#include <algorithm>
#include <vector>
#include <list>
#include <sstream>
#include <map>
#include <boost/algorithm/string.hpp>

using namespace std;



template <typename T> 
struct AVLTree
{
public:

	AVLTree() 
	{
		_m_pRoot = nullptr;
	}

	virtual ~AVLTree() 
	{
		Destroy();
	}

	template <typename CompareableType>
	struct AVLTreeNode
	{
		CompareableType						data;
		AVLTreeNode<CompareableType>		*pLeft;
		AVLTreeNode<CompareableType>		*pRight;
	};


protected:
	AVLTreeNode<T>  *_m_pRoot;


public:
	void Insert(const T &value)
	{
		 _Insert(_m_pRoot, value);
	}

	void Delete(const T &value)
	{
		_Remove(_m_pRoot, value);
	}

	std::string PreOrder()
	{
		std::string strRet = _PreOrder(_m_pRoot);
		if (boost::algorithm::ends_with(strRet, " "))
		{
			boost::algorithm::replace_last(strRet, " ", "");
		}
		return strRet;
	}

	std::string  InOrder()
	{
		std::string strRet = _InOrder(_m_pRoot);
		if (boost::algorithm::ends_with(strRet, " "))
		{
			boost::algorithm::replace_last(strRet, " ", "");
		}
		return strRet;
	}

	std::string  PostOrder()
	{
		std::string strRet = _PostOrder(_m_pRoot);
		if (boost::algorithm::ends_with(strRet, " "))
		{
			boost::algorithm::replace_last(strRet, " ", "");
		}
		return strRet;
	}

	size_t  Height(const AVLTreeNode<T> *pNode)
	{
		if (nullptr == pNode) return 0;
		size_t nRightHeight =  1 + Height(pNode->pRight);
		size_t nLeftHeight = 1 + Height(pNode->pLeft);
		return std::max(nRightHeight, nLeftHeight);
	}


	void Destroy()
	{
		_Destroy(_m_pRoot);
	}


protected:


	std::string  StrFormat(const T &value)
	{
		std::string strRet;
		std::stringstream  ss;
		ss << value << " ";
		strRet += ss.str();
		return strRet;
	}


	std::string _PreOrder(AVLTreeNode<T> *pNode )
	{
		if (nullptr == pNode) return std::string();

		std::string strRet;
		strRet += StrFormat(pNode->data);
		strRet += _PreOrder(pNode->pLeft);
		strRet += _PreOrder(pNode->pRight);
		return strRet;
	}

	std::string  _InOrder(AVLTreeNode<T> *pNode)
	{
		if (nullptr == pNode) return std::string();

		std::string strRet;
		strRet += _InOrder(pNode->pLeft);
		strRet += StrFormat(pNode->data);
		strRet += _InOrder(pNode->pRight);
		return strRet;
	}

	std::string  _PostOrder(AVLTreeNode<T> *pNode)
	{
		if (nullptr == pNode) return std::string();


		std::string strRet;
		strRet += _PostOrder(pNode->pLeft);
		strRet += _PostOrder(pNode->pRight);
		strRet += StrFormat(pNode->data);
		return strRet;
	}


	//后序遍历释放空间
	void _Destroy(AVLTreeNode<T> * pNode) 
	{
		if (nullptr == pNode)
			return;
		_Destroy(pNode->pLeft);
		_Destroy(pNode->pRight);

		delete pNode;
		pNode = nullptr;
	}

	size_t _Difference(AVLTreeNode<T> *pNode)
	{
		return Height(pNode->pLeft) - Height(pNode->pRight);
	}

	void _Insert(AVLTreeNode<T> * &pNode, const T &value)
	{
		if (nullptr == pNode)
		{
			pNode = new AVLTreeNode<T>();
			pNode->data = value;
			pNode->pRight = nullptr;
			pNode->pLeft = nullptr;
			return ;
		}

		if (value > pNode->data)
		{
			_Insert(pNode->pRight, value);

			//进行平衡调整
			_Balance(pNode);
		}
		else
		{
			_Insert(pNode->pLeft, value);

			//进行平衡调整
			_Balance(pNode);
		}
	}



	//LL 型 调整,  单旋转,   右旋

	/*
	单旋转
	LL型   右旋

	  A
	 /
	B           --右旋-->       B
   /                           / \
  X(新插入的)                 X   A


  一般形式(插入X):

             A                                  B
	      /     \                            /     \
	     B       [#]                       [*]      A 
	   /  \      [#]        ----->         [*]    /   \
	 [*]   [$]   [#]                      /     [$]    [#] 
	 [*]   [$]                          [X]     [$]    [#]
	/                                                  [#]
  [X]


  */
	void LL_Adjust(AVLTreeNode<T> * &pNode)
	{
		AVLTreeNode<T> *pTmp = pNode->pLeft;
		pNode->pLeft = pTmp->pRight; //A接管B的右子树
		pTmp->pRight = pNode;

		pNode = pTmp;
	}



	/**
	单旋转

	RR型   左旋

	A
	 \
	  B              --左旋-->        B
	   \                             / \
	    X(新插入的)                 A   X


	一般形式(插入X):

	       A                                 B
	     /   \                            /     \
      [#]     B                          A       [$] 
	  [#]    /  \         --->         /   \     [$]
	  [#]  [*]   [$]                 [#]   [*]      \
		   [*]   [$]                 [#]   [*]      [X]
				   \                 [#]
				   [X]

	*/
	void RR_Adjust(AVLTreeNode<T> * &pNode)
	{
		AVLTreeNode<T> *pTmp = pNode->pRight;
		pNode->pRight = pTmp->pLeft; // A接管B的左子树
		pTmp->pLeft = pNode;
		pNode = pTmp;
	}



	/*
	双旋转

	LR型   先左旋  , 再右旋

	 A                             A
	/                             /
   B              --左旋-->      X            --右旋-->      X
	\                           /                           / \
	 X(新插入)                 B                           B   A


	*/
	void LR_Adjust(AVLTreeNode<T> *  &pNode)
	{
		RR_Adjust(pNode->pLeft);
		LL_Adjust(pNode);
	}



	/*
	双旋转

	RL型    先右旋, 再左旋

	A                           A
	 \                           \
	  B            --右旋-->      X           --左旋-->      X
	 /                             \                        / \
	X(新插入)                       B                      A   B

	*/

	void RL_Adjust(AVLTreeNode<T> * &pNode)
	{
		LL_Adjust(pNode->pRight);
		RR_Adjust(pNode);
	}


	void _Balance(AVLTreeNode<T> * &pNode)
	{
		if (nullptr == pNode) return;

		//求平衡因子(左右子树的高度差)
		int iBalanceFactor = _Difference(pNode);

		// LL型 或 LR型
		if (iBalanceFactor > 1)  
		{
			if (1 == _Difference(pNode->pLeft))
			{
				LL_Adjust(pNode);
			}
			else 
			{
				LR_Adjust(pNode);
			}
		}
		//RR型  或 RL型
		else if(iBalanceFactor < -1) 
		{
			if (-1 == _Difference(pNode->pRight)) 
			{
				//RR
				RR_Adjust(pNode);
			}
			else 
			{
				//RL
				RL_Adjust(pNode);
			}
		}
		//符合平衡条件
		else return;
	}



	//删除元素, 可以参考  BinarySearchTree的 remove方法
	//删除元素后需要进行平衡操作,以保持平衡性质
	void _Remove(AVLTreeNode<T> * &pNode, const T& value)
	{
		if (nullptr == pNode)
		{
			return;
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
				AVLTreeNode<T> *pTmp = pNode->pRight;
				for (; nullptr != pTmp->pLeft; pTmp = pTmp->pLeft) {};

				pNode->data = pTmp->data;
				_Remove(pNode->pRight, pTmp->data);
			}
			else if (nullptr == pNode->pLeft)
			{
				AVLTreeNode<T> *pTmp = pNode;
				pNode = pNode->pRight;
				//*pNode = *(pNode->pRight); //如果函数参数是  指针类型, 而不是指针引用类型, 则需要进行拷贝
				delete pTmp;
			}
			else if (nullptr == pNode->pRight)
			{
				AVLTreeNode<T> *pTmp = pNode;
				pNode = pNode->pLeft;
				*pNode = *(pNode->pLeft);
				delete pTmp;
			}
		}

		//平衡操作
		_Balance(pNode);
	}


};





```





测试用例



```cpp
// AVLTree.cpp : 定义控制台应用程序的入口点。
//


#include "stdafx.h"
#include<iostream>
#include<cstdio>
#include<sstream>
#include<algorithm>
#include <string>



#include <iostream>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <string>
#include <algorithm>
#include <vector>
#include <list>
#include <map>

using namespace std;



#include "AVLTree.hpp"
#include "avl_tree_ref.hpp"

#define BOOST_TEST_MAIN
#include <boost/test/included/unit_test.hpp>




BOOST_AUTO_TEST_SUITE(test)

//
//BOOST_AUTO_TEST_CASE(test_avl_tree)
//{
//	avl_tree avl;
//
//	r = avl.insert(r, 3);
//	r = avl.insert(r, 2);
//	r = avl.insert(r, 1);
//
//
//	avl.inorder(r);
//	std::cout << std::endl;
//}
//


BOOST_AUTO_TEST_CASE(test_AVLTree)
{
	AVLTree<int>  tree;
	tree.Insert(20);
	tree.Insert(13);
	tree.Insert(7); //LL型 
	tree.Insert(17);

	BOOST_REQUIRE_EQUAL(tree.InOrder(), std::string("7 13 17 20"));
	BOOST_REQUIRE_EQUAL(tree.PreOrder(), std::string("13 7 20 17"));
	BOOST_REQUIRE_EQUAL(tree.PostOrder(), std::string("7 17 20 13"));

	tree.Insert(15); //LL型 


	BOOST_REQUIRE_EQUAL(tree.InOrder(), std::string("7 13 15 17 20"));
	BOOST_REQUIRE_EQUAL(tree.PreOrder(), std::string("13 7 17 15 20"));
	BOOST_REQUIRE_EQUAL(tree.PostOrder(), std::string("7 15 20 17 13"));


	tree.Insert(14); //LL型  , 再 RR型

	BOOST_REQUIRE_EQUAL(tree.InOrder(), std::string("7 13 14 15 17 20"));
	BOOST_REQUIRE_EQUAL(tree.PreOrder(), std::string("15 13 7 14 17 20"));
	BOOST_REQUIRE_EQUAL(tree.PostOrder(), std::string("7 14 13 20 17 15"));


	tree.Insert(18); //RL型(17不符合平衡条件)
	BOOST_REQUIRE_EQUAL(tree.InOrder(), std::string("7 13 14 15 17 18 20"));
	BOOST_REQUIRE_EQUAL(tree.PreOrder(), std::string("15 13 7 14 18 17 20"));
	BOOST_REQUIRE_EQUAL(tree.PostOrder(), std::string("7 14 13 17 20 18 15"));


	tree.Insert(4); //不需调整
	tree.Insert(5);  //LR型
	BOOST_REQUIRE_EQUAL(tree.InOrder(), std::string("4 5 7 13 14 15 17 18 20"));
	BOOST_REQUIRE_EQUAL(tree.PreOrder(), std::string("15 13 5 4 7 14 18 17 20"));
	BOOST_REQUIRE_EQUAL(tree.PostOrder(), std::string("4 7 5 14 13 17 20 18 15"));


}


BOOST_AUTO_TEST_CASE(test_AVLTree_Remove)
{
	AVLTree<int>  tree;
	tree.Insert(10);
	tree.Insert(9);
	tree.Insert(11);
	tree.Insert(8);

	BOOST_REQUIRE_EQUAL(tree.InOrder(), std::string("8 9 10 11"));
	BOOST_REQUIRE_EQUAL(tree.PreOrder(), std::string("10 9 8 11"));
	BOOST_REQUIRE_EQUAL(tree.PostOrder(), std::string("8 9 11 10"));

	tree.Delete(10);

	BOOST_REQUIRE_EQUAL(tree.InOrder(), std::string("8 9 11"));
	BOOST_REQUIRE_EQUAL(tree.PreOrder(), std::string("9 8 11"));
	BOOST_REQUIRE_EQUAL(tree.PostOrder(), std::string("8 11 9"));

}




BOOST_AUTO_TEST_SUITE_END()


```

