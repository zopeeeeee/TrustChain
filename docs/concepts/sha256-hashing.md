# SHA-256 Hashing

## What is Hashing?

Hashing is the process of taking any input (a file, a message, a password) and producing a fixed-size string of characters called a **hash** or **digest**. The hash acts as a digital fingerprint of the input.

### The Analogy

Think of hashing like a meat grinder. You put a steak in (the input), and you get ground meat out (the hash). Key properties:

1. **Same input, same output**: If you grind the exact same steak twice, you get the same ground meat pattern
2. **Different input, different output**: A chicken breast produces different ground meat than a steak
3. **One-way**: You cannot reconstruct the original steak from the ground meat
4. **Fixed-size output**: No matter how big the input (a whole cow or a single chicken wing), the output is always the same amount

## What is SHA-256?

SHA-256 stands for **Secure Hash Algorithm, 256-bit**. It was designed by the United States National Security Agency (NSA) and is one of the most widely used cryptographic hash functions in the world.

Given any input, SHA-256 always produces a 256-bit (64 hexadecimal character) output. For example:

- Input: "hello" produces: `2cf24dba5fb0a30e26e83b2ac5b9e29e1b161e5c1fa7425e73043362938b9824`
- Input: "Hello" (capital H) produces: `185f8db32271fe25f561a6fc938b2e264306ec304eda518007d1764826381969`

Notice how a single character change (lowercase h to uppercase H) completely changes the output. This property is called the **avalanche effect**.

## Properties of SHA-256

### 1. Deterministic
The same input always produces the same hash. This is essential -- if you hash a video file today and hash the exact same file tomorrow, you get the same result. This consistency is what makes verification possible.

### 2. Fast to Compute
Hashing even a large file (500MB video) takes only a few seconds. This makes it practical for real-time applications.

### 3. One-Way (Pre-image Resistance)
Given a hash, it is computationally infeasible to figure out what the original input was. You cannot "reverse" the hash. This is important for security -- knowing the hash of a file tells you nothing about its contents.

### 4. Collision Resistant
It is virtually impossible to find two different inputs that produce the same hash. The probability is so low (1 in 2^256) that it would take more energy than exists in the solar system to find a collision through brute force.

To put 2^256 in perspective: it is approximately the number of atoms in the observable universe. Squared.

### 5. Avalanche Effect
A tiny change in the input produces a completely different hash. Change a single pixel in a video frame, and the entire SHA-256 hash changes. There is no way to tell from two hashes how similar the original inputs were.

## Why TrustChain-AV Uses SHA-256

### File Integrity Verification

When a user uploads a video, TrustChain-AV computes the SHA-256 hash of the file. This hash serves as a unique fingerprint:

- If someone claims "this video was analyzed by TrustChain-AV and found to be REAL," anyone can re-hash the video and compare it to the stored hash
- If the hashes match, the video is the exact same file that was analyzed
- If the hashes differ, the video has been modified since analysis (even a single byte change)

### Tamper Evidence

This is crucial because after a video is analyzed, someone might:
- Re-encode the video (changes the file bytes)
- Edit a few frames (adds or removes content)
- Strip or replace the audio track
- Compress the file differently

Any of these modifications would produce a completely different SHA-256 hash, immediately revealing that the video is not the same one that was originally analyzed.

### Blockchain Registration

When TrustChain-AV registers an analysis result on the blockchain (see [Blockchain and Smart Contracts](blockchain-and-smart-contracts.md)), it stores the SHA-256 hash on-chain -- not the video itself. This is practical because:

- Storing a 500MB video on the blockchain would cost thousands of dollars in gas fees
- Storing a 64-character hash costs a tiny fraction of that
- The hash is just as useful for verification -- anyone can re-hash the original video and check if it matches

### The Verification Flow

```
1. User uploads video
2. TrustChain-AV computes SHA-256 hash: abc123...
3. Analysis runs, produces verdict: REAL (95% confidence)
4. Hash abc123... is registered on the blockchain with the verdict

--- Later, someone questions the video's authenticity ---

5. They hash the video file themselves
6. They get: abc123...
7. They look up abc123... on the blockchain
8. They find: "Registered on March 6, 2026. Verdict: REAL, 95% confidence"
9. Since the hashes match, the video is verified as the exact file that was analyzed
```

If the video had been tampered with after analysis, step 6 would produce a different hash (e.g., xyz789...), and step 7 would find no matching record on the blockchain.

## SHA-256 vs. Other Hash Functions

| Algorithm | Output Size | Status | Use Case |
|-----------|-------------|--------|----------|
| MD5 | 128 bits | Broken (collisions found) | Legacy systems only |
| SHA-1 | 160 bits | Broken (collisions found) | Being phased out |
| **SHA-256** | **256 bits** | **Secure** | **Industry standard, used by Bitcoin, TLS, etc.** |
| SHA-3 | 256 bits | Secure | Newer alternative, different internal design |

TrustChain-AV uses SHA-256 because it is the most widely adopted, well-tested, and trusted cryptographic hash function in use today. It is the same algorithm that secures Bitcoin transactions and HTTPS connections.

## Common Misconceptions

### "Hashing is the same as encryption"
No. Encryption is **two-way** -- you can encrypt and decrypt. Hashing is **one-way** -- you can hash but you cannot "un-hash." Encryption is for secrecy (keeping data private). Hashing is for integrity (verifying data has not changed).

### "If two files have the same hash, they might be different files"
Theoretically possible, but practically impossible with SHA-256. The chance is so astronomically small that it has never happened and likely never will.

### "Hashing the file takes a long time for large videos"
SHA-256 processes data at about 200-500 MB per second on modern hardware. A 500MB video takes about 1-2 seconds to hash -- negligible compared to the minutes of ML analysis.

## Key Concepts

| Concept | Meaning |
|---------|---------|
| **Hash** | A fixed-size fingerprint computed from any input |
| **SHA-256** | Secure Hash Algorithm producing a 256-bit (64 hex character) output |
| **Digest** | Another word for the hash output |
| **Collision** | Two different inputs producing the same hash (virtually impossible with SHA-256) |
| **Avalanche effect** | A tiny input change produces a completely different hash |
| **Pre-image resistance** | The inability to reverse a hash back to the original input |
| **Integrity** | The assurance that data has not been modified |

## Further Reading

- [Blockchain and Smart Contracts](blockchain-and-smart-contracts.md) -- Where hashes are stored permanently on-chain
- [Deepfake Detection](deepfake-detection.md) -- Why tamper evidence matters in the deepfake context
