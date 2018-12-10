'use strict';

/**
 * @author: yqq
 * @create: 2018-12-10 12:32
 * @descriptions:
 */

let orderRouter =  require('./router/order');
let userRouter =  require('./router/user');
let express = require("express");
let app = express();


//应用程序级别中间件:   权限认证 , 和  拦截

app.use((req, res, next)=>{


    console.time("firstmiddleware")

    // res.send("中间件")
    console.log("第一个中间件");


    // if(req.url.startsWith('/order')){
    //     //拦截
    //     res.send("拦截了");
    // }else{
    //     next();
    // }



    //需求案例:
    //   根据用户请求是否有token参数
    //     如果有, 则表示已登录
    //     否则, 未登录
    let token = req.get('token');
    if(token){
        //已经登录
        next();
    }else{
        res.send({
            code:-1,
            msg:"当前用户没登录"
        });
        next();
    }

    console.timeEnd("firstmiddleware");

});


app.use((req, res, next)=>{

    a = 9;

    console.log("第二个中间件");
    next();

});




app.use('/order', orderRouter);
app.use('/user', userRouter);


//统一, 错误处理
//错误处理中间件, 一般放在最后注册
app.use((err, req, res, next)=>{

    console.log("出错了");

    res.send({
        code : -1,
        msg : "出错了"
    });

});

app.listen(9999);

