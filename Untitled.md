
This identity is the **entire encryption algorithm written in one equation**. Once you understand it, the whole paper becomes much simpler.

Let's build it from scratch.

---

## Step 1. What is (R_\theta)?

They define

[  
R_\theta=\operatorname{diag}(1,e^{i\theta}).  
]

"diag" means **diagonal matrix**.

So

[  
R_\theta=  
\begin{pmatrix}  
1&0\  
0&e^{i\theta}  
\end{pmatrix}.  
]

---

## Step 2. What does it do?

Apply it to an arbitrary qubit

[  
|\psi\rangle=\alpha|0\rangle+\beta|1\rangle.  
]

Since the matrix is diagonal,

# [  
R_\theta|\psi\rangle

\alpha|0\rangle+\beta e^{i\theta}|1\rangle.  
]

Notice:

- the amplitude of (|0\rangle) is unchanged,
    
- the amplitude of (|1\rangle) is multiplied by (e^{i\theta}).
    

It is **just a phase rotation**.

---

## Step 3. Why introduce (R_\theta)?

Because every public key can now be written with one formula.

Recall

# [  
|K_\theta\rangle

\frac{|0\rangle+e^{i\theta}|1\rangle}{\sqrt2}.  
]

But

# [  
|+\rangle

\frac{|0\rangle+|1\rangle}{\sqrt2}.  
]

Applying (R_\theta),

# [  
R_\theta|+\rangle

# \frac{|0\rangle+e^{i\theta}|1\rangle}{\sqrt2}

|K_\theta\rangle.  
]

So the four public keys are simply

[  
\boxed{|K_\theta\rangle=R_\theta|+\rangle.}  
]

This is why (R_\theta) is introduced—it lets us treat all four keys uniformly instead of analyzing four separate cases.

---

## Step 4. The identity

Suppose the message is

[  
|\psi\rangle=\alpha|0\rangle+\beta|1\rangle.  
]

The initial state is

[  
|K_\theta\rangle\otimes|\psi\rangle.  
]

Since

# [  
|K_\theta\rangle

\frac{|0\rangle+e^{i\theta}|1\rangle}{\sqrt2},  
]

the state is

[  
\frac1{\sqrt2}  
\left(  
\alpha|00\rangle  
+\beta|01\rangle  
+\alpha e^{i\theta}|10\rangle  
+\beta e^{i\theta}|11\rangle  
\right).  
]

Apply CNOT:

[  
|10\rangle\leftrightarrow|11\rangle.  
]

So we get

[  
\frac1{\sqrt2}  
\left(  
\alpha|00\rangle  
+\beta|01\rangle  
+\beta e^{i\theta}|10\rangle  
+\alpha e^{i\theta}|11\rangle  
\right).  
]

Now group by the **second qubit**:

# [

\frac1{\sqrt2}  
\left[  
(\alpha|0\rangle+\beta e^{i\theta}|1\rangle)\otimes|0\rangle  
+  
(\beta|0\rangle+\alpha e^{i\theta}|1\rangle)\otimes|1\rangle  
\right].  
]

But

# [  
\alpha|0\rangle+\beta e^{i\theta}|1\rangle

R_\theta|\psi\rangle,  
]

and

# [  
\beta|0\rangle+\alpha e^{i\theta}|1\rangle

R_\theta X|\psi\rangle.  
]

Therefore

[  
\boxed{  
|K_\theta\rangle\otimes|\psi\rangle  
\xrightarrow{\text{CNOT}}  
\frac1{\sqrt2}  
\left(  
R_\theta|\psi\rangle\otimes|0\rangle  
+  
R_\theta X|\psi\rangle\otimes|1\rangle  
\right).  
}  
]

---

This is why Claude called it **"the identity that makes it work."**

Everything after this follows immediately:

- If the measurement result is (m=0), the first branch survives:  
    [  
    R_\theta|\psi\rangle.  
    ]
    
- If (m=1), the second branch survives:  
    [  
    R_\theta X|\psi\rangle.  
    ]
    

Combining both cases,

[  
\boxed{|M_{en}\rangle=R_\theta X^m|\psi\rangle.}  
]

That single equation replaces all eight rows of the paper's decryption table. It's not a new protocol—it's a much more compact mathematical description of the same one.