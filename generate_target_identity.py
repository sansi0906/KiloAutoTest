import hashlib
import time
from Crypto.PublicKey import ECC
from Crypto.Random import get_random_bytes
from Crypto.Cipher import Salsa20

ZT_IDENTITY_GEN_MEMORY = 2 * 1024 * 1024

TARGET_NODEID = "411dbed5ae"

def get_address(digest):
    address = 0
    for i in range(59, 64):
        address <<= 8
        address |= digest[i]
    return address.to_bytes(5, 'big')

def check_hash(hash):
    if len(hash) != 64:
        return False
    if hash[0] > 17:
        return False
    if hash[59] == 0xFF:
        return False
    return True

def ComputeHash(public_key):
    digest = bytearray(hashlib.sha512(public_key).digest())
    genmem = bytearray(ZT_IDENTITY_GEN_MEMORY)
    key = bytes(digest[:32])
    nonce = bytes(digest[32:40])
    
    cipher = Salsa20.new(key=key, nonce=nonce)
    
    genmem[0:64] = cipher.encrypt(genmem[0:64])
    
    for i in range(64, ZT_IDENTITY_GEN_MEMORY, 64):
        k = i - 64
        genmem[i:i+64] = genmem[k:k+64]
        genmem[i:i+64] = cipher.encrypt(genmem[i:i+64])
    
    total_words = ZT_IDENTITY_GEN_MEMORY // 8
    i = 0
    
    while i < total_words:
        idx1 = int.from_bytes(genmem[i*8:(i+1)*8], "big") % 8
        i += 1
        
        idx2 = int.from_bytes(genmem[i*8:(i+1)*8], "big") % total_words
        i += 1
        
        idx1 *= 8
        idx2 *= 8
        
        tmp = genmem[idx2:idx2+8]
        genmem[idx2:idx2+8] = digest[idx1:idx1+8]
        digest[idx1:idx1+8] = tmp
        
        digest[:] = cipher.encrypt(bytes(digest))
    
    return bytes(digest)

def GenerateKeys():
    ed_private_key = ECC.generate(curve='Ed25519')
    ed_public_key = ed_private_key.public_key()
    
    ed_private_bytes = ed_private_key.d.to_bytes(32, 'big')
    ed_public_bytes = ed_public_key.pointQ.x.to_bytes(32, 'big')
    
    x_private_bytes = get_random_bytes(32)
    x_private_key = ECC.construct(seed=x_private_bytes, curve="Curve25519")
    x_public_key = x_private_key.public_key()
    x_public_bytes = x_public_key.pointQ.x.to_bytes(32, 'big')
    
    public_key = ed_public_bytes + x_public_bytes
    private_key = ed_private_bytes + x_private_bytes
    
    return public_key, private_key

target = TARGET_NODEID
target_int = int(target, 16)

log_file = open('e:\\KiloAutoTest\\generation_progress.log', 'w')

log_file.write(f"Target NodeID: {target}\n")
log_file.write(f"Target integer: {target_int}\n")
log_file.write("Starting brute-force generation...\n")
log_file.flush()

start_time = time.time()
attempts = 0
valid_count = 0
last_log_time = start_time

while True:
    pub, priv = GenerateKeys()
    digest = ComputeHash(pub)
    
    attempts += 1
    
    if check_hash(digest):
        valid_count += 1
        address = get_address(digest)
        address_int = int.from_bytes(address, 'big')
        
        if address_int == target_int:
            elapsed = time.time() - start_time
            log_file.write(f"\nFound! After {attempts} attempts ({elapsed:.2f} seconds)\n")
            log_file.write(f"\nidentity.public:\n{address.hex()}:0:{pub.hex()}\n")
            log_file.write(f"\nidentity.secret:\n{address.hex()}:0:{pub.hex()}:{priv.hex()}\n")
            log_file.flush()
            
            with open('e:\\KiloAutoTest\\identity.public', 'w') as f:
                f.write(f"{address.hex()}:0:{pub.hex()}")
            
            with open('e:\\KiloAutoTest\\identity.secret', 'w') as f:
                f.write(f"{address.hex()}:0:{pub.hex()}:{priv.hex()}")
            
            log_file.write("\nFiles saved to:\n")
            log_file.write("e:\\KiloAutoTest\\identity.public\n")
            log_file.write("e:\\KiloAutoTest\\identity.secret\n")
            log_file.flush()
            log_file.close()
            break
    
    current_time = time.time()
    if current_time - last_log_time >= 10:
        elapsed = current_time - start_time
        rate = attempts / elapsed if elapsed > 0 else 0
        log_file.write(f"Progress: {attempts} attempts, {valid_count} valid keys, {rate:.1f} attempts/sec\n")
        log_file.flush()
        last_log_time = current_time