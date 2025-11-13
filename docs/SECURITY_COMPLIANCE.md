# Security & Compliance Guide for ML Systems

## Table of Contents

1. [Introduction](#introduction)
2. [Security Threat Model](#security-threat-model)
3. [Authentication & Authorization](#authentication--authorization)
4. [Data Security](#data-security)
5. [Model Security](#model-security)
6. [Infrastructure Security](#infrastructure-security)
7. [Privacy & Compliance](#privacy--compliance)
8. [Security Monitoring](#security-monitoring)
9. [Incident Response](#incident-response)
10. [Compliance Frameworks](#compliance-frameworks)
11. [Security Checklist](#security-checklist)

---

## 1. Introduction

ML systems face unique security challenges beyond traditional applications:
- **Adversarial attacks**: Manipulating inputs to fool models
- **Model extraction**: Stealing model through API queries
- **Data poisoning**: Corrupting training data
- **Privacy leakage**: Models remembering training data
- **Bias and fairness**: Discriminatory predictions

This guide provides comprehensive security and compliance practices for production ML systems.

---

## 2. Security Threat Model

### 2.1 Attack Surface Analysis

```
ML System Attack Surface:

┌─────────────────────────────────────────────────────────────┐
│                    Data Collection Layer                     │
│  Threats: Data poisoning, PII leakage, backdoors           │
└────────────────────────┬────────────────────────────────────┘
                        │
┌────────────────────────▼────────────────────────────────────┐
│                   Training Pipeline Layer                    │
│  Threats: Malicious code injection, supply chain attacks   │
└────────────────────────┬────────────────────────────────────┘
                        │
┌────────────────────────▼────────────────────────────────────┐
│                    Model Storage Layer                       │
│  Threats: Model theft, unauthorized access, tampering      │
└────────────────────────┬────────────────────────────────────┘
                        │
┌────────────────────────▼────────────────────────────────────┐
│                  Inference API Layer                         │
│  Threats: Adversarial inputs, DDoS, API abuse              │
└────────────────────────┬────────────────────────────────────┘
                        │
┌────────────────────────▼────────────────────────────────────┐
│                   Monitoring Layer                           │
│  Threats: Log injection, metric manipulation               │
└─────────────────────────────────────────────────────────────┘
```

### 2.2 Threat Categories

#### A. Training-Time Attacks

**1. Data Poisoning**
```python
# Attack: Inject malicious training samples
# Goal: Degrade model or create backdoors

class DataPoisoningDefense:
    """
    Defend against data poisoning attacks.

    Techniques:
    - Outlier detection
    - Data provenance tracking
    - Robust training algorithms
    - Data validation
    """

    def detect_poisoned_samples(self, training_data):
        """Detect suspicious training samples."""

        # 1. Statistical outlier detection
        outliers = self.detect_statistical_outliers(training_data)

        # 2. Check data provenance
        suspicious = self.check_provenance(training_data)

        # 3. Consistency checks
        inconsistent = self.check_consistency(training_data)

        # 4. Cross-validation with holdout
        # Train on subsets, check if sample impacts model significantly
        influential_samples = self.detect_influential_samples(training_data)

        return {
            'outliers': outliers,
            'suspicious_provenance': suspicious,
            'inconsistent': inconsistent,
            'influential': influential_samples
        }

    def robust_training(self, X, y):
        """Train model robust to outliers."""
        # Use robust loss functions (Huber loss)
        # Use RANSAC or similar robust estimators
        # Downweight outliers automatically
        pass
```

**2. Model Backdoors**
```python
# Attack: Inject trigger that causes misclassification
# Example: Specific pixel pattern causes wrong prediction

class BackdoorDefense:
    """Detect and prevent model backdoors."""

    def scan_for_backdoors(self, model, test_data):
        """Scan model for potential backdoors."""

        # 1. Check for universal triggers
        triggers = self.generate_trigger_candidates()

        for trigger in triggers:
            # Test if trigger causes consistent misclassification
            poisoned_data = self.apply_trigger(test_data, trigger)
            predictions = model.predict(poisoned_data)

            # If >90% flip to specific class, likely backdoor
            if self.check_suspicious_pattern(predictions):
                alert(f"Potential backdoor detected with trigger: {trigger}")

    def neuron_analysis(self, model):
        """Analyze neuron activations for backdoors."""
        # Backdoors often use specific neurons
        # Check for neurons with unusual activation patterns
        pass
```

#### B. Inference-Time Attacks

**1. Adversarial Examples**
```python
class AdversarialDefense:
    """
    Defend against adversarial examples.

    Attack Types:
    - FGSM (Fast Gradient Sign Method)
    - PGD (Projected Gradient Descent)
    - C&W (Carlini & Wagner)
    - DeepFool
    """

    def detect_adversarial(self, input_data, model):
        """Detect adversarial inputs."""

        # 1. Input validation
        if not self.validate_input_range(input_data):
            return True, "Out of expected range"

        # 2. Check prediction confidence
        prediction, confidence = model.predict_proba(input_data)
        if confidence < 0.5:
            return True, "Low confidence"

        # 3. Consistency checking
        # Add small random noise and check if prediction changes drastically
        noisy_inputs = [input_data + np.random.normal(0, 0.01, input_data.shape)
                       for _ in range(10)]
        noisy_predictions = [model.predict(x) for x in noisy_inputs]

        # If predictions vary wildly, likely adversarial
        if np.std(noisy_predictions) > 0.3:
            return True, "Unstable predictions"

        return False, "Clean input"

    def input_transformation(self, input_data):
        """
        Transform input to remove adversarial perturbations.

        Techniques:
        - JPEG compression
        - Bit depth reduction
        - Spatial smoothing
        - Random resizing and padding
        """
        # These transformations often remove adversarial perturbations
        # while preserving benign inputs

        transformed = self.jpeg_compress(input_data, quality=75)
        transformed = self.spatial_smooth(transformed, kernel_size=3)

        return transformed

    def ensemble_defense(self, input_data, models):
        """Use ensemble of models for robustness."""
        # Adversarial examples often don't transfer well
        predictions = [model.predict(input_data) for model in models]

        # If models disagree, likely adversarial
        if len(set(predictions)) > 1:
            return "Suspicious input"

        return predictions[0]
```

**2. Model Extraction**
```python
class ModelExtractionDefense:
    """
    Prevent model theft through API queries.

    Attack: Query model many times to replicate it
    Defense: Rate limiting, query analysis, noise injection
    """

    def __init__(self):
        self.query_tracker = {}
        self.MAX_QUERIES_PER_USER = 10000
        self.QUERY_WINDOW_HOURS = 24

    def check_suspicious_queries(self, user_id, query_pattern):
        """Detect model extraction attempts."""

        # 1. Track queries per user
        queries = self.query_tracker.get(user_id, [])
        queries.append(query_pattern)

        # 2. Check for systematic querying patterns
        if self.is_systematic_querying(queries):
            alert(f"Suspicious query pattern from user {user_id}")
            return False  # Reject query

        # 3. Check query volume
        recent_queries = self.get_recent_queries(user_id, hours=24)
        if len(recent_queries) > self.MAX_QUERIES_PER_USER:
            alert(f"Rate limit exceeded for user {user_id}")
            return False

        return True

    def is_systematic_querying(self, queries):
        """Detect systematic/grid-like queries."""
        # Attackers often query in grid pattern or systematically
        # explore input space

        # Check if queries form a grid
        # Check if queries are evenly spaced
        # Check if queries cover input space systematically

        pass

    def add_prediction_noise(self, prediction, noise_level=0.01):
        """Add small noise to prevent exact model extraction."""
        noise = np.random.normal(0, noise_level)
        return prediction + noise

    def watermark_model(self, model):
        """Add watermark to detect stolen models."""
        # Add specific behavior on trigger inputs
        # If stolen model exhibits same behavior, can prove theft
        pass
```

---

## 3. Authentication & Authorization

### 3.1 API Authentication

**OAuth 2.0 + JWT Implementation:**

```python
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from jose import JWTError, jwt
from passlib.context import CryptContext
from datetime import datetime, timedelta
from typing import Optional

# Configuration
SECRET_KEY = "your-secret-key-here"  # Load from environment!
ALGORITHM = "HS256"
ACCESS_TOKEN_EXPIRE_MINUTES = 30

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")


class User(BaseModel):
    """User model."""
    username: str
    email: Optional[str] = None
    full_name: Optional[str] = None
    disabled: Optional[bool] = None
    roles: List[str] = []


class Token(BaseModel):
    """Token model."""
    access_token: str
    token_type: str


class AuthManager:
    """
    Authentication and authorization manager.

    Features:
    - Password hashing (bcrypt)
    - JWT token generation
    - Token validation
    - Role-based access control (RBAC)
    """

    def verify_password(self, plain_password: str, hashed_password: str) -> bool:
        """Verify password against hash."""
        return pwd_context.verify(plain_password, hashed_password)

    def get_password_hash(self, password: str) -> str:
        """Hash password."""
        return pwd_context.hash(password)

    def create_access_token(self, data: dict, expires_delta: Optional[timedelta] = None):
        """Create JWT access token."""
        to_encode = data.copy()

        if expires_delta:
            expire = datetime.utcnow() + expires_delta
        else:
            expire = datetime.utcnow() + timedelta(minutes=15)

        to_encode.update({"exp": expire})
        encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

        return encoded_jwt

    async def get_current_user(self, token: str = Depends(oauth2_scheme)) -> User:
        """Get current user from token."""
        credentials_exception = HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
            username: str = payload.get("sub")
            if username is None:
                raise credentials_exception

        except JWTError:
            raise credentials_exception

        user = self.get_user(username)
        if user is None:
            raise credentials_exception

        return user

    def check_permission(self, user: User, resource: str, action: str) -> bool:
        """Check if user has permission for action on resource."""

        # Define permission mapping
        permissions = {
            "admin": ["predict", "train", "deploy", "delete"],
            "data_scientist": ["predict", "train", "view"],
            "api_user": ["predict", "view"]
        }

        # Check if any user role has required permission
        for role in user.roles:
            if action in permissions.get(role, []):
                return True

        return False


# Usage in API
auth_manager = AuthManager()

@app.post("/predict")
async def predict(
    request: PredictionRequest,
    current_user: User = Depends(auth_manager.get_current_user)
):
    """Protected prediction endpoint."""

    # Check permissions
    if not auth_manager.check_permission(current_user, "model", "predict"):
        raise HTTPException(status_code=403, detail="Permission denied")

    # Make prediction
    prediction = model.predict(request.features)

    # Audit log
    audit_log(
        user=current_user.username,
        action="predict",
        resource="model",
        timestamp=datetime.utcnow()
    )

    return prediction
```

### 3.2 API Key Management

```python
class APIKeyManager:
    """
    Manage API keys for programmatic access.

    Features:
    - Generate API keys
    - Rotate keys
    - Revoke keys
    - Track usage
    """

    def generate_api_key(self, user_id: str, description: str) -> str:
        """Generate new API key."""
        import secrets

        # Generate cryptographically secure random key
        api_key = f"ml_{secrets.token_urlsafe(32)}"

        # Store in database
        self.store_api_key(
            api_key=api_key,
            user_id=user_id,
            description=description,
            created_at=datetime.utcnow(),
            expires_at=datetime.utcnow() + timedelta(days=90)
        )

        return api_key

    def validate_api_key(self, api_key: str) -> Optional[str]:
        """Validate API key and return user_id."""
        key_data = self.get_api_key(api_key)

        if not key_data:
            return None

        # Check if expired
        if key_data['expires_at'] < datetime.utcnow():
            return None

        # Check if revoked
        if key_data['revoked']:
            return None

        # Track usage
        self.track_api_key_usage(api_key)

        return key_data['user_id']

    def rotate_api_key(self, old_api_key: str) -> str:
        """Rotate API key (create new, revoke old after grace period)."""
        # Get user
        user_id = self.validate_api_key(old_api_key)

        if not user_id:
            raise ValueError("Invalid API key")

        # Generate new key
        new_key = self.generate_api_key(user_id, "Rotated key")

        # Schedule old key revocation (7 day grace period)
        self.schedule_revocation(old_api_key, days=7)

        return new_key
```

### 3.3 Rate Limiting

```python
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.util import get_remote_address
from slowapi.errors import RateLimitExceeded

limiter = Limiter(key_func=get_remote_address)

class RateLimiter:
    """
    Advanced rate limiting for API protection.

    Strategies:
    - Fixed window: N requests per time window
    - Sliding window: Smooth rate limiting
    - Token bucket: Allow bursts
    - Adaptive: Adjust based on system load
    """

    @limiter.limit("100/minute")
    @app.post("/predict")
    async def predict(request: PredictionRequest):
        """Rate-limited prediction endpoint."""
        pass

    def adaptive_rate_limit(self, user_tier: str, system_load: float):
        """Adjust rate limits based on user tier and system load."""

        base_limits = {
            "free": 100,
            "pro": 1000,
            "enterprise": 10000
        }

        base_limit = base_limits[user_tier]

        # Reduce limits under high load
        if system_load > 0.8:
            return int(base_limit * 0.5)
        elif system_load > 0.6:
            return int(base_limit * 0.75)

        return base_limit
```

---

## 4. Data Security

### 4.1 Encryption

**Data at Rest:**

```python
from cryptography.fernet import Fernet

class DataEncryption:
    """
    Encrypt sensitive data at rest.

    Use cases:
    - PII in training data
    - Model artifacts
    - API keys and secrets
    """

    def __init__(self):
        # Load key from secure key management service
        self.key = self.load_encryption_key()
        self.cipher = Fernet(self.key)

    def encrypt_data(self, data: bytes) -> bytes:
        """Encrypt data."""
        return self.cipher.encrypt(data)

    def decrypt_data(self, encrypted_data: bytes) -> bytes:
        """Decrypt data."""
        return self.cipher.decrypt(encrypted_data)

    def encrypt_dataframe(self, df: pd.DataFrame, pii_columns: List[str]) -> pd.DataFrame:
        """Encrypt PII columns in DataFrame."""
        df = df.copy()

        for col in pii_columns:
            df[col] = df[col].apply(
                lambda x: self.encrypt_data(str(x).encode()).decode()
            )

        return df

    def load_encryption_key(self):
        """Load encryption key from secure storage."""
        # In production: Use AWS KMS, Azure Key Vault, HashiCorp Vault
        # NEVER hardcode keys!

        import os
        key = os.environ.get('ENCRYPTION_KEY')

        if not key:
            raise ValueError("ENCRYPTION_KEY not set!")

        return key.encode()
```

**Data in Transit:**

```python
# Force HTTPS for all API endpoints
from fastapi.middleware.httpsredirect import HTTPSRedirectMiddleware

app.add_middleware(HTTPSRedirectMiddleware)

# TLS configuration
ssl_config = {
    "ssl_keyfile": "/path/to/key.pem",
    "ssl_certfile": "/path/to/cert.pem",
    "ssl_version": ssl.PROTOCOL_TLSv1_2,  # Minimum TLS 1.2
    "ssl_ciphers": "ECDHE+AESGCM",  # Strong ciphers only
}

# Run with TLS
uvicorn.run(
    app,
    host="0.0.0.0",
    port=443,
    **ssl_config
)
```

### 4.2 PII Handling

```python
class PIIHandler:
    """
    Handle personally identifiable information (PII) securely.

    PII Types:
    - Direct: SSN, email, phone
    - Quasi: Age, ZIP code, gender (can identify when combined)
    - Sensitive: Health info, financial data
    """

    def identify_pii(self, df: pd.DataFrame) -> Dict[str, List[str]]:
        """Automatically identify PII columns."""
        pii_columns = {
            'email': [],
            'phone': [],
            'ssn': [],
            'credit_card': [],
            'ip_address': []
        }

        for col in df.columns:
            # Check column name
            if any(keyword in col.lower() for keyword in ['email', 'e-mail']):
                pii_columns['email'].append(col)

            # Check data patterns
            sample = df[col].dropna().astype(str).head(100)

            if sample.str.match(r'\d{3}-\d{2}-\d{4}').mean() > 0.8:
                pii_columns['ssn'].append(col)

            if sample.str.match(r'\d{3}-\d{3}-\d{4}').mean() > 0.8:
                pii_columns['phone'].append(col)

        return {k: v for k, v in pii_columns.items() if v}

    def anonymize_data(self, df: pd.DataFrame, method: str = 'hash') -> pd.DataFrame:
        """
        Anonymize PII data.

        Methods:
        - Hash: One-way hash (can't reverse)
        - Mask: Replace with ***
        - Generalize: Age 34 → Age range 30-40
        - Suppress: Remove entirely
        """
        df = df.copy()
        pii_columns = self.identify_pii(df)

        for pii_type, columns in pii_columns.items():
            for col in columns:
                if method == 'hash':
                    df[col] = df[col].apply(self.hash_value)
                elif method == 'mask':
                    df[col] = '***REDACTED***'
                elif method == 'generalize':
                    df[col] = df[col].apply(self.generalize_value)
                elif method == 'suppress':
                    df = df.drop(columns=[col])

        return df

    def hash_value(self, value: str) -> str:
        """One-way hash for anonymization."""
        import hashlib
        return hashlib.sha256(str(value).encode()).hexdigest()

    def implement_differential_privacy(self, df: pd.DataFrame, epsilon: float = 1.0):
        """
        Add differential privacy to data.

        Differential Privacy: Mathematical guarantee that individual
        records cannot be identified from aggregated data.

        epsilon: Privacy budget (smaller = more privacy)
        """
        # Add calibrated noise to preserve privacy
        for col in df.select_dtypes(include=[np.number]).columns:
            sensitivity = df[col].max() - df[col].min()
            scale = sensitivity / epsilon

            noise = np.random.laplace(0, scale, size=len(df))
            df[col] = df[col] + noise

        return df
```

### 4.3 Data Access Control

```python
class DataAccessControl:
    """
    Control access to sensitive data.

    Principles:
    - Least privilege: Minimum access needed
    - Need-to-know: Access only required data
    - Separation of duties: No single person has full access
    - Audit trail: Log all access
    """

    def __init__(self):
        self.access_policies = {}
        self.audit_log = []

    def grant_access(self, user: str, dataset: str, permissions: List[str]):
        """Grant user access to dataset."""
        self.access_policies[user] = self.access_policies.get(user, {})
        self.access_policies[user][dataset] = permissions

        self.audit_log.append({
            'action': 'grant_access',
            'user': user,
            'dataset': dataset,
            'permissions': permissions,
            'timestamp': datetime.utcnow()
        })

    def check_access(self, user: str, dataset: str, operation: str) -> bool:
        """Check if user has access for operation on dataset."""
        user_policies = self.access_policies.get(user, {})
        dataset_permissions = user_policies.get(dataset, [])

        has_access = operation in dataset_permissions

        # Log access check
        self.audit_log.append({
            'action': 'check_access',
            'user': user,
            'dataset': dataset,
            'operation': operation,
            'granted': has_access,
            'timestamp': datetime.utcnow()
        })

        return has_access

    def list_data_access(self, dataset: str) -> List[Dict]:
        """List all users with access to dataset."""
        users_with_access = []

        for user, policies in self.access_policies.items():
            if dataset in policies:
                users_with_access.append({
                    'user': user,
                    'permissions': policies[dataset]
                })

        return users_with_access
```

---

## 5. Model Security

### 5.1 Model Integrity

```python
class ModelIntegrityChecker:
    """
    Ensure model hasn't been tampered with.

    Techniques:
    - Cryptographic hashing
    - Digital signatures
    - Checksum verification
    """

    def compute_model_hash(self, model_path: str) -> str:
        """Compute SHA-256 hash of model file."""
        import hashlib

        sha256 = hashlib.sha256()

        with open(model_path, 'rb') as f:
            while chunk := f.read(8192):
                sha256.update(chunk)

        return sha256.hexdigest()

    def sign_model(self, model_path: str, private_key_path: str) -> str:
        """Digitally sign model."""
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding

        # Load private key
        with open(private_key_path, 'rb') as f:
            private_key = serialization.load_pem_private_key(
                f.read(),
                password=None
            )

        # Compute hash
        model_hash = self.compute_model_hash(model_path)

        # Sign hash
        signature = private_key.sign(
            model_hash.encode(),
            padding.PSS(
                mgf=padding.MGF1(hashes.SHA256()),
                salt_length=padding.PSS.MAX_LENGTH
            ),
            hashes.SHA256()
        )

        return signature.hex()

    def verify_model(self, model_path: str, signature: str, public_key_path: str) -> bool:
        """Verify model signature."""
        from cryptography.hazmat.primitives import hashes, serialization
        from cryptography.hazmat.primitives.asymmetric import padding

        # Load public key
        with open(public_key_path, 'rb') as f:
            public_key = serialization.load_pem_public_key(f.read())

        # Compute current hash
        model_hash = self.compute_model_hash(model_path)

        # Verify signature
        try:
            public_key.verify(
                bytes.fromhex(signature),
                model_hash.encode(),
                padding.PSS(
                    mgf=padding.MGF1(hashes.SHA256()),
                    salt_length=padding.PSS.MAX_LENGTH
                ),
                hashes.SHA256()
            )
            return True
        except Exception:
            return False
```

### 5.2 Model Access Control

```python
class ModelAccessControl:
    """
    Control who can access and use models.

    Policies:
    - Read: View model metadata
    - Predict: Use model for inference
    - Train: Retrain model
    - Deploy: Promote to production
    - Delete: Remove model
    """

    def __init__(self):
        self.policies = {}

    def check_model_access(self, user: str, model_id: str, action: str) -> bool:
        """Check if user can perform action on model."""

        # Get user roles
        user_roles = self.get_user_roles(user)

        # Define role permissions
        role_permissions = {
            'viewer': ['read', 'predict'],
            'data_scientist': ['read', 'predict', 'train'],
            'ml_engineer': ['read', 'predict', 'train', 'deploy'],
            'admin': ['read', 'predict', 'train', 'deploy', 'delete']
        }

        # Check if any role has permission
        for role in user_roles:
            if action in role_permissions.get(role, []):
                # Log access
                self.log_model_access(user, model_id, action, granted=True)
                return True

        # Log denied access
        self.log_model_access(user, model_id, action, granted=False)
        return False
```

---

## 6. Infrastructure Security

### 6.1 Container Security

```yaml
# Dockerfile security best practices

FROM python:3.9-slim  # Use specific versions, not 'latest'

# Run as non-root user
RUN useradd -m -u 1000 mluser
USER mluser

# Copy only necessary files
COPY --chown=mluser:mluser requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Set read-only filesystem (where possible)
COPY --chown=mluser:mluser --chmod=755 src/ /app/

# Drop capabilities
USER mluser
WORKDIR /app

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import requests; requests.get('http://localhost:8000/health')"

# Security scanning
# Run: docker scan ml-pipeline-api
# Run: trivy image ml-pipeline-api
```

### 6.2 Network Security

```yaml
# docker-compose.yml network security

version: '3.8'

services:
  model-api:
    networks:
      - public  # Exposed to internet
      - private  # Internal only

  mlflow:
    networks:
      - private  # Not exposed to internet

  postgres:
    networks:
      - private  # Not exposed to internet

networks:
  public:
    driver: bridge
  private:
    driver: bridge
    internal: true  # No internet access
```

### 6.3 Secrets Management

```python
class SecretsManager:
    """
    Manage secrets securely.

    DO NOT:
    - Hardcode secrets in code
    - Commit secrets to Git
    - Log secrets
    - Pass secrets in URLs

    DO:
    - Use environment variables (development)
    - Use secrets management service (production)
    - Rotate secrets regularly
    - Encrypt secrets at rest
    """

    def __init__(self, provider='environment'):
        self.provider = provider

        if provider == 'aws':
            import boto3
            self.client = boto3.client('secretsmanager')
        elif provider == 'azure':
            from azure.keyvault.secrets import SecretClient
            self.client = SecretClient(...)
        elif provider == 'vault':
            import hvac
            self.client = hvac.Client(url='http://vault:8200')

    def get_secret(self, secret_name: str) -> str:
        """Retrieve secret from secure storage."""

        if self.provider == 'environment':
            import os
            secret = os.environ.get(secret_name)

            if not secret:
                raise ValueError(f"Secret {secret_name} not found!")

            return secret

        elif self.provider == 'aws':
            response = self.client.get_secret_value(SecretId=secret_name)
            return response['SecretString']

        # ... other providers

    def rotate_secret(self, secret_name: str):
        """Rotate secret (generate new value)."""
        # Generate new secret
        # Update in secrets manager
        # Update applications
        # Revoke old secret after grace period
        pass
```

---

## 7. Privacy & Compliance

### 7.1 GDPR Compliance

```python
class GDPRCompliance:
    """
    Ensure GDPR compliance for EU data.

    Key Requirements:
    - Right to access: Users can request their data
    - Right to erasure: Users can request deletion
    - Right to portability: Export data in machine-readable format
    - Right to rectification: Users can correct their data
    - Privacy by design: Build privacy into system
    - Data protection impact assessment (DPIA)
    """

    def handle_data_access_request(self, user_id: str) -> Dict:
        """Handle user's request to access their data."""
        # Collect all data about user
        data = {
            'personal_info': self.get_user_profile(user_id),
            'training_data': self.get_user_training_data(user_id),
            'predictions': self.get_user_predictions(user_id),
            'model_influence': self.calculate_model_influence(user_id)
        }

        return data

    def handle_deletion_request(self, user_id: str):
        """Handle user's right to be forgotten."""

        # 1. Delete user data
        self.delete_user_data(user_id)

        # 2. Remove from training data
        self.remove_from_training_data(user_id)

        # 3. Assess impact on model
        impact = self.assess_deletion_impact(user_id)

        # 4. Retrain if significant impact
        if impact > 0.01:  # 1% accuracy impact
            self.trigger_model_retraining()

        # 5. Delete predictions
        self.delete_user_predictions(user_id)

        # 6. Audit log (keep for compliance)
        self.log_deletion_request(user_id, timestamp=datetime.utcnow())

    def export_user_data(self, user_id: str) -> bytes:
        """Export user data in machine-readable format."""
        data = self.handle_data_access_request(user_id)

        # Export as JSON
        import json
        json_data = json.dumps(data, indent=2)

        return json_data.encode('utf-8')

    def conduct_dpia(self, project_description: str) -> Dict:
        """
        Conduct Data Protection Impact Assessment.

        Required for high-risk processing:
        - Automated decision-making
        - Large-scale processing
        - Sensitive data
        - Systematic monitoring
        """
        assessment = {
            'description': project_description,
            'necessity': 'Why is data processing necessary?',
            'proportionality': 'Is processing proportionate to purpose?',
            'risks': self.identify_privacy_risks(),
            'mitigations': self.identify_mitigations(),
            'conclusion': 'Acceptable risk level?',
            'date': datetime.utcnow()
        }

        return assessment
```

### 7.2 Model Explainability (Right to Explanation)

```python
class ModelExplainer:
    """
    Provide explanations for model predictions.

    Required by:
    - GDPR (right to explanation)
    - Fair Credit Reporting Act
    - Internal governance

    Methods:
    - SHAP: Game theory-based explanations
    - LIME: Local linear approximations
    - Attention weights: For neural networks
    - Decision rules: For tree models
    """

    def explain_prediction(self, model, instance, feature_names):
        """Generate explanation for single prediction."""
        import shap

        # Create explainer
        explainer = shap.Explainer(model)

        # Calculate SHAP values
        shap_values = explainer(instance)

        # Generate explanation
        explanation = {
            'prediction': model.predict(instance)[0],
            'confidence': model.predict_proba(instance)[0].max(),
            'feature_contributions': dict(zip(
                feature_names,
                shap_values.values[0]
            )),
            'baseline': explainer.expected_value
        }

        return explanation

    def generate_natural_language_explanation(self, explanation: Dict) -> str:
        """Convert explanation to natural language."""

        prediction = explanation['prediction']
        confidence = explanation['confidence']
        contributions = explanation['feature_contributions']

        # Sort by absolute contribution
        sorted_features = sorted(
            contributions.items(),
            key=lambda x: abs(x[1]),
            reverse=True
        )

        text = f"Prediction: {prediction} (confidence: {confidence:.2%})\n\n"
        text += "Top factors:\n"

        for feature, contribution in sorted_features[:5]:
            direction = "increased" if contribution > 0 else "decreased"
            text += f"- {feature} {direction} the prediction by {abs(contribution):.3f}\n"

        return text

    def generate_counterfactual(self, model, instance, target_class):
        """
        Generate counterfactual explanation.

        "What would need to change for a different outcome?"

        Example: "If income was $10k higher, prediction would be approved"
        """
        # Find minimal changes to flip prediction
        # Uses optimization or search algorithms

        pass
```

---

## 8. Security Monitoring

### 8.1 Security Metrics

```python
class SecurityMonitor:
    """
    Monitor security metrics.

    Metrics:
    - Failed authentication attempts
    - Unusual API usage patterns
    - Data access violations
    - Model prediction anomalies
    - Resource abuse
    """

    def monitor_authentication(self):
        """Monitor authentication attempts."""
        failed_attempts = self.get_failed_auth_attempts(hours=1)

        # Alert on brute force attacks
        by_ip = defaultdict(int)
        for attempt in failed_attempts:
            by_ip[attempt['ip']] += 1

        for ip, count in by_ip.items():
            if count > 10:
                alert(f"Possible brute force attack from {ip}: {count} failed attempts")
                self.block_ip(ip, duration_hours=24)

    def monitor_api_abuse(self):
        """Monitor for API abuse."""

        # Check rate limit violations
        violations = self.get_rate_limit_violations(hours=1)

        if len(violations) > 100:
            alert("High number of rate limit violations")

        # Check for unusual patterns
        api_calls = self.get_api_calls(hours=24)
        unusual_patterns = self.detect_unusual_patterns(api_calls)

        if unusual_patterns:
            alert(f"Unusual API usage detected: {unusual_patterns}")

    def monitor_data_access(self):
        """Monitor data access for policy violations."""

        # Check unauthorized access attempts
        unauthorized = self.get_unauthorized_access_attempts(hours=1)

        if unauthorized:
            alert(f"Unauthorized access attempts: {len(unauthorized)}")

        # Check for unusual data access patterns
        access_logs = self.get_data_access_logs(hours=24)
        anomalies = self.detect_access_anomalies(access_logs)

        if anomalies:
            alert(f"Unusual data access patterns detected")
```

### 8.2 Audit Logging

```python
class AuditLogger:
    """
    Comprehensive audit logging.

    Log:
    - Who did what, when, where
    - Authentication events
    - Authorization decisions
    - Data access
    - Model usage
    - Configuration changes
    """

    def log_event(
        self,
        event_type: str,
        user: str,
        action: str,
        resource: str,
        result: str,
        details: Dict = None
    ):
        """Log security event."""

        event = {
            'timestamp': datetime.utcnow().isoformat(),
            'event_type': event_type,
            'user': user,
            'action': action,
            'resource': resource,
            'result': result,  # 'success' or 'failure'
            'ip_address': self.get_client_ip(),
            'user_agent': self.get_user_agent(),
            'details': details or {}
        }

        # Write to secure audit log
        self.write_audit_log(event)

        # Send to SIEM (Security Information and Event Management)
        self.send_to_siem(event)

    def search_audit_log(
        self,
        start_date: datetime,
        end_date: datetime,
        filters: Dict = None
    ) -> List[Dict]:
        """Search audit logs."""

        # Search by user, action, resource, etc.
        # Support compliance audits

        pass
```

---

## 9. Incident Response

### 9.1 Security Incident Response Plan

```markdown
## Security Incident Response Procedure

### Phase 1: Detection & Analysis (0-30 minutes)

✅ Detection
- [ ] Security alert received
- [ ] Incident severity assessed (Critical/High/Medium/Low)
- [ ] Security team notified
- [ ] Initial containment considered

✅ Analysis
- [ ] Verify it's a real security incident (not false positive)
- [ ] Determine attack vector
- [ ] Identify affected systems
- [ ] Assess data exposure

### Phase 2: Containment (30 minutes - 2 hours)

✅ Short-term Containment
- [ ] Isolate affected systems
- [ ] Block malicious IPs
- [ ] Revoke compromised credentials
- [ ] Enable additional logging

✅ Evidence Preservation
- [ ] Capture system state
- [ ] Preserve logs
- [ ] Document timeline
- [ ] Take disk images if needed

### Phase 3: Eradication (2-8 hours)

✅ Remove Threat
- [ ] Remove malware/backdoors
- [ ] Patch vulnerabilities
- [ ] Close attack vectors
- [ ] Verify threat removed

### Phase 4: Recovery (8-24 hours)

✅ Restore Services
- [ ] Restore from clean backups
- [ ] Verify system integrity
- [ ] Reset all credentials
- [ ] Monitor for reinfection

### Phase 5: Post-Incident (Within 1 week)

✅ Review & Improve
- [ ] Conduct post-mortem
- [ ] Document lessons learned
- [ ] Update security controls
- [ ] Update incident response plan
- [ ] Conduct training
```

### 9.2 Breach Notification

```python
class BreachNotification:
    """
    Handle data breach notifications.

    Legal Requirements:
    - GDPR: 72 hours to notify authorities
    - CCPA: "Without unreasonable delay"
    - HIPAA: 60 days
    - State breach laws: Vary by state
    """

    def assess_breach(self, incident: Dict) -> Dict:
        """Assess if incident constitutes a breach."""

        assessment = {
            'is_breach': False,
            'severity': 'unknown',
            'notification_required': False,
            'notification_deadline': None
        }

        # Check if personal data involved
        if incident['personal_data_exposed']:
            assessment['is_breach'] = True

            # Assess severity
            if incident['sensitive_data']:  # Health, financial, etc.
                assessment['severity'] = 'high'
                assessment['notification_required'] = True
                assessment['notification_deadline'] = datetime.utcnow() + timedelta(hours=72)
            else:
                assessment['severity'] = 'medium'
                assessment['notification_required'] = incident['individuals_affected'] > 500

        return assessment

    def notify_authorities(self, breach_details: Dict):
        """Notify relevant authorities."""

        # EU: Notify Data Protection Authority
        if self.has_eu_data:
            self.notify_dpa(breach_details)

        # US: Notify FTC, state attorneys general
        if self.has_us_data:
            self.notify_ftc(breach_details)
            self.notify_state_ags(breach_details)

    def notify_affected_individuals(self, breach_details: Dict):
        """Notify affected individuals."""

        affected_users = self.identify_affected_users(breach_details)

        for user in affected_users:
            self.send_breach_notification(
                user=user,
                details=breach_details,
                remediation_steps=self.get_remediation_steps()
            )
```

---

## 10. Compliance Frameworks

### 10.1 SOC 2 Compliance

```python
class SOC2Compliance:
    """
    System and Organization Controls (SOC 2) compliance.

    Trust Service Criteria:
    - Security: Protection against unauthorized access
    - Availability: System available for operation
    - Processing Integrity: Complete, valid, accurate processing
    - Confidentiality: Designated confidential information protected
    - Privacy: Personal information protected per commitments
    """

    def security_controls(self):
        """Implement SOC 2 security controls."""
        return {
            'CC6.1': 'Logical and Physical Access Controls',
            'CC6.2': 'Prior to issuing system credentials',
            'CC6.3': 'Removes access when no longer needed',
            'CC6.4': 'Restricts access to authorized users',
            'CC6.5': 'Alerts in case of security breaches',
            'CC6.6': 'Prevents unauthorized access',
            'CC6.7': 'Restricts transmission of data',
            'CC6.8': 'Encrypts data at rest and in transit'
        }

    def availability_controls(self):
        """Implement SOC 2 availability controls."""
        return {
            'A1.1': 'System monitoring',
            'A1.2': 'Incident response procedures',
            'A1.3': 'Backup and disaster recovery'
        }
```

### 10.2 ISO 27001

```python
class ISO27001Compliance:
    """
    ISO 27001 Information Security Management System.

    Domains:
    A.5: Information security policies
    A.6: Organization of information security
    A.7: Human resource security
    A.8: Asset management
    A.9: Access control
    A.10: Cryptography
    A.11: Physical and environmental security
    A.12: Operations security
    A.13: Communications security
    A.14: System acquisition, development and maintenance
    A.15: Supplier relationships
    A.16: Information security incident management
    A.17: Business continuity management
    A.18: Compliance
    """

    def access_control_policy(self):
        """A.9: Access control requirements."""
        return {
            'A.9.1.1': 'Access control policy documented',
            'A.9.2.1': 'User registration and de-registration',
            'A.9.2.2': 'User access provisioning',
            'A.9.2.3': 'Management of privileged access rights',
            'A.9.2.4': 'Management of secret authentication information',
            'A.9.3.1': 'Use of secret authentication information'
        }
```

---

## 11. Security Checklist

### Complete Security Checklist

```markdown
## Pre-Production Security Checklist

### Authentication & Authorization
- [ ] OAuth2/JWT implemented
- [ ] Role-based access control (RBAC)
- [ ] API key management
- [ ] Rate limiting
- [ ] Session management
- [ ] Password policy (if applicable)
- [ ] Multi-factor authentication (for admin)

### Data Security
- [ ] Data encrypted at rest
- [ ] Data encrypted in transit (TLS 1.2+)
- [ ] PII identified and protected
- [ ] Data retention policy
- [ ] Data backup strategy
- [ ] Secure data deletion

### Model Security
- [ ] Model integrity checks (hashing/signing)
- [ ] Model access control
- [ ] Adversarial input detection
- [ ] Model extraction prevention
- [ ] Prediction auditing

### Infrastructure Security
- [ ] Network segmentation
- [ ] Firewall rules configured
- [ ] Security groups/ACLs
- [ ] Container security scanning
- [ ] Dependency vulnerability scanning
- [ ] Secrets management (not hardcoded)
- [ ] Regular security updates

### Monitoring & Logging
- [ ] Audit logging enabled
- [ ] Security event monitoring
- [ ] Anomaly detection
- [ ] Log retention policy
- [ ] SIEM integration

### Compliance
- [ ] Privacy policy published
- [ ] Terms of service
- [ ] Data processing agreements
- [ ] GDPR compliance (if EU data)
- [ ] CCPA compliance (if CA data)
- [ ] Industry-specific compliance

### Incident Response
- [ ] Incident response plan documented
- [ ] Security contacts defined
- [ ] Breach notification procedure
- [ ] Regular security drills
- [ ] Disaster recovery plan

### Testing
- [ ] Penetration testing completed
- [ ] Vulnerability assessment
- [ ] Security code review
- [ ] Dependency audit
- [ ] Configuration review
```

---

## Conclusion

Security and compliance are ongoing processes, not one-time tasks. Key takeaways:

1. **Defense in Depth**: Multiple layers of security
2. **Least Privilege**: Minimum necessary access
3. **Security by Design**: Build security in from start
4. **Continuous Monitoring**: Always watching for threats
5. **Regular Updates**: Security is never "done"

**Action Items:**
1. Complete security checklist
2. Conduct security assessment
3. Implement missing controls
4. Schedule regular security reviews
5. Train team on security practices

Remember: **The cost of prevention << The cost of a breach**
