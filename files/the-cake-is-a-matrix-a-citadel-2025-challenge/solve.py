

from pwn import *
import random
import string

r = remote(HOST, PORT, level='debug')

def weee(s):
    return [int(x) for x in ''.join([bin(ord(i))[2:].zfill(8)[1:] for i in s])]

def rev_weee(s):
    x = ''
    for i in range(0, len(s), 7):
        chunk = ''.join(str(int(bit)) for bit in s[i:i+7])
        x += chr(int(chunk, 2))
    return x

r.recvuntil(b'HERE HAVE CAKE:\r\n')
enc = eval(r.recvline().decode())
out = []
codes = []

for i in range(56):
    r.recvuntil(b"Enter 8 bytes:\r\n")
    code = ''.join([random.choice(string.ascii_letters + string.digits) for _ in range(8)])
    r.sendline(code.encode())
    r.recvuntil(b'have your cake:\r\n')
    val_line = r.recvline().strip().decode()
    out.append(eval(val_line))
    codes.append(code)

r.recvuntil(b'PS. the prime is ')
p = int(r.recvline().strip().decode())

codes_bits = [weee(code) for code in codes]


def inv_mod(a, p):
    a %= p
    if a == 0:
        return None
    return pow(a, p-2, p)

def mat_mul(A, B, p):

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

    n = len(A)

    M = [ [(A[i][j] % p) for j in range(n)] + [1 if i==j else 0 for j in range(n)] for i in range(n) ]
    row = 0
    for col in range(n):

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

        for j in range(col, 2*n):
            M[row][j] = (M[row][j] * inv) % p

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

    Inv = [ row[n:] for row in M ]
    return Inv

def solve_rectangular(A, y, p):

    R = len(A)
    C = len(A[0])

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
        for j in range(c, C+1):
            M[r][j] = (M[r][j] * inv) % p
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
    if any(pivot_row_for_col[c] == -1 for c in range(C)):
        raise ValueError("Matrix does not have full column rank; can't uniquely solve.")
    x = [ M[pivot_row_for_col[c]][-1] % p for c in range(C) ]
    return x


cols = 56
rows_out = 64

X_rows = [ [ codes_bits[col][row] % p for col in range(cols) ] for row in range(cols) ]

Y_rows = [ [ out[col][row] % p for col in range(cols) ] for row in range(rows_out) ]

X_inv = gauss_jordan_square_inverse(X_rows, p)

K_sub = mat_mul(Y_rows, X_inv, p)

flag_inner = ''
for e in enc:
    y_vec = [int(x) % p for x in e]
    v = solve_rectangular(K_sub, y_vec, p)
    bits = [int(int(x) % p) & 1 for x in v]
    flag_inner += rev_weee(bits)

flag = 'citadel{' + flag_inner + '}'
print(flag)
