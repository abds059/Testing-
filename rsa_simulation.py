import secrets
import random

# ----- Sieve of Eratosthenes -----
def sieve(limit):
    if limit < 2:
        return []
    arr = bytearray(b'\x01') * (limit + 1)
    arr[0:2] = b'\x00\x00'
    for p in range(2, int(limit ** 0.5) + 1):
        if arr[p]:
            arr[p*p : limit+1 : p] = b'\x00' * ((limit - p*p)//p + 1)
    return [i for i, isprime in enumerate(arr) if isprime]

# ----- Miller-Rabin -----
def is_probable_prime(n, k=12):
    if n < 2:
        return False
    small_primes = [2,3,5,7,11,13,17,19,23,29]
    for p in small_primes:
        if n % p == 0:
            return n == p
    d = n - 1
    s = 0
    while d % 2 == 0:
        d //= 2
        s += 1
    for _ in range(k):
        a = secrets.randbelow(n - 3) + 2
        x = pow(a, d, n)
        if x == 1 or x == n - 1:
            continue
        for _ in range(s - 1):
            x = pow(x, 2, n)
            if x == n - 1:
                break
        else:
            return False
    return True

# ----- RSA Class -----
class RSA:
    def __init__(self, p, q, e=65537):
        if not (is_probable_prime(p) and is_probable_prime(q)):
            raise ValueError("Both p and q must be prime.")
        if p == q:
            raise ValueError("p and q must be distinct primes.")
        self.p = p
        self.q = q
        self.n = p * q
        self.phi = (p-1)*(q-1)
        self.e = e
        self.d = self.mod_inverse(e, self.phi)

    def mod_inverse(self, a, m):
        m0 = m
        x0, x1 = 0, 1
        if m == 1:
            return 0
        while a > 1:
            q = a // m
            a, m = m, a % m
            x0, x1 = x1 - q*x0, x0
        if x1 < 0:
            x1 += m0
        return x1

    def encrypt(self, plaintext):
        if not plaintext.isalnum():
            raise ValueError("Plaintext must be alphanumeric (no spaces or special chars).")
        return " ".join([str(pow(ord(c), self.e, self.n)) for c in plaintext])

    def decrypt(self, ciphertext):
        parts = ciphertext.strip().split()
        if not all(p.isdigit() for p in parts):
            raise ValueError("Ciphertext must be numbers separated by spaces.")
        nums = list(map(int, parts))
        return "".join([chr(pow(c, self.d, self.n)) for c in nums])
