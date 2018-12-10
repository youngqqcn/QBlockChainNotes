'use strict';

/**
 * @author: yqq
 * @create: 2018-12-10 12:09
 * @descriptions:
 *
 *
 */



// let express = require("express");
// let router  = express.Router();
//
//
// router.get('/list', (req, res)=>{
//
//     res.send("获取订单接口")
//
// });
//
//
// router.post('/create', (req, res)=>{
//
//     res.send("创建订单接口");
//
// });
//
//
//
// module.exports= router;


let express = require("express");
let router = express.Router();



router.use((req, res, next)=>{
    
    console.log("路由级别中间件");
    next();
    
});



router.get('/list', (req, res)=>{

    res.send("get");

});

router.post('/create', (req, res)=>{
    res.send("post");
});


module.exports=router;
