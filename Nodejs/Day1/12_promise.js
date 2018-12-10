

let fs = require("fs");
let path = require("path");
let util = require("util");


//promise  async/await




/*
async function demo() {

    try{

    let pstat = util.promisify( fs.stat);
    let files = await pstat("test.txt");

    if(files.isDirectory()){
        console.log("files is dir")
    }else{
        console.log("files is file")
    }

    }catch (e) {
        throw e;
    }

}


demo();
*/




let promise = new Promise((resolve , reject) =>{

    console.log("构造promise");
     //err = new Error("hahah");
   // let err = null;
   // c.a = 100;
   // resolve("ok");
   //  reject("fd");

    throw new Error("构造中的异常");

    // if(err){
    //     reject(err);
    // }else{
    //     resolve("ok");
    // }
});


function ok(data) {
   console.log("ok函数");
}

function fault(data) {
    console.log("fault函数");
}


//下面三种写法都可以
//1. promise.then(ok, fault); //fault函数

//2. promise.then(ok).catch(fault); //fault函数

//3. promise.then(ok).catch(err=>{  //fault函数
//     fault(err);
// });


promise.then((data)=>{
   console.log(" ok 了");
   // c.b  = 1000;
}, (err)=>{
   console.log(" 捕获promise构造中的异常 ");
   // c.c = 99;
}).catch((err)=>{
    console.log("这是 onfulfilled 和 onRejected 函数中的异常");
});

console.log("helllllllll");






/*
结论:

    1.promise.then 有两个参数
        onfulfilled -->对应构造时的resolve, 当onfulled
        onrejected-->对应构造时的reject

    2.因为 promise.then的两个参数(函数变量) 是异步执行的,
      所以promise.then() 后面的代码会继续执行

    3.promise.then() 返回的是一个新的promise

    4.构造函数中, 需要显示调用resolve, 但是不用显示调用reject(如果在then函数中有指定, 出错时会自动调用)

    5. promise 有三种状态  Pending   fullfilled(已成功)    rejected(已失败)

              只能是  Pending 转为 其他两个状态,   不可逆!
       也就是说:  在 Promise构造中, resolve 和  reject   只能执行其中一个.

 */
















































