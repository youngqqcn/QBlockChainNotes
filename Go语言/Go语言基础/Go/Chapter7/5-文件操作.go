package main

/**
*作者: yqq
*日期: 2018/12/3  16:40
*描述: 文件操作
*/

/*

1.目录操作

func Mkdir(name string, perm FileMode) error //创建名称为name的目录，权限设置是perm，例如0777
func MkdirAll(path string, perm FileMode) error //根据path创建多级子目录，例如astaxie/test1/test2。
func Remove(name string) error //删除名称为name的目录，当目录下有文件或者其他目录时会出错
func RemoveAll(path string) error //根据path删除多级子目录，如果path是单个名称，那么该目录下的子目录全部删除。


2.文件操作
//新建文件
func Create(name string) (file *File, err Error) //根据提供的文件名创建新的文件，返回一个文件对象，默认权限是0666的文件，返回的文件对象是可读写的。
func NewFile(fd uintptr, name string) *File //根据文件描述符创建相应的文件，返回一个文件对象

//打开文件
func Open(name string) (file *File, err Error) //该方法打开一个名称为name的文件，但是是只读方式，内部实现其实调用了OpenFile。
func OpenFile(name string, flag int, perm uint32) (file *File, err Error) //打开名称为name的文件，flag是打开的方式，只读、读写等，perm是权限



3.写文件
写文件函数：
func (file *File) Write(b []byte) (n int, err Error) //写入byte类型的信息到文件
func (file *File) WriteAt(b []byte, off int64) (n int, err Error) //在指定位置开始写入byte类型的信息
func (file *File) WriteString(s string) (ret int, err Error) //写入string信息到文件

4.读文件
读文件函数：
func (file *File) Read(b []byte) (n int, err Error) //读取数据到b中
func (file *File) ReadAt(b []byte, off int64) (n int, err Error) //从off开始读取数据到b中


5. 删除文件
func Remove(name string) Error  //调用该函数就可以删除文件名为name的 文件 或 目录

 */




func main() {

}
