---
title: "Fibonacci LFSR: How it works and How to Attack it"
description: Understanding the Fibonacci Linear Feedback Shift Register (LFSR), how it generates pseudo-random sequences, and why it is insecure when used as a stream cipher.
image: images/post/fibonacci-lfsr/thumbnail.png
authors:
  - Nithik R
date: 2025-09-28T15:00:00+05:30
categories:
  - Cryptography
tags:
  - XOR
  - Stream Cipher
  - Attack
postType: featured
draft: false
---

The **Fibonacci Linear Feedback Shift Register** is a classic example of a simple pseudo-random generator. It is often introduced in the study of stream ciphers and cryptanalysis because, while it can produce long pseudo-random sequences, its linearity also makes it vulnerable to attacks.  

In this post, I try to go through my understanding on how an LFSR works, how it can be used for encryption, and why a straightforward known-plaintext attack completely breaks it.  

---

## What is an LFSR?

An LFSR is one way to create a pseudo-random number generator. It generates a stream of bits from a linear function (here, XOR) of the previous state of bits.  

It consists of two core components:  

- **State**: a binary register of $m$ bits  
- **Feedback Coefficients**: a binary mask of $m$ bits that determines which bits are selected for XOR  

---

## How an LFSR Works

An initial state (seed) of $m$ bits is set with values $s_{m-1}, \dots, s_1, s_0$.  
A constant set of feedback coefficients is also set with values $p_{m-1}, \dots, p_1, p_0$.  

The output bit of the LFSR $s_m$, which is also the input to the leftmost position on the register, can be computed by the XOR-sum of the products of the state bit and corresponding feedback coefficient:

$$
s_m \equiv s_{m-1}p_{m-1} + \dots + s_{1}p_{1} + s_{0}p_{0} \pmod 2
$$

In general:  

$$
s_{i+m} \equiv \sum_{j=0}^{m-1} p_j s_{i+j} \pmod 2,\quad s_i, p_j \in \{0,1\},\; i=0,1,\dots
$$

At each iteration:  
- The register is shifted to the right.  
- The previous output bit is placed as the new leftmost bit.  
- The least significant bit at each stage is output to the bit stream.  


### Encrypting with an LFSR

An LFSR can be used in the form of a stream cipher. The bit stream generated from an LFSR can be used to encrypt data: every 8 bits from the stream are grouped together and XORed with the corresponding byte from the input plaintext. The result is printed as hex to ensure portability.  

This cipher is definitely **not secure**. The reason becomes clear when we look at the known-plaintext attack.  

---

## Known-Plaintext Attack

Because an LFSR is a linear system, its feedback coefficients can be recovered from a short stretch of output. If the register length $m$ is assumed to be known — and the first $2m$ bits of the plaintext are also known — the LFSR can be broken. Even if $m$ isn’t known exactly, a modern computer can brute force small values of $m$ very quickly.  

Let the known plaintext bits be $x_0, x_1, \dots, x_{2m-1}$ and the corresponding ciphertext bits be $y_0, y_1, \dots, y_{2m-1}$.  

The first $2m$ stream bits can be reconstructed by:  

$$
s_i \equiv x_i + y_i \pmod 2, \quad i = 0,1,\dots,2m-1
$$

We also know that  

$$
s_m \equiv s_{m-1}p_{m-1} + \dots + s_{1}p_{1} + s_{0}p_{0} \pmod 2
$$

Similarly, the equations for $s_{m+1}$ to $s_{2m-1}$ can be written. This gives $m$ linear equations in $m$ unknowns $p_0, p_1, \dots, p_{m-1}$.  

These equations can be solved using [Gaussian elimination](https://en.wikipedia.org/wiki/Gaussian_elimination) over the [Galois Field of 2](https://en.wikipedia.org/wiki/GF(2)).  

Once the feedback coefficients are found, the initial state (seed) is also known — it is simply the first $m$ reconstructed bits. With both the coefficients and seed, the LFSR can be clocked to reproduce the exact keystream used for encryption.  

Since XOR is symmetric, the ciphertext bytes can be XORed with this stream to recover the complete plaintext.  


---

## Demonstration

I have coded an implementation of both, the LFSR and the known-plaintext attack, using C and it can be viewed on my GitHub [repository](https://github.com/noinoiexists/Fibonacci-LFSR).


On running the encryption by setting the initial seed as `101110` and feedback coefficients as `111101`, I get the following ciphertext:

```sh
$ ./cipher
Seed:
101110
Feedback coefficients:
111101
Plaintext:
Go placidly amid the noise and the haste, and remember what peace there may be in silence.
Ciphertext (hex):
31ec3289b66d288e0c5d56bdc1a9d712a36691bf2c258801424abdc1aada56f77a9cfa642a941c5403bdc1aada56f17794bf6129821a1158f5c1b09e06e6739abf2c3f8f0d434abdcda5c756e177d9b3626b94015d4af3c3a190
```

Now assuming the role of an attacker, if I have the ciphertext, as well as just the first word `Go` of the plaintext, I can use the above mentioned known-plaintext attack to retrieve the complete plaintext:

```sh
$ ./attack
Ciphertext (hex):
31ec3289b66d288e0c5d56bdc1a9d712a36691bf2c258801424abdc1aada56f77a9cfa642a941c5403bdc1aada56f17794bf6129821a1158f5c1b09e06e6739abf2c3f8f0d434abdcda5c756e177d9b3626b94015d4af3c3a190
Known Plaintext:
Go
Found Seed length:
6
Found feedback coefficients:
111101
Found plaintext:
Go placidly amid the noise and the haste, and remember what peace there may be in silence.
```

The original plaintext was obtained just with the word `Go`.  

As shown above, the linear nature of LFSR compromises its security greatly and it can be "broken" with ease.