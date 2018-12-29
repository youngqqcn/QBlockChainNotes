const MyStringStore = artifacts.require("MyStringStore");

module.exports = function(deployer) {
  deployer.deploy(MyStringStore);
};
