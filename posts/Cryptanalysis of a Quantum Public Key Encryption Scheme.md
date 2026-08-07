---
title: Cryptanalysis of a Quantum Public Key Encryption Scheme
description: Cryptanalysis of a public key encryption scheme that uses a four-states quantum public key to encrypt a qubit message. This scheme was described in Zhixin Liu et al 2022 Phys. Scr. 97 045102
image: images/post/Cryptanalysis of a Quantum Public Key Encryption Scheme/thumbnail.png
authors:
  - Nithik R
date: 2026-08-07T23:56:30+05:30
categories:
  - Cryptography
  - Quantum Information
tags:
  - Linear Algebra
postType: featured
draft: false
---

I explain my cryptanalysis of a public key encryption scheme that uses a four-states quantum public key to encrypt a qubit message. This scheme was described in Zhixin Liu et al 2022 Phys. Scr. 97 [045102](https://doi.org/10.1088/1402-4896/ac576c)

---

## Introduction

We'll first try to understand the scheme described in the paper. As with most public key encryption schemes, there are two keys. A private key to decrypt data. A public key derived from the private key to encrypt data.

The private key ($K_p$) is classical and can take any one of four values. Which means it contains $log_2\ 4 = 2$ bits of information. $$K_p\in\{k_0,k_1,k_2,k_3\} $$
The public key ($K_\theta$) is a qubit prepared in one of four states, the eigenstates of the Pauli $X$ and $Y$ operators

$$|K_\theta\rangle=\tfrac{1}{\sqrt2}\big(|0\rangle+e^{i\theta}|1\rangle\big),\quad \theta\in\{0,\pi,\tfrac{\pi}{2},-\tfrac{\pi}{2}\}\ \leftrightarrow\ \{|+\rangle,|-\rangle,|{P_+}\rangle,|{P_-}\rangle\}$$

The public keys are generated from the private keys using these rules:
$$
\begin{array}{c|c|c}
\text{Private Key} & \text{Public Key} & \text{Notation} \\ \hline
k_0 &
\dfrac{1}{\sqrt2}|0\rangle+\dfrac{i}{\sqrt2}|1\rangle &
|P_+\rangle \\[1.2ex]
k_1 &
\dfrac{i}{\sqrt2}|0\rangle+\dfrac{1}{\sqrt2}|1\rangle &
|P_-\rangle \\[1.2ex]
k_2 &
\dfrac{1}{\sqrt2}|0\rangle+\dfrac{1}{\sqrt2}|1\rangle &
|+\rangle \\[1.2ex]
k_3 &
\dfrac{1}{\sqrt2}|0\rangle-\dfrac{1}{\sqrt2}|1\rangle &
|-\rangle
\end{array}
$$

The plaintext message is a qubit $|M\rangle=\alpha|0\rangle+\beta|1\rangle$. Here, $|\alpha|^2$ and $|\beta|^2$ give the probabilities of obtaining 0 and 1 respectively after measurement in the computational $Z$ basis and hence $|\alpha|^2 + |\beta|^2=1$.

#### Encryption.
The [CNOT](https://en.wikipedia.org/wiki/Controlled_NOT_gate) operation is done with public key qubit $|K_\theta\rangle$ as *control* and message $|M\rangle$ as *target*. The target is then measured in $Z$ basis and the outcome $m$ is published. The collapsed control wire is shipped as ciphertext $|M_{en}\rangle$.

The paper claims that this scheme is information-theoretically [secure](https://en.wikipedia.org/wiki/Information-theoretic_security), which I show is not true.

---

## The Flaw

First, I'll express the entire encryption scheme in a simpler way.

Define a matrix $R_\theta$ : $$R_\theta=
\begin{pmatrix}
1&0\\
0&e^{i\theta}
\end{pmatrix}$$
This is just a phase rotation operator.

Now, suppose the message is $|M\rangle=\alpha|0\rangle+\beta|1\rangle$.
The initial state is $$|K_\theta\rangle\otimes|M\rangle$$
$$= \tfrac{1}{\sqrt2}\big(|0\rangle+e^{i\theta}|1\rangle\big)\otimes \big(\alpha|0\rangle+\beta|1\rangle\big)$$
$$= \frac1{\sqrt2}  \left(  \alpha|00\rangle  +\beta|01\rangle  +\alpha e^{i\theta}|10\rangle  +\beta e^{i\theta}|11\rangle  \right)$$
Applying $\mathrm{CNOT}$ $|10\rangle\leftrightarrow|11\rangle$
$$\frac1{\sqrt2}  \left(  \alpha|00\rangle  +\beta|01\rangle  +\beta e^{i\theta}|10\rangle  +\alpha e^{i\theta}|11\rangle  \right)$$
Now, grouping by the second qubit  $$\frac1{\sqrt2}
\left[(\alpha|0\rangle+\beta e^{i\theta}|1\rangle)\otimes|0\rangle  + (\beta|0\rangle+\alpha e^{i\theta}|1\rangle)\otimes|1\rangle  \right]$$
Here, we observe that $$\alpha|0\rangle+\beta e^{i\theta}|1\rangle = R_\theta|M\rangle$$
and $$\beta|0\rangle+\alpha e^{i\theta}|1\rangle=R_\theta X|M\rangle$$
Therefore $$\boxed{  |K_\theta\rangle\otimes|M\rangle\xrightarrow{\text{CNOT}}  \frac1{\sqrt2}\left( R_\theta|M\rangle\otimes|0\rangle  +  R_\theta X|M\rangle\otimes|1\rangle \right)}$$

The protocol then measures the second qubit and publishes the result $m$.
If $m=0$ $$|M_{en}\rangle = R_\theta|M\rangle$$
if $m=1$ $$|M_{en}\rangle = R_\theta X|M\rangle$$

Therefore, generally
$$\boxed{|M_{en}\rangle = R_\theta X^m|M\rangle}$$

{{< block >}}
<strong>Theorem (Computational-Basis Population Preservation).</strong> <br>

Let the plaintext be
$$
|M\rangle=\alpha|0\rangle+\beta|1\rangle,
$$

and let the ciphertext be generated according to the protocol, with the published measurement outcome $m$.

Then the ciphertext uniquely determines the computational-basis probability distribution of the plaintext:
$$
\left(|\alpha|^2,\;|\beta|^2\right)
$$

<strong>Proof.</strong> From the previous derivation, we know
$$
|M_{en}\rangle=R_\theta X^m|M\rangle.
$$
The operator
$$
R_\theta=
\begin{pmatrix}
1 & 0\\
0 & e^{i\theta}
\end{pmatrix}
$$
is diagonal. Therefore it only changes the relative phase of the $|1\rangle$ component, leaving the magnitudes of the amplitudes unchanged.

If $m=0$, then

$$
|M_{en}\rangle
=
R_\theta|M\rangle
=
\alpha|0\rangle+\beta e^{i\theta}|1\rangle.
$$

Measuring in the computational $Z$ basis gives
$$
P(0)=|\alpha|^2,\qquad
P(1)=|\beta|^2.
$$

If $m=1$, then

$$
|M_{en}\rangle
=
R_\theta X|M\rangle
=
\beta|0\rangle+\alpha e^{i\theta}|1\rangle,
$$

Measuring in the computational $Z$ basis gives
$$
P(0)=|\beta|^2,\qquad
P(1)=|\alpha|^2.
$$

Since the value of $m$ is published as part of the ciphertext, an adversary knows whether this swap has occurred and can therefore reconstruct the original probability distribution

$$
\left(|\alpha|^2,\;|\beta|^2\right).
$$

Hence, the computational-basis probability distribution of the plaintext is completely preserved by the ciphertext. $\qquad\blacksquare$
{{< /block >}}

The paper makes the mistake of assuming that measuring the target qubit destroys the plaintext. However, after $\mathrm{CNOT}$, the quantum information of the message lies in the control qubit. Measurement does *not* destroy the information encoded in the control qubit.  

Since the ciphertext uniquely determines the computational-basis probability distribution of the plaintext, an adversary can extract non-trivial information about the message without knowing the private key. An information-theoretically secure encryption scheme must reveal no information whatsoever about the plaintext from the ciphertext alone. This scheme therefore fails to achieve information-theoretic security.

---

This analysis highlights the value of reducing a protocol to its simplest mathematical form before attempting to reason about its security.