
//console.log(global.process);
//console.log(global.process);
//console.log(global.path);
// console.log(global.process.env);
console.error("error");
console.warn("warning");

console.log(__dirname); //当前文件所在目录
console.log(__filename); //当前文件名



console.time("label1");

setTimeout(()=>{

    console.log("helloowrl")
}, 1000);
console.timeEnd("label1"); //打印从  time 到 timeEnd 中间代码执行所耗的时间


//每隔1s, 执行以下函数
setInterval(()=>{
    console.log("run every 1 second")
}, 1000);
