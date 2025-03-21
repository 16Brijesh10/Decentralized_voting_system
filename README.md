
# decentralized-voting-system

A decentralized voting system where a user can walk into a government authorized center (Ex- banks, telecom companies etc.) and cast their vote using the proposed portal.


**NOTE:** All diagrams are made by me and appropriate credits must be given before copying it.
## Key Advantages

 - **VoterID required** as a user's validity (age: 18+) 
 - **Secure vote** by Azure blockchain and biometric authentication (using pre-existing Aadhaar database)
 - **Reduced cost** during election process
 - **Shorter wait times** as it is decentralized
 - A vote can be cast from **anywhere in the country**
 - **Efficient election system** in which the portal can be up for days together, in turn **increasing voter turnout**

## A Vote's Story

A user will walk into a government authorized center and complete his/her biometric verification. Once the verification is complete the user will be taken to a web-based portal **(developed by us)** where he/she will be presented with the voting options. The portal then sends the information of the user's vote (encrypted) to backend **(developed by me)** where the data will be decrypted and the vote's transaction from the user to the candidate will take place using the Azure blockchain service. The candidate with the most votes is elected. During each election time the users are that are voted are logged which will make sure only one transaction can be made by the user during the whole election process.

 
## Voting System Workflow

During the election time the admin will initiate the election. When the election is initiated the candidate list is sent to the front end of the portal (which is setup at govt. authorized locations). The front end can display useful information on the candidate and can aid in their decision making (display promises, proposals etc.). The encrypted vote along with the user information is sent to the initiate vote method at the backend. This initiate vote method calls the account validation method which validates the user using the Aadhaar API and make sures that the user has not voted yet. If the user validation is successful then the vote cast method is called, which sends the vote as a contract to the Azure Blockchain Service.  

**NOTE:** At the end of the election, the candidate with the most votes is elected.


## Technologies
 - Deep Face (for biometric authentication)
 - Python (to communicate with blockchain and for backend and frontend API calls) 
 - Truffle (provides tools to create and test smart contracts)
 - Ganache (to create private blockchain network for testing on localhost) 
 - Flask (web framework)
 - Docker (deployment of portal on the cloud)

