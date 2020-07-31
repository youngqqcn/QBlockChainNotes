## 图

图的描述方式:

- 邻接矩阵
- 邻接链表



### 邻接矩阵实现

```cpp
#pragma once
#include "graph.h"
#include <vector>
#include <iostream>
#include <iomanip>
#include <queue>
#include <exception>
//#include <string>
#define  NPOS  -1


template <typename V, typename E>
class AdjenctMatrix : public GraphBase<V, E>
{
private:
	std::vector<V>  m_vctVertexes;
	std::vector<std::vector<E>> m_matrix;

public:
	AdjenctMatrix(int nSize, bool isWeight = true, bool isDirected = true);

	virtual ~AdjenctMatrix() {};

	bool InsertVertex(const V& vertex);
	bool InsertEdge(const V& vertex1, const V& vertex2, const E& weight);

	void ShowMatrix();

	//bool RemoveEdge(const V& vertex1, const V& vertex2);
	//bool RemoveVertex(const V& vertex);

	int GetVertexPosition(const V& vertex);

	V GetVertexValueByPos(int nPos) //根据顶点在顶点表中的位置(下标) 来获取顶点的值
	{
		if (!(0 <= nPos && nPos < this->m_vctVertexes.size()))
		{
			throw std::runtime_error("invalid pos");
		}
		return this->m_vctVertexes[nPos];
	}


	void DFSTraverse(); //深度优先遍历
	void BFSTraverse(); //广度优先遍历


	int FristAdjenctVertex(int i); //获取顶点i 的第一个邻接顶点
	int NextAdjenctVertex(int i, int n); //返回 i 的邻接顶点 n 的下一个邻接顶点

	std::vector<std::vector<E>>& GetMatrix() { return this->m_matrix; };

	E GetWeight(int v1, int v2); //根据顶点在顶点表中的位置, 获取边的权重


protected:
	void DFS(int n, std::vector<bool> &vctVisited);
};


template <typename V, typename E>
 AdjenctMatrix<V, E>::AdjenctMatrix(int nSize, bool isWeight  , bool isDirected )
{
	this->m_nMaxVertexesCount = nSize;
	this->m_nVertexesCount = 0;
	this->m_nEdgesCount = 0;
	this->m_fDirected = isDirected;
	this->m_fWeight = isWeight;
	this->m_vctVertexes.resize(this->m_nMaxVertexesCount);
	this->m_matrix.resize(this->m_nMaxVertexesCount);
	for (auto &it : this->m_matrix)
	{
		it.resize(this->m_nMaxVertexesCount);
	}

	for (auto &v : this->m_matrix)
	{
		for (auto &vv : v)
		{
			vv = MAGIC_MAX_WEIGHT;
		}
	}


}

template <typename V, typename E>
int AdjenctMatrix<V, E>::GetVertexPosition(const V& vertex)
{
	for (size_t i = 0; i < this->m_nMaxVertexesCount; i++)
	{
		if (vertex == this->m_vctVertexes[i])
		{
			return i;
		}
	}
	return NPOS;
}

template <typename V, typename E>
bool AdjenctMatrix<V, E>::InsertVertex(const V& vertex)
{
	if (this->m_nVertexesCount == this->m_nMaxVertexesCount)
	{
		std::cerr<< "size overflow" << std::endl;
		return false;
	}

	if (NPOS != GetVertexPosition(vertex))
	{
		std::cerr<< "vertex " << vertex << "already existed" << std::endl;
		return false;
	}

	this->m_vctVertexes[this->m_nVertexesCount++] = vertex; //插入

	return true;
}



template< typename V, typename E>
bool AdjenctMatrix<V, E>::InsertEdge(const V& vertex1, const V& vertex2, const E& weight)
{
	int nV1Pos = GetVertexPosition(vertex1);
	int nV2Pos = GetVertexPosition(vertex2);
	if (NPOS == nV1Pos)
	{
		std::cerr << "vertex1  not exist" << std::endl;
		return false;
	}

	if (NPOS == nV2Pos)
	{
		std::cerr << "vertex2  not exist" << std::endl;
		return false;
	}

	if (!(this->MAX_WEIGHT == m_matrix[nV1Pos][nV2Pos] || 0 == m_matrix[nV1Pos][nV2Pos]))
	{
		std::cerr << "edge: " << vertex1 << " , " << vertex2 << "already existed" << std::endl;
		return false;
	}

	if (this->m_fDirected){ //有向图
		m_matrix[nV1Pos][nV2Pos] = weight;
	}else { //无向图
		m_matrix[nV1Pos][nV2Pos] = weight;
		m_matrix[nV2Pos][nV1Pos] = weight;
	}

	this->m_nEdgesCount ++;
	

	return true;
}



template <typename V, typename E>
void AdjenctMatrix<V, E>::ShowMatrix()
{
	//输出顶点
	for (auto const &it : m_vctVertexes)
	{
		std::cout << it << ", ";
	}
	std::cout << std::endl << "===================" << std::endl;


	//输出邻接矩阵
	for (int i = 0; i < this->m_nVertexesCount; i++)
	{
		for (int j = 0; j < this->m_nVertexesCount; j++)
		{
			if (this->MAX_WEIGHT == m_matrix[i][j]) {
				std::cout << std::setw(7) << "∞";
			}
			else {
				std::cout << std::setw(7) << m_matrix[i][j];
			}
		}
		std::cout << std::endl;
	}

}



template <typename V, typename E> 
void AdjenctMatrix<V, E>::DFSTraverse() //深度优先遍历
{
	std::vector<bool> vctVisited(this->m_nVertexesCount, false);

	for (int i = 0; i < this->m_nVertexesCount; i++)
	{
		if (!vctVisited[i])
		{
			DFS(i, vctVisited);
		}
	}

}

template <typename V, typename E>
void AdjenctMatrix<V, E>::DFS(int i, std::vector<bool> &vctVisited)
{
	vctVisited[i] = true;
	std::cout << this->m_vctVertexes[i] << " , ";

	for (int j = 0; j < this->m_nVertexesCount; j++)
	{
		if (!vctVisited[j] &&
			this->m_matrix[i][j] != 0
			&& this->m_matrix[j][i] != this->MAX_WEIGHT)
		{
			DFS(j, vctVisited);
		}
	}

}


template <typename V, typename E>
void AdjenctMatrix<V, E>::BFSTraverse() //广度优先遍历
{
	std::vector<bool> vctVisited(this->m_nVertexesCount, false);
	std::queue<int> que;

	for (int i = 0; i < this->m_nVertexesCount; i++)
	{
		if(vctVisited[i]) continue;

		que.push(i);
		vctVisited[i] = true;
		std::cout << this->m_vctVertexes[i] << " , ";

		while (!que.empty())
		{
			int parent = que.front();
			que.pop();


			int child = FristAdjenctVertex(parent);

			for (int child = FristAdjenctVertex(parent); 
				child >= 0; 
				child = NextAdjenctVertex(parent, child))
			{
				if (vctVisited[child])
					continue;

				que.push(child);
				std::cout << this->m_vctVertexes[child] << " , ";
				vctVisited[child] = true;
			}
		}
	}

}




template <typename V, typename E>
int AdjenctMatrix<V, E>::NextAdjenctVertex(int i, int n)
{
	if (!(0 <= i && i < this->m_matrix.size()))
	{
		std::cerr << "i is invalid" << std::endl;
		return NPOS;
	}
	if (!(0 <= n && n < this->m_matrix.size()))
	{
		std::cerr << "n is invalid" << std::endl;
		return NPOS;
	}

	for (int col = n + 1; col < this->m_matrix.size() && col < this->m_nVertexesCount; col++)
	{
		if (this->MAX_WEIGHT != this->m_matrix[i][col] && 0 != this->m_matrix[i][col])
		{
			return col;
		}
	}

	return NPOS;
}

template <typename V, typename E>
int AdjenctMatrix<V, E>::FristAdjenctVertex(int i)
{
	if (!(0 <= i && i < this->m_matrix.size()))
	{
		std::cerr << "i is invalid" << std::endl;
		return NPOS;
	}

	for (int col = 0; col < this->m_nVertexesCount; col++)
	{
		if (this->MAX_WEIGHT != this->m_matrix[i][col] && 0 != this->m_matrix[i][col])
		{
			return col;
		}
	}

	return NPOS;
}


template <typename V, typename E>
E AdjenctMatrix<V, E>::GetWeight(int v1, int v2)
{
	if (0 <= v1 && v1 <= this->m_nVertexesCount && 0 <= v2 && v2 <= this->m_nVertexesCount)
	{
		return this->m_matrix[v1][v2];
	}

	std::cerr << "GetWeight error" << std::endl;
	throw std::runtime_error("invalid v1 and v2");
}


```





