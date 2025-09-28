---
title: "Bit Flip Cipher: My First Attempt at Making a Cipher"
description: A simple symmetric cipher I built for fun using SHA-256 and XOR, and why it’s definitely not secure.
image: images/post/Bit Flip Cipher/thumbnail.jpg
authors:
  - Nithik R
date: 2025-09-28T15:00:00+05:30
categories:
  - Cryptography
tags:
  - XOR
  - Stream Cipher
  - SHA-256
postType: featured
draft: false
---

A few months back, I found myself with an idea: *what if I tried making my own cipher, just for fun?* I hadn’t studied cryptography at all at that point, but I wanted to see how far I could go. That’s how **Bit Flip Cipher** came into existence.  

It’s a symmetric cipher that flips bits using a SHA-256 hash derived from a key, with XOR. The output is encoded in Base64 to keep it readable. It was never meant to be secure, but it taught me a lot about how ciphers are constructed, and broken. Today, I thought I’d write it down here to document my early attempts at cryptography.

---

## How the Cipher Works

At its heart, Bit Flip Cipher is very simple. Here’s how I designed it:

#### Encryption
1. The user provides a key (a password) and the text to encrypt.
2. A SHA-256 hash of the key is generated.
3. Each byte of the text is XOR-ed with the corresponding byte from the hash, wrapping around the hash when needed.
4. The result is then encoded in Base64 to make it printable.

#### Decryption
Decryption is the reverse process, and because XOR is symmetric, the same key can undo the encryption:
1. The user provides the key and the Base64 ciphertext.
2. The Base64 ciphertext is decoded back to the XORed form.
3. The SHA-256 hash of the key is generated.
4. XOR the encrypted bytes with the hash again.

---

## Why I Built It

I just wanted to see if I could come up with a scheme that “looked” like encryption. Only later did I realise that this is extremely weak: it has predictable patterns, and is vulnerable to all sorts of attacks.  

Still, making it gave me a feel for how stream ciphers work: taking a key, stretching it into something longer, and combining it with the message through XOR. Even though my version is broken by design, the exercise itself made me curious about stronger, real-world cryptography. I also learnt more about packaging software for linux and C in general.

---

## Weaknesses and Attacks

- **Frequency Analysis:** Since the main idea of this cipher is to XOR a 32-byte long hash in a repeating fashion, every 32 bytes, the character is encrypted using the same byte. If the original plaintext was just an English text, the statistical properties of the language itself are not hidden well enough by this cipher and we can apply frequency analysis on the sets of bytes of positions $i$, $i+32$, $i+64 ...$
- **Keystream Reuse**: Encrypting multiple messages with the same key always produces the same keystream. XORing two ciphertexts together cancels out the keystream and reveals relationships between the plaintexts. 
- **Short Keystream Length**: With only 32 bytes before repeating, the cipher leaks structure very quickly compared to modern ciphers whose keystreams *effectively* never repeat.

There are definitely more ways to break this cipher than I have listed here.

---

## Implementation

I packaged this cipher as a small CLI tool called `bflip`. It takes a key and either encrypts or decrypts depending on the flag passed.

Examples:
```sh
bflip -k secretkey 'hello world'
bflip -d -k secretkey 'BASE64_ENCODED_TEXT'
```

I even made a `.deb` package for easier installation. Compiling from the source is straightforward too.  

The source and installation details are available on my GitHub [repository](https://github.com/noinoiexists/Bit-Flip-Cipher).

---

Bit Flip Cipher is a beginner experiment. It is naive but meaningful. I wouldn’t recommend anyone to use it, but I realise it’s a great way to get hands-on experience and gain a better perspective on cryptography. That’s why I decided to write about it now, months after creating it.