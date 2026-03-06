# Blockchain and Smart Contracts

## What is a Blockchain?

A blockchain is a **distributed, append-only ledger** -- a shared record book that anyone can read, no single entity controls, and nobody can alter after the fact.

### The Analogy

Imagine a town where every financial transaction is written in a big book kept in the town square. But instead of one book:

- Every citizen has an identical copy of the book
- Every time a new transaction happens, every copy is updated simultaneously
- Pages are sealed with wax (cryptography) so that altering a past page is detectable
- New pages can only be added at the end -- you cannot insert, edit, or tear out old pages

This is a blockchain. The "blocks" are pages (groups of transactions), and the "chain" is the fact that each page references the previous page's seal, creating an unbreakable sequence.

### Why This Matters

Traditional databases have an administrator who can edit or delete records. A blockchain does not. Once something is recorded, it is permanent. This makes it ideal for situations where you need to prove that a record existed at a certain time and has not been tampered with -- exactly what TrustChain-AV needs for media authenticity verification.

## What is Ethereum?

Ethereum is a specific blockchain platform, launched in 2015. While Bitcoin was designed primarily for financial transactions ("send 5 coins from A to B"), Ethereum added the ability to run **programs** on the blockchain. These programs are called **smart contracts**.

Think of Bitcoin as a calculator (it can do math with money) and Ethereum as a smartphone (it can run apps).

### Ethereum Key Concepts

**Ether (ETH)**: The native cryptocurrency of Ethereum. Used to pay for transactions and computation on the network.

**Gas**: The unit measuring computational effort. Every operation on Ethereum costs gas, and gas is paid in ETH. This prevents people from running infinite loops or spamming the network -- every computation has a real cost.

**Wallet**: A pair of cryptographic keys (public and private) that represent an identity on Ethereum. The public key is your address (like an email address), and the private key proves you own it (like a password).

**Transaction**: Any action on the blockchain -- sending ETH, deploying a contract, or calling a contract function. Each transaction is signed with your private key, recorded on the blockchain, and assigned a unique transaction hash.

## What is a Smart Contract?

A smart contract is a program that lives on the blockchain. Once deployed, it runs exactly as written -- nobody can change it, shut it down, or interfere with it.

### The Vending Machine Analogy

A smart contract is like a vending machine:

1. The rules are predefined and transparent (insert $1, select B3, get a snack)
2. It executes automatically when conditions are met (no human operator needed)
3. It is trustless (you do not need to trust a cashier -- the machine follows its rules mechanically)
4. Once deployed, the rules cannot be changed (the machine does what it was built to do)

### How Smart Contracts Differ from Regular Programs

| Aspect | Regular Program | Smart Contract |
|--------|----------------|----------------|
| Where it runs | Your server | Thousands of nodes worldwide |
| Who controls it | You (the developer) | Nobody (it is autonomous) |
| Can it be changed? | Yes, anytime | No, once deployed it is permanent |
| Data persistence | Your database | The blockchain (permanent, public) |
| Cost to run | Electricity for your server | Gas fees (paid in ETH) |
| Trust model | Trust the developer | Trust the code (verifiable by anyone) |

## Solidity: The Language of Smart Contracts

**Solidity** is the programming language used to write smart contracts for Ethereum. It was designed specifically for this purpose, with built-in concepts for handling money, ownership, and events.

TrustChain-AV's smart contract (MediaRegistry) is written in Solidity and does a few specific things:

### What MediaRegistry Does

1. **Register Media**: Accepts a file hash (the SHA-256 hash of an analyzed video) and stores it on the blockchain with a timestamp. This creates a permanent, tamper-proof record that "this file was analyzed at this time."

2. **Lookup Media**: Given a file hash, returns whether it has been registered and when. Anyone can verify this -- it is a public read operation that costs no gas.

3. **Emit Events**: When a new registration happens, the contract emits a **MediaRegistered event**. Events are like public announcements on the blockchain -- external systems can listen for them and react.

### Why Not Store Everything On-Chain?

Storing data on the blockchain is expensive. Ethereum charges gas for every byte stored. Storing a 500MB video would cost thousands of dollars. Instead, TrustChain-AV stores only the essentials on-chain:

- The SHA-256 hash of the video (32 bytes)
- A timestamp
- A Merkle root (a compact proof of the analysis results)

The full video, analysis results, and detailed metadata stay in the PostgreSQL database. The blockchain serves as an anchor point -- proof that the analysis existed at a specific time.

## Testnets: Safe Experimentation

### What is a Testnet?

