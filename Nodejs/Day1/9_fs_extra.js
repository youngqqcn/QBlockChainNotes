
 let fse = require("fs-extra");


/*
fse.remove("testdir", err =>{
    if(err) throw err;
    console.log("delete dir ok!")
});
*/



fse.watchFile("test2.txt", (cur, pre)=>{

    console.log("cur time:" + cur.mtime);
    console.log("prev time:" + pre.mtime);

});