### 单源最短路径-- Dijskra

```cpp
#pragma once
#include <iostream>
#include <vector>
#include <string>

//************************************
// Method:    Dijkstra
// FullName:  Dijkstra
// Access:    public 
// Returns:   void
// Qualifier:
// Parameter: int nVertexCount  顶点个数
// Parameter: int nBeginVertexIndex   起始顶点(在顶点表中的下标,例如: 第1个下表为0)
// Parameter: std::vector<int> & vctPrevious   记录最短路径的前驱节点 , 获取一条具体路径, 则反向生成即可
//                                   例如: p为 [0, 1, 1, 3, 4]  
//                                     从第1个顶点到第5个顶点的最短路径为  1, 3, 4, 5  , 
//                                      即  5  <== p[5 - 1] 即 4 <<== p[ 4 - 1 ] 即 3  <<== p[3 - 1] 即 1 
// Parameter: std::vector<int> & vctMinPath  记录起始顶点到各个顶点的权重
// Parameter: const std::vector<std::vector<int>> & matrix   邻接矩阵
//************************************
void Dijkstra(int nVertexCount, int nBeginVertexIndex, std::vector<int>&vctPrevious,
	std::vector<int>&vctMinPath, const std::vector<std::vector<int>>& matrix)
{
	int min = MAGIC_MAX_WEIGHT , k = 0;
	std::vector<bool> vctVisitedRows(nVertexCount, false);
	for (int i = 0; i < nVertexCount; i++)
	{
		vctMinPath[i] = matrix[nBeginVertexIndex][i];
	}

	vctMinPath[nBeginVertexIndex] = 0;   //表示v到v路径长度为0
	vctVisitedRows[nBeginVertexIndex] = true;   //表示v到v路径不需要求
	for (int i = 0; i < nVertexCount; ++i)
	{
		// 从  vctMinPath 中获取最小的 , 未访问过的 的 索引
		// 当然也可以使用小根堆来实现
		min = MAGIC_MAX_WEIGHT;
		for (int j = 0; j < nVertexCount; ++j)
		{
			if (!vctVisitedRows[j] && 0 != vctMinPath[j]  && vctMinPath[j] < min)
			{
				k = j;
				min = vctMinPath[j];
			}
		}


		vctVisitedRows[k] = true;   
		for (int w = 0; w < nVertexCount; w++)
		{
			//如果复合路径(就是有多条边)的权重   小于   单路径(直达)的权重    则调整最小权重路径vctMinPath
			// 不可直达的权重初始化为 MAGIC_MAX_WEIGHT  即无穷大
			if (!vctVisitedRows[w] && 0 != matrix[k][w] &&(min + matrix[k][w]) < vctMinPath[w])
			{
				vctMinPath[w] = min + matrix[k][w];
				vctPrevious[w] = k;    //将此顶点加入到最短路径前驱
			}
		}
	}
}


void Floyd(int num, std::vector<std::vector<int>> &p, std::vector<std::vector<int>>& d)
{
	for (int i = 0; i < num; ++i)   //初始化p
	{
		for (int j = 0; j < num; ++j)
		{
			//d[i][j] = g[i][j];
			p[i][j] = j;
		}
	}
	for (int i = 0; i < num; ++i)   //初始化d和p
	{
		for (int j = 0; j < num; ++j)
		{
			for (int k = 0; k < num; k++)
			{
				if (d[j][k] > d[j][i] + d[i][k])
				{
					d[j][k] = d[j][i] + d[i][k];
					p[j][k] = p[j][i];
				}
			}
		}
	}
}


```





