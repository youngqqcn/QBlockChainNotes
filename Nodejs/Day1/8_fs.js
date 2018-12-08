
const fs = require("fs"); //文件系统
let path = require("path");

fs.stat("test.txt", (err, stat)=>{

    if(err){
        console.log(err);
        return;
    }
    console.log(stat);
});

console.log("======================");


fs.readFile("test.txt", (err, data)=>{
    if(err){
        throw err;
    }

    console.log(data.toString());

});




fs.writeFile("test.txt", "hello world", (err, )=>{
    if(err){
        throw err;
    }

    console.log("wirte ok!")

});



fs.readdir("../Day1", (err, files)=>{

    //console.log(files);

    files.forEach(f =>{
        fs.stat(path.join("../Day1", f), (err, stat)=>{
            if(stat.isDirectory()){
                console.log(f, "is dir")
            }else{
                console.log(f, "is file")
            }
        })
    });


    // for(var i = 0; i <100; i++){
    //     console.log(i);
    // }

});


//删除文件
fs.unlink("test.txt", (err)=>{
    if(err){
        throw err;
    }
    console.log("delete ok");
});


//删除空目录
// fs.rmdir()




