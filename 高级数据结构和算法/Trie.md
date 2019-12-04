# Trie (前缀树)



- Trie.hpp

```cpp
/**
*@time: 2019-11-15 15:43:13
*@author: yqq
*@descriptions:  实现前缀树
*/


#ifndef __TRIE_H__
#define  __TRIE_H__


#include <map>
#include <string>

template < class CharT = char, class StringT = std::string>
class TrieTree 
{

protected:
	template < class CharT = char>
	struct Node
	{
		bool bIsWord = false;
		std::map< CharT, Node >  subNodes;
	};

	Node<CharT> root;
	size_t  nWordSize = 0;

public:
	TrieTree (){ }
	~TrieTree() { }

public:
	void Insert( const StringT  &strWord )
	{
		Node<CharT>  *pNode = &root;
		for (size_t i = 0; i < strWord.length(); i++)
		{
			CharT chTmp = strWord.at(i);

			auto it = pNode->subNodes.find(chTmp);
			if (pNode->subNodes.end() == it)
			{
				pNode->subNodes.insert( std::make_pair( chTmp, Node<CharT>() ) );
			}
			it = pNode->subNodes.find(chTmp);

			pNode = &it->second;
		}

		if (!pNode->bIsWord)
		{
			pNode->bIsWord = true;
			nWordSize++;
		}
	}



	bool Contains(const StringT &strWord)
	{
		Node<CharT>  *pNode = &root;
		for (size_t i = 0; i < strWord.length(); i++)
		{
			CharT chTmp = strWord.at(i);

			auto it = pNode->subNodes.find(chTmp);
			if (pNode->subNodes.end() == it)
			{
				//pNode->subNodes.insert(std::make_pair(chTmp, Node<>()));
				return false;
			}
			it = pNode->subNodes.find(chTmp);

			pNode = &it->second;
		}

		
		return pNode->bIsWord;
	}


	bool IsPrefix(const StringT &strPrefix)
	{

		Node<CharT>  *pNode = &root;
		for (size_t i = 0; i < strPrefix.length(); i++)
		{
			CharT chTmp = strPrefix.at(i);

			auto it = pNode->subNodes.find(chTmp);
			if (pNode->subNodes.end() == it)
			{
				//pNode->subNodes.insert(std::make_pair(chTmp, Node<>()));
				return false;
			}
			it = pNode->subNodes.find(chTmp);

			pNode = &it->second;
		}

		return true;
	}


	size_t  GetSize()const
	{
		return nWordSize;
	}


 
	
	// 解决 https://leetcode-cn.com/problems/add-and-search-word-data-structure-design/
public:
	bool search(const StringT &strPattern)
	{
		return _match(&root, strPattern, 0 );
	}

protected:
	bool _match(const Node<CharT> *pNode, const StringT &strPattern, size_t  index)
	{
		if (index >= strPattern.length())
			return pNode->bIsWord;

		//CharT chDot = '.';
		//if (std::is_same<CharT, wchar_t >::value) chDot = L'.';
		//else if (std::is_same<CharT, char>::value) chDot = '.';

		CharT  chTmp = strPattern.at(index);
		//if ( chDot == chTmp)
		if ( (CharT)'.' == chTmp)
		{
			for (auto &item : pNode->subNodes)
			{
				if (_match(&item.second, strPattern, index + 1))
					return true;
			}
			return false;
		}
		else
		{
			auto it = pNode->subNodes.find(chTmp);
			if (pNode->subNodes.end() == it) 
				return false;

			return _match(  &it->second , strPattern, index + 1);
		}
	}


	//解决: https://leetcode-cn.com/problems/map-sum-pairs/



};






#endif//__TRIE_H__

```





- Trie.cpp

