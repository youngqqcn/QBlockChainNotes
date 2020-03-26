
let EOS = require('eosjs');

eos = EOS.localnet({
    chainId:"e70aaab8997e1dfce58fbfac80cbbb8fecec7b99cf982a9444273cbc64c41473",
    keyProvider:['5JfUC7k6yGs5RCoHeX464TqZnPWgdqrFfsETBzYGPB9ipDfNyzw'],
    httpEndpoint:'http://jungle2.cryptolions.io:80'
});


eos.contract('child.acnt').then((contract) => {
    contract.ping("child.acnt",{authorization:['child.acnt']}).then((res) => {
        console.log(res)
    })
});
