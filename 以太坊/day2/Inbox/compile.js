
//使用npm  install solc@0.4.25   , 高版本有错

const path = require("path");
const fs = require("fs");
const solc = require("solc");


const srcpath = path.resolve(__dirname, "contracts", "inbox.sol");
// console.log(srcpath);


const source = fs.readFileSync(srcpath, 'utf-8');
// console.log(source);

const result =  solc.compile(source, 1);
// console.log(result);

module.exports = result.contracts[':Inbox'];   //导出编译结果, 部署合约时需要用到