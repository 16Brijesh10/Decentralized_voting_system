#backend.py
from flask import Flask, jsonify, request, json
import logging
from web3 import Web3
import os

# Configure logging
logging.basicConfig(level=logging.DEBUG)

# Blockchain setup (Local Ganache or other local Ethereum node)
rpc = "HTTP://127.0.0.1:7545"  # Local RPC for Ganache or Hardhat
web3 = Web3(Web3.HTTPProvider(rpc))

# Replace with your contract ABI and address (or set locally)
abi = '[{"constant":true,"inputs":[],"name":"candidatesCount","outputs":[{"name":"","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function","signature":"0x2d35a8a2"},{"constant":true,"inputs":[{"name":"","type":"uint256"}],"name":"candidates","outputs":[{"name":"id","type":"uint256"},{"name":"name","type":"string"},{"name":"voteCount","type":"uint256"}],"payable":false,"stateMutability":"view","type":"function","signature":"0x3477ee2e"},{"constant":true,"inputs":[{"name":"","type":"address"}],"name":"voters","outputs":[{"name":"","type":"bool"}],"payable":false,"stateMutability":"view","type":"function","signature":"0xa3ec138d"},{"inputs":[],"payable":false,"stateMutability":"nonpayable","type":"constructor","signature":"constructor"},{"anonymous":false,"inputs":[{"indexed":true,"name":"_candidateId","type":"uint256"}],"name":"votedEvent","type":"event","signature":"0xfff3c900d938d21d0990d786e819f29b8d05c1ef587b462b939609625b684b16"},{"constant":false,"inputs":[],"name":"end","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function","signature":"0xefbe1c1c"},{"constant":false,"inputs":[{"name":"_candidateId","type":"uint256"}],"name":"vote","outputs":[],"payable":false,"stateMutability":"nonpayable","type":"function","signature":"0x0121b93f"}]' # Add ABI here
contract_addr = "0x3F90DD7EC259DCe1ca019CCD8E49837EA4272b34"  # Replace with your contract address

# Flask app setup
app = Flask(__name__)
app.secret_key = os.getenv("SECRET_KEY", "i love white chocolate too")

# Sensitive data (replace with local or hardcoded values)

accounts = ["0xdFd7A34269f3CDF3beef4A039fc9BAbdc0c56eAE","0x09a3b1F429db3646Ce49fd23b037d0bF5e356E36"]  # Add your accounts
privatekeys = ["0x5678657c721c7c74d03a043951ed287933a8d2dec8b856b56d5cb319209ee06d","0xff2cc3cc89de7ded12484678b2ad41b25cbb057eb8b97ee39e7068267ab6a2c2"]  # Add your private keys

# Application state
vote_tx = []
voted = set()
ended = False


@app.route("/", methods=["POST"])
def home():
    if not ended:
        try:
            data = json.loads(request.data)  # Safer way to parse JSON data
            logging.debug("Received data: %s", data)  # Log incoming data

            aid = int(data["aadhaarID"]) - 1
            if aid in voted:
                return "Already voted", 400  # Ensure the person has not voted yet

            cid = int(data["candidateID"])  # Candidate ID to vote for

            # Account and private key of the voter
            acc = accounts[aid]
            pvt = privatekeys[aid]

            contract = web3.eth.contract(address=contract_addr, abi=abi)
            has_voted = contract.functions.voters(acc).call()
            if has_voted:
                return "Already voted", 400
            transaction = contract.functions.vote(cid).build_transaction({
                'from': acc,
                'nonce': web3.eth.get_transaction_count(acc),
                'gas': 2000000,  # Example gas, you can adjust based on your contract
                'gasPrice': web3.to_wei('20', 'gwei')  # Example gas price in gwei
            })

            # Sign the transaction
            signed_tx = web3.eth.account.sign_transaction(transaction, pvt)

            # Send the transaction
            web3legacy = Web3(Web3.HTTPProvider(rpc))
            tx_hash = web3legacy.eth.send_raw_transaction(signed_tx.raw_transaction)

            # Store the transaction hash and mark the user as voted
            vote_tx.append(tx_hash.hex())
            voted.add(aid)

            return "Vote successfully casted", 200
        except Exception as e:
            logging.error("Error processing vote: %s", e)
            return f"Error processing: {str(e)}", 500
    else:
        return "Election period ended", 
    
@app.route("/end", methods=["POST"])
def end_election():
    global ended
    ended = True  # Mark the election as ended in the backend
    
    # Select the account and private key for ending the election
    account_index = 0  # Use index 0 for the first account or change as needed
    acc = accounts[account_index]
    pvt = privatekeys[account_index]
    
    # Initialize the contract
    contract = web3.eth.contract(address=contract_addr, abi=abi)
    
    try:
        # Build the transaction for calling `end`
        transaction = contract.functions.end().build_transaction({
            'from' : acc,
            'nonce': web3.eth.get_transaction_count(acc),
            'gas': 2000000,  # Set appropriate gas limit
            'gasPrice': web3.to_wei('20', 'gwei')  # Set gas price in gwei
        })
        
        # Sign the transaction
        signed_tx = web3.eth.account.sign_transaction(transaction, pvt)
        
        # Send the transaction
        web3legacy = Web3(Web3.HTTPProvider(rpc))
        tx_hash = web3legacy.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        return f"Election successfully ended\nTx Hash: {tx_hash.hex()}", 200
    except Exception as e:
        logging.error("Error ending the election: %s", e)
        return f"Error ending the election: {str(e)}", 500



@app.route("/results", methods=["GET"])
def count():
    if ended:
        res = []
        election = web3.eth.contract(address=contract_addr, abi=abi)
        
        # Fetch the candidates count
        candidates_count = election.functions.candidatesCount().call()

        for i in range(candidates_count):
            # Fetch each candidate's details (adjust based on your contract's structure)
            candidate = election.functions.candidates(i + 1).call()
            res.append({
                "id": candidate[0],  # Assuming candidate structure has ID as first element
                "name": candidate[1],
                "voteCount": candidate[2]
            })

        return json.dumps(res), 200
    else:
        return "Election still ongoing", 400


@app.route("/number_of_users", methods=["GET"])
def number_of_users():
    return str(len(accounts)), 200

@app.route("/isended", methods=["GET"])
def isended():
    return jsonify(ended), 200

@app.route("/candidates_list", methods=["GET"])
def candidates_list():
    try:
        res = []
        election = web3.eth.contract(address=contract_addr, abi=abi)
        for i in range(election.functions.candidatesCount().call()):
            res.append(election.functions.candidates(i + 1).call()[1])  # Candidate name
        return jsonify(res), 200
    except Exception as e:
        logging.error("Error fetching candidates: %s", e)
        return "Error processing", 500


if __name__ == '__main__':
    app.run(host="0.0.0.0", port=80, debug=True)
