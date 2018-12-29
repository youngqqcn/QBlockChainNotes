//'use strict';

/**
 * @author: yqq
 * @create: 2018-12-29 12:06
 * @descriptions:
 */


const MyStringStore = artifacts.require("./MyStringStore.sol");

contract("MyStringStore", accounts => {
    it("should store the string 'Hey there!'", async () => {
        const myStringStore = await MyStringStore.deployed();

        // Set myString to "Hey there!"
        await myStringStore.set("Hey there!", { from: accounts[0] });

        // Get myString from public variable getter
        const storedString = await myStringStore.myString.call();

        assert.equal(storedString, "Hey there!", "The string was not stored");
    });
});