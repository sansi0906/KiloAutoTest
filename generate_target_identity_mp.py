import hashlib
import time
import multiprocessing
import os
from Crypto.PublicKey import ECC
from Crypto.Random import get_random_bytes
from Crypto.Cipher import Salsa20

ZT_IDENTITY_GEN_MEMORY = 2 * 1024 * 1024
TARGET_NODEID = "411dbed5ae"
TARGET_INT = int(TARGET_NODEID, 16)

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

def worker(queue, process_id):
    attempts = 0
    valid_count = 0
    
    while True:
        pub, priv = GenerateKeys()
        digest = ComputeHash(pub)
        
        attempts += 1
        
        if check_hash(digest):
            valid_count += 1
            address = get_address(digest)
            address_int = int.from_bytes(address, 'big')
            
            if address_int == TARGET_INT:
                queue.put({
                    'found': True,
                    'address': address,
                    'public_key': pub,
                    'private_key': priv,
                    'attempts': attempts,
                    'process_id': process_id
                })
                return
            
            if attempts % 100 == 0:
                queue.put({
                    'found': False,
                    'process_id': process_id,
                    'attempts': attempts,
                    'valid_count': valid_count
                })

def main():
    num_processes = multiprocessing.cpu_count()
    print(f"Starting with {num_processes} processes...")
    
    queue = multiprocessing.Queue()
    processes = []
    
    for i in range(num_processes):
        p = multiprocessing.Process(target=worker, args=(queue, i))
        processes.append(p)
        p.start()
        print(f"Process {i} started")
    
    start_time = time.time()
    total_attempts = 0
    total_valid = 0
    
    while True:
        try:
            result = queue.get(timeout=5)
            
            if result['found']:
                elapsed = time.time() - start_time
                print(f"\nFound by process {result['process_id']}!")
                print(f"Total attempts across all processes: {total_attempts + result['attempts']}")
                print(f"Time elapsed: {elapsed:.2f} seconds")
                print(f"\nidentity.public:\n{result['address'].hex()}:0:{result['public_key'].hex()}")
                print(f"\nidentity.secret:\n{result['address'].hex()}:0:{result['public_key'].hex()}:{result['private_key'].hex()}")
                
                with open('e:\\KiloAutoTest\\identity.public', 'w') as f:
                    f.write(f"{result['address'].hex()}:0:{result['public_key'].hex()}")
                
                with open('e:\\KiloAutoTest\\identity.secret', 'w') as f:
                    f.write(f"{result['address'].hex()}:0:{result['public_key'].hex()}:{result['private_key'].hex()}")
                
                print("\nFiles saved to:")
                print("e:\\KiloAutoTest\\identity.public")
                print("e:\\KiloAutoTest\\identity.secret")
                
                for p in processes:
                    p.terminate()
                
                return
            else:
                total_attempts += result['attempts']
                total_valid += result['valid_count']
                elapsed = time.time() - start_time
                rate = total_attempts / elapsed if elapsed > 0 else 0
                print(f"Progress: {total_attempts} attempts, {total_valid} valid keys, {rate:.1f} attempts/sec")
                
        except Exception as e:
            elapsed = time.time() - start_time
            rate = total_attempts / elapsed if elapsed > 0 else 0
            print(f"Progress: {total_attempts} attempts, {rate:.1f} attempts/sec")

if __name__ == '__main__':
    main()