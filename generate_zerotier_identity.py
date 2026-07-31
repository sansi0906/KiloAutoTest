import hashlib
import struct
import os
from cryptography.hazmat.primitives.asymmetric.ed25519 import Ed25519PrivateKey

ZT_IDENTITY_GEN_MEMORY = 2097152
ZT_IDENTITY_GEN_HASHCASH_FIRST_BYTE_LESS_THAN = 17

def salsa20_quarter_round(state, a, b, c, d):
    state[a] = (state[a] + state[b]) & 0xffffffff
    state[d] ^= ((state[a] << 7) | (state[a] >> (32 - 7))) & 0xffffffff
    state[c] = (state[c] + state[d]) & 0xffffffff
    state[b] ^= ((state[c] << 9) | (state[c] >> (32 - 9))) & 0xffffffff
    state[a] = (state[a] + state[b]) & 0xffffffff
    state[d] ^= ((state[a] << 13) | (state[a] >> (32 - 13))) & 0xffffffff
    state[c] = (state[c] + state[d]) & 0xffffffff
    state[b] ^= ((state[c] << 18) | (state[c] >> (32 - 18))) & 0xffffffff

def salsa20_block(key, iv, counter):
    constants = b"expand 32-byte k"
    
    state = [0] * 16
    state[0] = struct.unpack('<I', constants[0:4])[0]
    state[1] = struct.unpack('<I', key[0:4])[0]
    state[2] = struct.unpack('<I', key[4:8])[0]
    state[3] = struct.unpack('<I', key[8:12])[0]
    state[4] = struct.unpack('<I', key[12:16])[0]
    state[5] = struct.unpack('<I', constants[4:8])[0]
    state[6] = struct.unpack('<I', iv[0:4])[0]
    state[7] = struct.unpack('<I', iv[4:8])[0]
    state[8] = counter & 0xffffffff
    state[9] = (counter >> 32) & 0xffffffff
    state[10] = struct.unpack('<I', constants[8:12])[0]
    state[11] = struct.unpack('<I', key[16:20])[0]
    state[12] = struct.unpack('<I', key[20:24])[0]
    state[13] = struct.unpack('<I', key[24:28])[0]
    state[14] = struct.unpack('<I', key[28:32])[0]
    state[15] = struct.unpack('<I', constants[12:16])[0]
    
    x = state[:]
    
    for _ in range(10):
        salsa20_quarter_round(x, 0, 4, 8, 12)
        salsa20_quarter_round(x, 5, 9, 13, 1)
        salsa20_quarter_round(x, 10, 14, 2, 6)
        salsa20_quarter_round(x, 15, 3, 7, 11)
        salsa20_quarter_round(x, 0, 1, 2, 3)
        salsa20_quarter_round(x, 5, 6, 7, 4)
        salsa20_quarter_round(x, 10, 11, 8, 9)
        salsa20_quarter_round(x, 15, 12, 13, 14)
    
    result = bytearray(64)
    for i in range(16):
        struct.pack_into('<I', result, i * 4, (state[i] + x[i]) & 0xffffffff)
    
    return bytes(result)

def ntoh64(val):
    return struct.unpack('>Q', struct.pack('<Q', val))[0]

def compute_memory_hard_hash(public_key):
    digest = bytearray(hashlib.sha512(public_key).digest())
    
    genmem = bytearray(ZT_IDENTITY_GEN_MEMORY)
    key = bytes(digest[:32])
    iv = bytes(digest[32:40])
    
    counter = 0
    s20_output = salsa20_block(key, iv, counter)
    counter += 1
    genmem[:64] = s20_output
    
    for i in range(64, ZT_IDENTITY_GEN_MEMORY, 64):
        for j in range(8):
            val = struct.unpack('<Q', genmem[i - 64 + j * 8:i - 64 + (j + 1) * 8])[0]
            struct.pack_into('<Q', genmem, i + j * 8, val)
        
        s20_output = salsa20_block(key, iv, counter)
        counter += 1
        for j in range(64):
            genmem[i + j] ^= s20_output[j]
    
    for i in range(0, ZT_IDENTITY_GEN_MEMORY // 8, 2):
        val1 = struct.unpack('<Q', genmem[i * 8:(i + 1) * 8])[0]
        idx1 = ntoh64(val1) % (64 // 8)
        
        val2 = struct.unpack('<Q', genmem[(i + 1) * 8:(i + 2) * 8])[0]
        idx2 = ntoh64(val2) % (ZT_IDENTITY_GEN_MEMORY // 8)
        
        tmp = struct.unpack('<Q', genmem[idx2 * 8:(idx2 + 1) * 8])[0]
        val_digest = struct.unpack('<Q', digest[idx1 * 8:(idx1 + 1) * 8])[0]
        struct.pack_into('<Q', genmem, idx2 * 8, val_digest)
        struct.pack_into('<Q', digest, idx1 * 8, tmp)
        
        s20_output = salsa20_block(key, iv, counter)
        counter += 1
        for j in range(64):
            digest[j] ^= s20_output[j]
    
    return bytes(digest)

def generate_identity(target_nodeid):
    target = int(target_nodeid, 16)
    attempts = 0
    
    while True:
        private_key = Ed25519PrivateKey.generate()
        public_key = private_key.public_key().public_bytes_raw()
        
        digest = compute_memory_hard_hash(public_key)
        
        if digest[0] >= ZT_IDENTITY_GEN_HASHCASH_FIRST_BYTE_LESS_THAN:
            continue
        
        last_5_bytes = digest[59:64]
        address_int = struct.unpack('>Q', last_5_bytes + b'\x00\x00\x00')[0]
        node_id = address_int
        
        if node_id == target:
            private_bytes = private_key.private_bytes_raw()
            
            identity_public = f"{target_nodeid}:0:{public_key.hex()}"
            identity_secret = f"{target_nodeid}:0:{public_key.hex()}:{private_bytes.hex()}"
            
            return {
                'public_key': public_key,
                'private_key': private_bytes,
                'identity_public': identity_public,
                'identity_secret': identity_secret
            }
        
        attempts += 1
        if attempts % 10000 == 0:
            print(f"Attempts: {attempts}, Current NodeID: {format(node_id, '010x')}")

target_nodeid = "411dbed5ae"
print(f"Generating ZeroTier identity with NodeID: {target_nodeid}")
print("This may take a long time...")

result = generate_identity(target_nodeid)

print("\nSuccess! Generated identity files:")
print(f"\nidentity.public:\n{result['identity_public']}")
print(f"\nidentity.secret:\n{result['identity_secret']}")

with open('e:\\KiloAutoTest\\identity.public', 'w') as f:
    f.write(result['identity_public'])

with open('e:\\KiloAutoTest\\identity.secret', 'w') as f:
    f.write(result['identity_secret'])

print("\nFiles saved to:")
print("e:\\KiloAutoTest\\identity.public")
print("e:\\KiloAutoTest\\identity.secret")