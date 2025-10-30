---
title: Understanding Modular Binomials in Cryptography
description: "An analysis of modular binomials and their implications. This articles gives an example of how algebraic structure can break secrecy."
image: images/post/understanding-modular-binomials-in-cryptography/thumbnail.png
authors:
  - Nithik R
date: 2025-10-30T12:57:18+05:30
categories:
  - Cryptography
tags:
  - Applied Mathematics
  - RSA
postType: featured
draft: false
---

In this article, I go over a toy model of modular binomials and try to demonstrate how algebraic structure or patterns in a cryptographic system can inherently break secrecy.  

---

Let's start by assuming a system where the ciphertexts $c_1$ and $c_2$ are defined as:
$$c_1 \equiv (a_1p + b_1q)^{e_1} \pmod{N}$$
$$c_2 \equiv (a_2p + b_2q)^{e_2} \pmod{N}$$
The values of $c_1,\ c_2,\ a_1,\ a_2,\ N$ are given and we have to recover the primes $p$ and $q$ where $N=pq$.

Raising $c_1$ to the power of $e_2$:
$$c_1^{e_2} \equiv (a_1p + b_1q)^{e_1e_2} \pmod{N}$$  
By binomial theorem,
$$c_1^{e_2} \equiv (a_1p)^{e_1e_2}+(a_1p)^{e_1e_2-1}(b_1q)+(a_1p)^{e_1e_2-2}(b_1q)^2+...+(b_1q)^{e_1e_2} \pmod{N}$$  
All terms except the first and last contain a factor of $pq$, and thus vanish modulo $N$:
$$\therefore c_1^{e_2} \equiv (a_1p)^{e_1e_2}+(b_1q)^{e_1e_2} \pmod{N}$$  
Multiplying $a_1^{-e_1e_2}$ on both sides:
$$a_1^{-e_1e_2} c_1^{e_2} \equiv a_1^{-e_1e_2}(a_1p)^{e_1e_2}+a_1^{-e_1e_2}(b_1q)^{e_1e_2} \pmod{N}$$
$$a_1^{-e_1e_2} c_1^{e_2} \equiv p^{e_1e_2}+a_1^{-e_1e_2}(b_1q)^{e_1e_2} \pmod{N}$$
Similarly,
$$a_2^{-e_1e_2} c_2^{e_1} \equiv p^{e_1e_2}+a_2^{-e_1e_2}(b_2q)^{e_1e_2} \pmod{N}$$
Subtracting these two congruences:
$$a_2^{-e_1e_2} c_2^{e_1} - a_1^{-e_1e_2} c_1^{e_2} \equiv q^{e_1e_2}((a_2^{-1}b_2)^{e_1e_2}-(a_1^{-1}b_1)^{e_1e_2}) \pmod{N}$$
This can be rewritten compactly as:
$$A \equiv q B \pmod{N}$$
$$A = qB + kN$$
$$A = q(B + kp)$$

Computing $\gcd(A,\ N)$:
$$\gcd(A,\ N) = \gcd(q(B+kp),\ pq)$$
$$\gcd(A,\ N) = q\ \gcd(B+kp,\ p)$$
If $B$ is coprime to $p$,  
$$\gcd(A,\ N) = q$$
$$\boxed{q = \gcd(a_2^{-e_1e_2} c_2^{e_1} - a_1^{-e_1e_2} c_1^{e_2},\ N)}$$

---

As demonstrated, finding the value of $q$ is straightforward. Once $q$ is known, we can apply a similar strategy to find $p$ or just do $p=\frac{N}{q}$.  

Obviously, in the real world, modular binomials of the kind described here will never be used in places where secrecy is required. However, if a predictable structure or pattern has crept into an implementation, due to some bug, negligence or poor design, it can most definitely be taken advantage of. This exercise shows that the existence of any kind of mathematical pattern in a cryptographic system can lead to it being exploited and be a threat to its efficacy at protecting information. 