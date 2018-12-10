'use strict';

/**
 * @author: yqq
 * @create: 2018-12-10 13:27
 * @descriptions:
 */

//npm install pm2 -g
//pm2 start   xxxx.js
//pm2 list
//pm2 log
//pm2 stop  id(app的id)
//pm2 delete
//pm2 -h  //查看帮助


//使用以下命令  启动    4个cpu内核
//pm2 start 1_express使用.js -i 4


//可以使用 Apache 自带的 ab测试工具 进行测试


//ab -n 10000 -c 1000 http://127.0.0.1:3000/
// -n   请求书
// -c   并发请求数




