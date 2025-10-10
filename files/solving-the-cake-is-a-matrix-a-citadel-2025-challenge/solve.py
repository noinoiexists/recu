#!/usr/bin/env python3
# exploit.py — minimal changes from your original, replace Sage with plain modular Gauss-Jordan

from pwn import *
import random
import string

HOST = "chall_citadel.cryptonitemit.in"
PORT = 54356
r = remote(HOST, PORT, level='debug')

# NOTE: this weee returns 56 bits per 8-byte string (drops MSB of each byte)
def weee(s):
    # for each character: take binary, zfill(8), then drop the MSB -> 7 bits per char
    return [int(x) for x in ''.join([bin(ord(i))[2:].zfill(8)[1:] for i in s])]

def rev_weee(s):
    # s: iterable of '0'/'1' (or ints 0/1) of length multiple of 7
    x = ''
    for i in range(0, len(s), 7):
        chunk = ''.join(str(int(bit)) for bit in s[i:i+7])
        x += chr(int(chunk, 2))
    return x

# --- network interaction (unchanged) ---
r.recvuntil(b'HERE HAVE CAKE:\r\n')
enc = eval(r.recvline().decode())   # list of 4 lists (each length 64)
out = []
codes = []

for i in range(56):
    r.recvuntil(b"Enter 8 bytes:\r\n")
    code = ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(8)])
    r.sendline(code.encode())
    r.recvuntil(b'have your cake:\r\n')
    val_line = r.recvline().strip().decode()
    out.append(eval(val_line))   # this is a list length 64
    codes.append(code)

r.recvuntil(b'PS. the prime is ')
p = int(r.recvline().strip().decode())

# Convert codes to 56-bit vectors (lists) using same ordering as server expects
codes_bits = [weee(code) for code in codes]  # list of 56 lists (each len 56)

# --- helper modular linear algebra (Gauss-Jordan) ---
def inv_mod(a, p):
    a %= p
    if a == 0:
        return None
    return pow(a, p-2, p)

def mat_mul(A, B, p):
    # A: r x m, B: m x c -> returns r x c
    r = len(A)
    m = len(A[0])
    assert m == len(B)
    c = len(B[0])
    C = [[0]*c for _ in range(r)]
    for i in range(r):
        for k in range(m):
            a = A[i][k] % p
            if a == 0:
                continue
            rowB = B[k]
            for j in range(c):
                C[i][j] = (C[i][j] + a * (rowB[j] % p)) % p
    return C

def gauss_jordan_square_inverse(A, p):
    # Invert a square matrix A (n x n) mod p. Returns inverse as list of rows.
    n = len(A)
    # build augmented [A | I]
    M = [ [(A[i][j] % p) for j in range(n)] + [1 if i==j else 0 for j in range(n)] for i in range(n) ]
    row = 0
    for col in range(n):
        # pivot search
        sel = None
        for i in range(row, n):
            if M[i][col] % p != 0:
                sel = i
                break
        if sel is None:
            raise ValueError("Matrix not invertible (pivot missing) — try again or use different queries.")
        if sel != row:
            M[row], M[sel] = M[sel], M[row]
        inv = inv_mod(M[row][col], p)
        assert inv is not None
        # normalize pivot row
        for j in range(col, 2*n):
            M[row][j] = (M[row][j] * inv) % p
        # eliminate other rows
        for i in range(n):
            if i == row:
                continue
            fac = M[i][col]
            if fac == 0:
                continue
            for j in range(col, 2*n):
                M[i][j] = (M[i][j] - fac * M[row][j]) % p
        row += 1
        if row == n:
            break
    # extract right half (inverse)
    Inv = [ row[n:] for row in M ]
    return Inv

def solve_rectangular(A, y, p):
    # Solve A * x = y (mod p), where A is R x C (R rows, C cols) and y length R.
    # We assume there exists unique solution (columns are independent); we use Gauss-Jordan on augmented matrix.
    R = len(A)
    C = len(A[0])
    # build augmented matrix M of size R x (C+1)
    M = [ [(A[i][j] % p) for j in range(C)] + [y[i] % p] for i in range(R) ]
    pivot_row_for_col = [-1] * C
    r = 0
    for c in range(C):
        sel = None
        for i in range(r, R):
            if M[i][c] % p != 0:
                sel = i
                break
        if sel is None:
            continue
        if sel != r:
            M[r], M[sel] = M[sel], M[r]
        inv = inv_mod(M[r][c], p)
        assert inv is not None
        # normalize
        for j in range(c, C+1):
            M[r][j] = (M[r][j] * inv) % p
        # eliminate other rows
        for i in range(R):
            if i == r:
                continue
            fac = M[i][c]
            if fac == 0:
                continue
            for j in range(c, C+1):
                M[i][j] = (M[i][j] - fac * M[r][j]) % p
        pivot_row_for_col[c] = r
        r += 1
        if r == R:
            break
    # check pivot coverage for all cols
    if any(pivot_row_for_col[c] == -1 for c in range(C)):
        # not full column rank -> no unique solution
        raise ValueError("Matrix does not have full column rank; can't uniquely solve.")
    # solution x[col] = M[pivot_row_for_col[col]][-1]
    x = [ M[pivot_row_for_col[c]][-1] % p for c in range(C) ]
    return x

# --- build matrices as lists-of-rows/cols consistent with our routines ---

# X: 56 x 56 matrix whose columns are the 56 code-vectors (codes_bits[j])
# We'll build X_rows (56 rows x 56 cols)
cols = 56
rows_out = 64

# form X as columns -> convert to rows representation
X_rows = [ [ codes_bits[col][row] % p for col in range(cols) ] for row in range(cols) ]  # 56 x 56

# form Y: 64 x 56 matrix whose columns are out[j] (each out[j] length 64)
Y_rows = [ [ out[col][row] % p for col in range(cols) ] for row in range(rows_out) ]  # 64 x 56

# invert X
X_inv = gauss_jordan_square_inverse(X_rows, p)   # returns 56 x 56 (rows)

# compute K_sub = Y * X_inv  (64 x 56) * (56 x 56) -> 64 x 56
K_sub = mat_mul(Y_rows, X_inv, p)  # 64 x 56

# Now for each printed enc (each is length 64) we solve K_sub * v = enc_vec (mod p) for v (56)
flag_inner = ''
for e in enc:
    y_vec = [int(x) % p for x in e]   # length 64
    # solve for v (length 56)
    v = solve_rectangular(K_sub, y_vec, p)   # returns list length 56
    # v should be 0/1 bits, coerce to ints 0/1
    bits = [int(int(x) % p) & 1 for x in v]
    flag_inner += rev_weee(bits)

flag = 'citadel{' + flag_inner + '}'
print(flag)