A testnet is a separate blockchain network used for development and testing. It works identically to the main Ethereum network (mainnet), but its currency has no real value.

### Sepolia

TrustChain-AV deploys to **Sepolia**, one of Ethereum's official testnets. Key properties:

- **Free to use**: You get test ETH from "faucets" (websites that give you fake money for testing)
- **Identical behavior**: Smart contracts work the same as on mainnet
- **Public and persistent**: Contracts deployed on Sepolia are real, accessible, and verifiable -- just not with real money
- **Etherscan support**: You can view transactions and contracts on sepolia.etherscan.io, just like the real Etherscan

Using a testnet is like rehearsing a play. The performance is real, the actors follow the script, the audience watches -- but it is not opening night. TrustChain-AV's contract works exactly as it would on mainnet, but without the financial risk.

## Hardhat: Development Toolkit

**Hardhat** is a development environment for Ethereum smart contracts. Think of it as the workshop where you build, test, and deploy your contracts before they go live.

Hardhat provides:

- **Local blockchain**: A private, in-memory blockchain on your computer for instant testing
- **Testing framework**: Write automated tests for your contract (does registration work? does lookup return correct data?)
- **Deployment scripts**: Automated deployment to testnets or mainnet
- **Debugging tools**: Step-by-step execution of contract code

TrustChain-AV uses Hardhat to:
1. Develop the MediaRegistry contract
2. Run automated tests locally (no network fees)
3. Deploy the tested contract to Sepolia

## Web3.py: The Bridge

**Web3.py** is a Python library that lets the FastAPI backend communicate with the Ethereum blockchain. It is the bridge between TrustChain-AV's backend and the smart contract.

When a user clicks "Register on Blockchain":

1. The FastAPI backend receives the request
2. Web3.py constructs a transaction calling `registerMedia()` on the smart contract
3. The transaction is signed with the backend's private key
4. Web3.py submits the transaction to the Sepolia network
5. The transaction is mined (included in a block)
6. Web3.py retrieves the transaction hash and block number
7. The backend stores these in PostgreSQL for display to the user

### The Waiter Analogy (Extended)

Continuing the restaurant analogy from the FastAPI doc:

- **FastAPI** is the waiter (takes your order)
- **Web3.py** is the phone the waiter uses to call an external supplier
- **Ethereum/Sepolia** is the external supplier (processes the order independently)
- **The smart contract** is the supplier's automated system (follows predefined rules)

The waiter does not control the supplier -- they just place the order and wait for confirmation.

## How It All Fits Together in TrustChain-AV

```
User clicks "Register on Blockchain"
    |
    v
Frontend sends request to FastAPI
    |
    v
FastAPI backend uses Web3.py to call MediaRegistry.registerMedia()
    |
    v
Transaction submitted to Sepolia network
    |
    v
Ethereum miners/validators process the transaction
    |
    v
MediaRegistered event emitted
    |
    v
Transaction confirmed (hash + block number returned)
    |
    v
Backend stores tx hash + block in PostgreSQL
    |
    v
Frontend shows: "Registered! View on Etherscan: [link]"
```

### What Gets Verified

Later, anyone can verify the registration:

1. Take the video file
2. Compute its SHA-256 hash
3. Call the smart contract's lookup function with that hash
4. The contract returns: "Yes, registered on March 6, 2026"
5. This proves the file existed and was analyzed on that date

Since the blockchain is immutable, this proof cannot be forged, backdated, or deleted.

## Key Concepts

| Concept | Meaning |
|---------|---------|
| **Blockchain** | A distributed, append-only ledger that nobody controls |
| **Ethereum** | A blockchain platform that supports smart contracts |
| **Smart Contract** | A program that runs on the blockchain, autonomous and unchangeable |
| **Solidity** | The programming language for Ethereum smart contracts |
| **Gas** | The cost of computation on Ethereum (prevents abuse) |
| **Testnet** | A practice blockchain with free, valueless currency |
| **Sepolia** | The Ethereum testnet used by TrustChain-AV |
| **Hardhat** | Development toolkit for building and testing smart contracts |
| **Web3.py** | Python library for interacting with Ethereum from the backend |
| **Transaction hash** | A unique identifier for a blockchain transaction |
| **Event** | A public log entry emitted by a smart contract (e.g., MediaRegistered) |
| **Immutable** | Cannot be changed after the fact |

## Further Reading

- [SHA-256 Hashing](sha256-hashing.md) -- The file fingerprint stored on-chain
- [FastAPI](fastapi.md) -- The backend that triggers blockchain registration
- [Deepfake Detection](deepfake-detection.md) -- Why permanent records of analysis matter
