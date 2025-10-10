---
title: The Cake is a Matrix – a CitadelCTF 2025 Challenge
description: My writeup for the CitadelCTF 2025 challenge, “The Cake is a Matrix”, by Cryptonite, MIT Manipal.
image: images/post/the-cake-is-a-matrix-a-citadel-2025-challenge/thumbnail.png
authors:
  - Nithik R
date: 2025-10-10T17:30:28+05:30
categories:
  - Cryptography
  - CTFs
tags:
  - Applied Mathematics
  - Linear Algebra
  - Cryptonite
postType: featured
draft: false
---

In this writeup I'll go through my thought process and solution for the challenge “The Cake is a Matrix,” which was a part of the CitadelCTF 2025 by [Cryptonite](https://cryptonitemit.in). This challenge was created by [goosbo](https://github.com/goosbo).

---

## Problem Statement

> You enter this floor to find a vast dining hall, sterile and impossibly clean. At the head of the table sits a towering mechanical guardian, cables coiled like a throne, her single glowing eye fixed on you. 
On her plate there seems to be a matrix of symbols masquerading as dessert that are generated from a program beside her. Her voice floats across the hall, sweet and mocking: *“Go on… eat. I insist. The cake is… well, something else entirely.”* Maybe by deciphering the matrix, you might unlock the key to the next floor?
[server.py](https://github.com/noinoiexists/recu/blob/main/files/solving-the-cake-is-a-matrix-a-citadel-2025-challenge/server.py)

---

## Understanding the Setup

The server imports a $FLAG$ from an inaccessible location which is probably the flag we have to find. It strips off the prefix `citadel{` and the trailing `}` and sets $flag$ to be the 32-byte string remaining. 

It generates a random 128-bit prime number $p$ and then generates a 64x64 matrix $key$ which is made up of random entries from the integer ring $\mathbb{Z}_{p}$.

The function $weee(s)$ converts an 8-byte string $s$ to its corresponding binary representation in the form of an array, resulting in a 64-element vector.

The function $multiply(key,\ x)$ computes $key * x\ (mod\ p)$ where x is that 64-element vector.

The server splits the 32-byte $flag$ into 4 blocks (let's call them $subflag_i$ ) of 8 bytes each. Then it computes $enc_i = multiply(key,\ weee(subflag_i))$ for $i=0,\ 1,\ 2,\ 3$. $enc$ is the set of all $enc_i$. On connecting to the server, we receive this $enc$.

Then it allows input of an 8-byte strings $s$ and outputs $multiply(key,\ weee(s))$. This can be done a maximum of 56 times. Finally it also gives the value of $p$ used.

---

## The Exploit
We know that $enc_i \equiv key * weee(subflag_i)\ \ (mod\ p)$, which means that to find $weee(subflag_i)$ we need to find $key^{-1}$. After that, to obtain $subflag_i$ we just need to reverse $weee$, which is relatively easy.

In general a 64×64 matrix needs 64 independent columns to invert; but since flag plaintexts occupy only a 56-dimensional subspace (MSBs fixed), we cannot find $key^{-1}$.

However, we notice that for typical ASCII characters, when expressed in 8-bits, the MSB (most significant bit) is 0. This is an interesting observation as this means that when the function $weee$ expands the 8-byte string to 64 bits, 8 of the bits are fixed to be 0. We just need to find the inverse of $key$ restricted within this subspace.

The server lets us input 56 queries which is exactly the dimension of the subspace. We can apply [Gauss Jordan Elimination](https://en.wikipedia.org/wiki/Gaussian_elimination#Finding_the_inverse_of_a_matrix) with these 56 sets of outputs to find the inverse of $key$.

Once we have the inverse, $weee(subflag_i)\equiv key^{-1}*enc_i \ \ (mod\ p)$. Then we just reverse $weee$ by representing the 64 bits as 8 bytes and put together the four $subflag$s to obtain $flag$.

The python code for this solution can be found [here](https://github.com/noinoiexists/recu/blob/main/files/solving-the-cake-is-a-matrix-a-citadel-2025-challenge/solve.py).

---

The final flag is `citadel{7h3_m4tr1x_i5_4_li3_4nd_50_wa5_1}`