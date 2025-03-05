const HDWalletProvider = require('@truffle/hdwallet-provider');
const fs = require('fs');

module.exports = {
  networks: {
    development: {
      host: "127.0.0.1", // Localhost (Ganache CLI)
      port: 7545,        // Default Ganache CLI port
      network_id: "5777", // Match Ganache network id 
    },
    ganacheLocal: {
      provider: () => {
        // Read mnemonic from mnemonic.env file
         const mnemonic = "catalog impact feel enter parrot income budget robot please scrap skin network";
        //const mnemonic = fs.readFileSync("mnemonic.env").toString().trim();
        return new HDWalletProvider(mnemonic, "http://127.0.0.1:7545");  // Ensure this is port 8545 if using Ganache CLI
      },
      network_id: "5777", // Match Ganache network id
      gas: 5000000, // Increase gas limit
      gasPrice: 20000000000
    }
  },
  mocha: {
    // Test options (if needed)
  },
  compilers: {
    solc: {
      version: "0.8.13", // Specify Solidity compiler version
      settings: {
        optimizer: {
          enabled: true,
          runs: 200,
        },
      },
    },
  },
};
