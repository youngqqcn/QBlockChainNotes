const ecc = require("eosjs-ecc");


/*
ecc.randomKey().then( privateKey => {
    console.log("Private Key:\t", privateKey); // wif
    console.log("Public Key:\t", ecc.privateToPublic(privateKey)); // EOSkey...
});
*/






data = Buffer.from("b099531a13633f8cfb89b65b7794b1f8ecca8d03ab6bfd846d849d4609cd0ad0" , "hex");
console.log(data);
console.log( ecc.signHash(data, '5JfUC7k6yGs5RCoHeX464TqZnPWgdqrFfsETBzYGPB9ipDfNyzw'));

/*
data = Buffer.from("11e1d69884d3292ab924a0f2c4451770aebc88e4505c6bab0f36f348b128489c" , "hex");
console.log(data);
console.log( ecc.signHash(data, '5JfUC7k6yGs5RCoHeX464TqZnPWgdqrFfsETBzYGPB9ipDfNyzw'));
*/

/*
data = Buffer.from("b099531a13633f8cfb89b65b7794b1f8ecca8d03ab6bfd846d849d4609cd0ad0" , "hex");
console.log(data);
data_sha256 = ecc.sha256(data);
// console.log(data_sha256);
sig = ecc.signHash(data_sha256, '5JfUC7k6yGs5RCoHeX464TqZnPWgdqrFfsETBzYGPB9ipDfNyzw');
*/

// console.log( ecc.signHash(data, '5JfUC7k6yGs5RCoHeX464TqZnPWgdqrFfsETBzYGPB9ipDfNyzw'));

/*

sha256: 02208b9403a87df9f4ed6b2ee2657efaa589026b4cce9accc8e8a5bf3d693c86
<Buffer ff>
<Buffer 80 3c e8 40 10 a8 b1 5f 2b 99 75 80 f4 33 00 88 a4 e8 0e a9 ea cb 36 64 cf 29 4c 80 e9 62 1a 74>
5c9e8316d0221aa043e68539b0cced905b05f1693171108139a00713065f7d82
SIG_K1_KWYjQdiqR2ypURZL3Rf2iRSKBwUokZeWDPWTFU1w3kwPhpFrybsUuJb3WzFJQCvZBwpnyr2m8vTF44N6QxY1ZTP5eKLgty

 */