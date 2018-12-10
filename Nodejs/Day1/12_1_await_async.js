'use strict';

/**
 * @author: yqq
 * @create: 2018-12-10 15:21
 * @descriptions:
 *
 *
 * 参考网址: https://www.cnblogs.com/SamWeb/p/8417940.html
 *          博主写的很好, 一看就明白
 *
 *
 *       Promise.resolve(value)方法返回一个以给定值解析后的Promise 对象。
 *          1.但如果这个值是个thenable（即带有then方法），返回的promise会“跟随”这个thenable的对象，
 *          采用它的最终状态（指resolved/rejected/pending/settled）；
 *
 *          2.如果传入的value本身就是promise对象，则该对象作为Promise.resolve方法的返回值返回；
 *
 *          3.否则以该值为成功状态返回promise对象(即传入的是普通的值)
 *
 *
 *      注意点:
 *          1.async函数返回的是一个promise对象
 *          2.async 修饰的函数是异步执行的
 *          3.await 函数只能在 async函数中使用
 */

/*
//////////////////////////////test1/////////////////////////
async function timeout() {
    return 'hello world'
}
timeout().then(result => {  //因为 async函数返回的是一个promise对象
    console.log(result);
})
console.log('虽然在后面，但是我先执行');
*/



/*
//////////////////////////////test2/////////////////////////
async function timeout() {
    return 'hello world'
}
console.log(timeout());
console.log('虽然在后面，但是我先执行');
*/


/*
//////////////////////////////test3/////////////////////////
async function timeout(flag) {
    if (flag) {
        return 'hello world'
    } else {
        throw 'my god, failure'
    }
}
console.log(timeout(true))  // 调用Promise.resolve() 返回promise 对象。
console.log(timeout(false));
// console.log(timeout(false).catch(err=>{
//     console.log(err);
// })); // 调用Promise.reject() 返回promise 对象。
*/



//////////////////////////////test4/////////////////////////
// 2s 之后返回双倍的值
function doubleAfter2seconds(num) {
    return new Promise((resolve, reject) => {
        setTimeout(() => {
            resolve(2 * num)
        }, 2000);
    } )
}

async function testResult() {
    let first = await doubleAfter2seconds(30);
    let second = await doubleAfter2seconds(50);
    let third = await doubleAfter2seconds(30);
    console.log(first + second + third);
}
testResult();




