//异步IO



let fs = require("fs");

//异步
fs.writeFile("test.txt", "this is test string." , function () {
    console.log("写完了")
});

//同步
fs.writeFileSync("test2.txt", "this is test string.", "");

console.log("执行了");
console.log("执行了");
