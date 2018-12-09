'use strict';

/**
 * @author: yqq
 * @create: 2018-12-09 14:38
 * @descriptions:
 *
 */




let EventEmitter = require('events');

class MyEmitter extends EventEmitter{

}


let myEmitter = new MyEmitter();

myEmitter.on('event1', (param)=>{
    console.log("事件触发了", JSON.stringify(param));
});


setTimeout(()=>{
    myEmitter.emit('event1', {"name":"yqq", "age":"23"});
}, 2000);