### 测试

```cpp
// datastructure.cpp : 此文件包含 "main" 函数。程序执行将在此处开始并结束。
//

#include <iostream>
#include "adjenct_matrix.h"
#include "algo.h"
#include <stack>

int main()
{

	AdjenctMatrix<int, int>  adjmatrx(10);
	adjmatrx.InsertVertex(1);
	adjmatrx.InsertVertex(2);
	adjmatrx.InsertVertex(3);
	adjmatrx.InsertVertex(4);


	adjmatrx.InsertEdge(1, 2, 1);
	adjmatrx.InsertEdge(1, 3, 2);
	adjmatrx.InsertEdge(2, 4, 5);
	adjmatrx.InsertEdge(3, 4, 1);


	adjmatrx.ShowMatrix();


	std::cout << "========" << std::endl;
	adjmatrx.DFSTraverse();

	std::cout << "========" << std::endl;
	adjmatrx.BFSTraverse();

	std::cout << "========" << std::endl;


	
	int nVertexCount = adjmatrx.GetVertexCount();
	int nBeginVertex = 1;
	int nBeginVertexIndex = adjmatrx.GetVertexPosition(nBeginVertex);
	std::vector<int> vctPrevious(nVertexCount,  nBeginVertexIndex );
	std::vector<int> vctMinPath(nVertexCount, MAGIC_MAX_WEIGHT);
	
	Dijkstra(nVertexCount, nBeginVertexIndex, vctPrevious, vctMinPath, adjmatrx.GetMatrix());

	for (auto const &item : vctMinPath)
	{
		std::cout << item << " , ";
	}
	std::cout << std::endl;

	
	int nEndVertex = 4;
	int nEndVertexIndex = adjmatrx.GetVertexPosition(nEndVertex);
	std::stack<int>  minPath;
	minPath.push(nEndVertexIndex);
	for (int i = nEndVertexIndex; ; )
	{
		minPath.push( vctPrevious[i] );
		i = vctPrevious[i];
		if (nBeginVertexIndex == i)
		{
			break;
		}
	}

	for ( ; !minPath.empty() ; )
	{
		int pos = minPath.top();
		std::cout << adjmatrx.GetVertexValueByPos(pos);
		minPath.pop();
		if (minPath.size() > 0)
		{
			std::cout << "->";
		}
	}
	std::cout << std::endl;


    std::cout << "Hello World!\n"; 
}


```

