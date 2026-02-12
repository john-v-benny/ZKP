/**
 * Student application logic
 */

const ISSUER_URL = 'http://localhost:5001';
const VERIFIER_URL = 'http://localhost:5002';

let currentKeys = null;
let currentCredential = null;

// Initialize on page load
document.addEventListener('DOMContentLoaded', () => {
    // Check if keys already exist
    const storedKeys = retrieveKeys();
    if (storedKeys) {
        currentKeys = storedKeys;
        displayKeys();
    }

    // Set up event listeners
    document.getElementById('generateKeysBtn').addEventListener('click', handleGenerateKeys);
    document.getElementById('requestCredentialBtn').addEventListener('click', handleRequestCredential);
    document.getElementById('applyScholarshipBtn').addEventListener('click', handleApplyScholarship);
});

/**
 * Handle key generation
 */
function handleGenerateKeys() {
    const btn = document.getElementById('generateKeysBtn');
    btn.disabled = true;
    btn.textContent = 'Generating...';

    try {
        // Generate keys
        const keys = generateKeyPair();
        currentKeys = keys;

        // Store keys
        storeKeys(keys.privateKey, keys.publicKey);

        // Display keys
        displayKeys();

        btn.textContent = 'Regenerate Keys';
    } catch (error) {
        showStatus('keysDisplay', 'Error generating keys: ' + error.message, 'error');
    } finally {
        btn.disabled = false;
    }
}

/**
 * Display generated keys
 */
function displayKeys() {
    const display = document.getElementById('keysDisplay');
    const publicKeyDisplay = document.getElementById('publicKeyDisplay');

    publicKeyDisplay.textContent = currentKeys.publicKey;
    display.classList.remove('hidden');
}

/**
 * Handle credential request
 */
async function handleRequestCredential() {
    const studentId = document.getElementById('studentId').value.trim();
    const studentName = document.getElementById('studentName').value.trim();

    if (!studentId || !studentName) {
        showStatus('credentialStatus', 'Please enter both Student ID and Name', 'error');
        return;
    }

    if (!currentKeys) {
        showStatus('credentialStatus', 'Please generate keys first (Step 1)', 'error');
        return;
    }

    const btn = document.getElementById('requestCredentialBtn');
    btn.disabled = true;
    btn.textContent = 'Processing...';

    try {
        // Step 1: Verify identity
        showStatus('credentialStatus', 'Verifying identity...', 'info');

        const verifyResponse = await fetch(`${ISSUER_URL}/verify-identity`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                student_id: studentId,
                name: studentName
            })
        });

        const verifyData = await verifyResponse.json();

        if (!verifyData.verified) {
            showStatus('credentialStatus', 'Identity verification failed. Please check your credentials.', 'error');
            return;
        }

        // Step 2: Bind public key
        showStatus('credentialStatus', 'Binding public key...', 'info');

        const bindResponse = await fetch(`${ISSUER_URL}/bind-key`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                student_id: studentId,
                name: studentName,
                public_key: currentKeys.publicKey
            })
        });

        const bindData = await bindResponse.json();

        if (!bindData.success) {
            showStatus('credentialStatus', 'Key binding failed: ' + bindData.message, 'error');
            return;
        }

        // Step 3: Request credential
        showStatus('credentialStatus', 'Requesting credential...', 'info');

        const credResponse = await fetch(`${ISSUER_URL}/issue-credential`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                student_id: studentId,
                public_key: currentKeys.publicKey
            })
        });

        const credData = await credResponse.json();

        if (!credData.success) {
            showStatus('credentialStatus', 'Credential issuance failed', 'error');
            return;
        }

        currentCredential = credData;

        // Step 4: Register credential with verifier
        showStatus('credentialStatus', 'Registering with scholarship system...', 'info');

        const registerResponse = await fetch(`${VERIFIER_URL}/register-credential`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                student_id: studentId,
                credential: credData.credential,
                signature: credData.signature
            })
        });

        const registerData = await registerResponse.json();

        if (registerData.success) {
            showStatus('credentialStatus',
                '✓ Credential obtained and registered successfully! You can now apply for scholarships.',
                'success');
        } else {
            showStatus('credentialStatus', 'Credential registration failed', 'error');
        }

    } catch (error) {
        showStatus('credentialStatus', 'Error: ' + error.message, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Request Credential';
    }
}

/**
 * Handle scholarship application
 */
async function handleApplyScholarship() {
    if (!currentKeys) {
        showStatus('scholarshipStatus', 'Please generate keys first (Step 1)', 'error');
        return;
    }

    if (!currentCredential) {
        showStatus('scholarshipStatus', 'Please request credential first (Step 2)', 'error');
        return;
    }

    const studentId = document.getElementById('studentId').value.trim();
    if (!studentId) {
        showStatus('scholarshipStatus', 'Please enter your Student ID', 'error');
        return;
    }

    const btn = document.getElementById('applyScholarshipBtn');
    btn.disabled = true;
    btn.textContent = 'Processing...';

    try {
        // Step 1: Request challenge
        showStatus('scholarshipStatus', 'Requesting verification challenge...', 'info');

        const challengeResponse = await fetch(`${VERIFIER_URL}/request-challenge`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                student_id: studentId
            })
        });

        const challengeData = await challengeResponse.json();

        if (!challengeData.challenge) {
            showStatus('scholarshipStatus', 'Failed to get challenge: ' + (challengeData.error || 'Unknown error'), 'error');
            return;
        }

        // Step 2: Generate ZKP proof
        showStatus('scholarshipStatus', 'Generating zero-knowledge proof...', 'info');

        const proof = createProof(currentKeys.privateKey, challengeData.challenge);

        // Step 3: Submit proof and check eligibility
        showStatus('scholarshipStatus', 'Verifying proof and checking eligibility...', 'info');

        const eligibilityResponse = await fetch(`${VERIFIER_URL}/check-eligibility`, {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                session_id: challengeData.session_id,
                student_id: studentId,
                proof: proof
            })
        });

        const eligibilityData = await eligibilityResponse.json();

        // Display result
        if (eligibilityData.eligible) {
            let message = `<strong>🎉 Congratulations!</strong><br>`;
            message += `Decision: <strong>${eligibilityData.decision}</strong><br>`;
            message += `<br><strong>Reasons:</strong><br>`;
            eligibilityData.reasons.forEach(reason => {
                message += `✓ ${reason}<br>`;
            });
            showStatus('scholarshipStatus', message, 'success');
        } else {
            let message = `<strong>Application Result</strong><br>`;
            message += `Decision: <strong>${eligibilityData.decision}</strong><br>`;
            message += `<br><strong>Reasons:</strong><br>`;
            eligibilityData.reasons.forEach(reason => {
                message += `• ${reason}<br>`;
            });
            showStatus('scholarshipStatus', message, 'error');
        }

    } catch (error) {
        showStatus('scholarshipStatus', 'Error: ' + error.message, 'error');
    } finally {
        btn.disabled = false;
        btn.textContent = 'Apply for Scholarship';
    }
}

/**
 * Show status message
 */
function showStatus(elementId, message, type) {
    const element = document.getElementById(elementId);
    element.innerHTML = `<div class="status ${type}">${message}</div>`;
}
