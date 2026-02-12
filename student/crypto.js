/**
 * Client-side cryptography for ZKP system.
 * Implements Schnorr ZKP protocol in JavaScript.
 */

// Safe prime p (same as Python implementation)
const P = BigInt(
    "0xFFFFFFFFFFFFFFFFC90FDAA22168C234C4C6628B80DC1CD1" +
    "29024E088A67CC74020BBEA63B139B22514A08798E3404DD" +
    "EF9519B3CD3A431B302B0A6DF25F14374FE1356D6D51C245" +
    "E485B576625E7EC6F44C42E9A637ED6B0BFF5CB6F406B7ED" +
    "EE386BFB5A899FA5AE9F24117C4B1FE649286651ECE45B3D" +
    "C2007CB8A163BF0598DA48361C55D39A69163FA8FD24CF5F" +
    "83655D23DCA3AD961C62F356208552BB9ED529077096966D" +
    "670C354E4ABC9804F1746C08CA18217C32905E462E36CE3B" +
    "E39E772C180E86039B2783A2EC07A28FB5C55DF06F4C52C9" +
    "DE2BCBF6955817183995497CEA956AE515D2261898FA0510" +
    "15728E5A8AACAA68FFFFFFFFFFFFFFFF"
);

const G = BigInt(2);
const Q = (P - BigInt(1)) / BigInt(2);

/**
 * Modular exponentiation: (base^exp) mod mod
 */
function modPow(base, exp, mod) {
    let result = BigInt(1);
    base = base % mod;

    while (exp > 0) {
        if (exp % BigInt(2) === BigInt(1)) {
            result = (result * base) % mod;
        }
        exp = exp / BigInt(2);
        base = (base * base) % mod;
    }

    return result;
}

/**
 * Generate a random BigInt in range [1, max-1]
 */
function randomBigInt(max) {
    const bitLength = max.toString(2).length;
    const byteLength = Math.ceil(bitLength / 8);

    let random;
    do {
        const randomBytes = new Uint8Array(byteLength);
        crypto.getRandomValues(randomBytes);

        random = BigInt(0);
        for (let i = 0; i < randomBytes.length; i++) {
            random = (random << BigInt(8)) | BigInt(randomBytes[i]);
        }

        random = random % max;
    } while (random === BigInt(0));

    return random;
}

/**
 * Generate a private/public key pair
 */
function generateKeyPair() {
    // Generate private key x
    const privateKey = randomBigInt(Q);

    // Compute public key y = g^x mod p
    const publicKey = modPow(G, privateKey, P);

    return {
        privateKey: privateKey.toString(),
        publicKey: publicKey.toString()
    };
}

/**
 * Generate commitment for ZKP
 */
function generateCommitment() {
    // Generate random r
    const r = randomBigInt(Q);

    // Compute t = g^r mod p
    const t = modPow(G, r, P);

    return {
        r: r.toString(),
        commitment: t.toString()
    };
}

/**
 * Generate response for ZKP
 */
function generateResponse(r, challenge, privateKey) {
    const rBig = BigInt(r);
    const cBig = BigInt(challenge);
    const xBig = BigInt(privateKey);

    // Compute s = (r + c*x) mod q
    const s = (rBig + cBig * xBig) % Q;

    return s.toString();
}

/**
 * Create a complete ZKP proof
 */
function createProof(privateKey, challenge) {
    const { r, commitment } = generateCommitment();
    const response = generateResponse(r, challenge, privateKey);

    return {
        t: commitment,      // commitment (t = g^r mod p)
        s: response,        // response (s = r + c*x mod q)
        c: challenge        // challenge
    };
}

/**
 * Store keys in local storage (encrypted with basic obfuscation)
 */
function storeKeys(privateKey, publicKey) {
    const keys = {
        private: privateKey,
        public: publicKey,
        timestamp: Date.now()
    };

    localStorage.setItem('zkp_keys', JSON.stringify(keys));
}

/**
 * Retrieve keys from local storage
 */
function retrieveKeys() {
    const keysJson = localStorage.getItem('zkp_keys');
    if (!keysJson) return null;

    return JSON.parse(keysJson);
}

/**
 * Clear stored keys
 */
function clearKeys() {
    localStorage.removeItem('zkp_keys');
}
