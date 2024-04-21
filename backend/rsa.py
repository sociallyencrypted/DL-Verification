import random

def gcd(a, b):
    while b:
        a, b = b, a % b
    return a

def mod_inv(a, m):
    for x in range(1, m):
        if (a*x) % m == 1:
            return x
    return None

def generate_prime(bits):

    while True:
        # Generate a random odd number with the specified number of bits.
        p = random.getrandbits(bits)
        if p % 2 == 0:
            p += 1
        
        # Test for primality using the Miller-Rabin test.
        if is_prime(p):
            return p

def is_prime(n):
    if n <= 1:
        return False
    elif n <= 3:
        return True
    elif n % 2 == 0 or n % 3 == 0:
        return False
    i = 5
    while i*i <= n:
        if n % i == 0 or n % (i+2) == 0:
            return False
        i += 6
    return True

def generate_primes(n_bits):
    while True:
        p = random.getrandbits(n_bits)
        if is_prime(p):
            return p

def encrypt(plaintext, public_key):
    n, e = public_key
    ciphertext = [ pow((ord(char)),e) % n for char in plaintext]
    return ciphertext

def decrypt(ciphertext, private_key):
    n, d = private_key
    plaintext = [chr(pow((char), d) % n) for char in ciphertext]
    return ''.join(plaintext)

def gen_keys(p,q):
    n = p * q
    phi = (p - 1) * (q - 1)

    e = random.randrange(1, phi)
    while gcd(e, phi) != 1:
        e = random.randrange(1, phi)

    #  d the modular inverse of e
    d = mod_inv(e, phi)

    # public n priv  keys
    public_key = (n, e)
    private_key = (n, d)
    return(public_key,private_key)

def main():
    p = generate_primes(7)
    q = generate_primes(7)
    print(p,q)

    n = p * q
    phi = (p - 1) * (q - 1)

    e = random.randrange(1, phi)
    while gcd(e, phi) != 1:
        e = random.randrange(1, phi)

    #  d the modular inverse of e
    d = mod_inv(e, phi)

    # public n priv  keys
    public_key = (n, e)
    private_key = (n, d)
    print('Public key:', public_key)
    print('Private key:', private_key)

    plaintext = 'RSA Test'
    ciphertext = encrypt(plaintext, public_key)
    decrypted_plaintext = decrypt(ciphertext, private_key)
    print('Plaintext:', plaintext)
    print('Ciphertext:', ciphertext)
    print('Decrypted plaintext:', decrypted_plaintext)

if __name__ == '__main__':
    main()