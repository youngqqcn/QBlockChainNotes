import TronStationSDK from 'tron-station-sdk';
import TronWeb from 'tronweb';

const HttpProvider = TronWeb.providers.HttpProvider;
const fullNode = new HttpProvider('https://api.trongrid.io');
const solidityNode = new HttpProvider('https://api.trongrid.io');
const eventServer = new HttpProvider('https://api.trongrid.io');

const privateKey = 'da146374a75310b9666e834ee4ad0866d6f4035967bfc76217c5a495fff9f0d0';

const tronWeb = new TronWeb(
    fullNode,
    solidityNode,
    eventServer,
    privateKey
);

// Constructor params are the tronWeb object and specification on if the net type is on main net or test net/private net
const tronStationSDK = new TronStationSDK(tronWeb, true);

async function getAccountBandwidth(address) {
  	console.log(await tronStationSDK.getAccountBandwidth(address));
}

getAccountBandwidth('TPL66VK2gCXNCD7EJg9pgJRfqcRazjhUZY');