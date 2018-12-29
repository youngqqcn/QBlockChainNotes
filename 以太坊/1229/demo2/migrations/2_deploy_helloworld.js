//'use strict';

/**
 * @author: yqq
 * @create: 2018-12-29 14:39
 * @descriptions:
 */



var HelloWorld = artifacts.require("./HelloWorld.sol");

module.exports = function(deployer) {
    deployer.deploy(HelloWorld);
};