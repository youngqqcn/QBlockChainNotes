

let fs = require("fs");
let path = require("path");
let util = require("util");


//promise  async/await




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