```cpp

// Trie.cpp : 定义控制台应用程序的入口点。
//


#include "stdafx.h"


/**
*@time: 2019-11-15 16:12:35
*@author: yqq
*@descriptions: 
*/

#include <iostream>
#include <stdio.h>
#include <string.h>
#include <stdlib.h>
#include <string>
#include <algorithm>
#include <vector>
#include <list>
#include <map>


#define BOOST_TEST_MAIN
#include <boost/test/included/unit_test.hpp>

using namespace std;


#include "Trie.hpp"


BOOST_AUTO_TEST_SUITE(test_trie)


BOOST_AUTO_TEST_CASE(test_char_stdstring)
{
	//std::cout << "hello" <<std::endl;

	TrieTree<char, std::string > trieTree;

	trieTree.Insert("hello");
	trieTree.Insert("world");
	trieTree.Insert("good");
	trieTree.Insert("god");
	trieTree.Insert("apple");
	trieTree.Insert("hell");
	trieTree.Insert("he");
	trieTree.Insert("application");
	trieTree.Insert("apply");


	BOOST_REQUIRE_EQUAL(trieTree.GetSize(), 9);
	BOOST_REQUIRE_EQUAL(trieTree.Contains("hell"), true);
	BOOST_REQUIRE_EQUAL(trieTree.Contains("hel"), false);
	BOOST_REQUIRE_EQUAL(trieTree.IsPrefix("hel"), true);


	BOOST_REQUIRE_EQUAL(trieTree.search("h..l"), true);
	BOOST_REQUIRE_EQUAL(trieTree.search("g.d"), true);
	BOOST_REQUIRE_EQUAL(trieTree.search("a..p.c"), false);
	BOOST_REQUIRE_EQUAL(trieTree.search("...."), true);
	BOOST_REQUIRE_EQUAL(trieTree.search("....."), true);

}


/*

	            ( ---------------root node----------------)
              /                |            \              \
	      [a]	              [g]	          [h]          [w]  
	    /                      |              /             |
      [p]                     [o]           [e]            [o]
       |                      /  \           |              |
      [p]                   [o]  [d]        [l]            [r]
       |                     |               |              |
      [l]                   [d]             [l]            [l]
    /  |  \                                  |              |
  [e] [i]   [y]                             [o]            [d]
       |
	   [c]
	   |
	   [a]
	   |
	   [t]
	   |
	   [i]
	   |
	   [o]
	   |
	   [n]

*/


BOOST_AUTO_TEST_CASE(test_wchart_stdwstring)
{
	//std::cout << "hello" <<std::endl;

	TrieTree<wchar_t, std::wstring > trieTree;

	trieTree.Insert(L"hello");
	trieTree.Insert(L"world");
	trieTree.Insert(L"good");
	trieTree.Insert(L"god");
	trieTree.Insert(L"apple");
	trieTree.Insert(L"hell");
	trieTree.Insert(L"he");
	trieTree.Insert(L"application");
	trieTree.Insert(L"apply");


	BOOST_REQUIRE_EQUAL(trieTree.GetSize(), 9);
	BOOST_REQUIRE_EQUAL( trieTree.Contains( L"hell" ) , true );
	BOOST_REQUIRE_EQUAL(trieTree.Contains(L"hel"), false );
	BOOST_REQUIRE_EQUAL(trieTree.IsPrefix(L"hel"), true);


	BOOST_REQUIRE_EQUAL(trieTree.search(L"h..l"), true);
	BOOST_REQUIRE_EQUAL(trieTree.search(L"g.d"), true);
	BOOST_REQUIRE_EQUAL(trieTree.search(L"a..p.c"), false);
	BOOST_REQUIRE_EQUAL(trieTree.search(L"...."), true);
	BOOST_REQUIRE_EQUAL(trieTree.search(L"....."), true);



}



BOOST_AUTO_TEST_CASE(test_wchart_stdwstring_for_chinese)
{

	TrieTree<wchar_t, std::wstring > trieTree;

	trieTree.Insert(L"中国梦");
	trieTree.Insert(L"中华人民共和国");
	trieTree.Insert(L"万里长城");
	trieTree.Insert(L"北京天安门");
	trieTree.Insert(L"中华第一关");
	trieTree.Insert(L"北京欢迎您");
	trieTree.Insert(L"北京天津路");


	BOOST_REQUIRE_EQUAL( trieTree.GetSize(),  7 );
	BOOST_REQUIRE_EQUAL(trieTree.Contains(L"中国"), false );
	BOOST_REQUIRE_EQUAL(trieTree.Contains(L"中国梦"), true );
	BOOST_REQUIRE_EQUAL(trieTree.IsPrefix(L"中国"), true);

}



BOOST_AUTO_TEST_CASE(test_match_pattern)
{
	TrieTree<wchar_t, std::wstring > trieTree;

	trieTree.Insert(L"中国梦");
	trieTree.Insert(L"中华人民共和国");
	trieTree.Insert(L"万里长城");
	trieTree.Insert(L"北京天安门");



	BOOST_REQUIRE_EQUAL(trieTree.search(L"中.梦"), true );
	BOOST_REQUIRE_EQUAL(trieTree.search(L"中.梦."), false);
	BOOST_REQUIRE_EQUAL(trieTree.search(L"...."), true);
	BOOST_REQUIRE_EQUAL(trieTree.search(L"....."), true);
	BOOST_REQUIRE_EQUAL(trieTree.search(L"......"), false);
	BOOST_REQUIRE_EQUAL(trieTree.search(L"......."), true);
	BOOST_REQUIRE_EQUAL(trieTree.search(L"中......"), true);



}

BOOST_AUTO_TEST_SUITE_END()

```

