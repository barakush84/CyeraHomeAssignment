from pydantic import BaseModel, Field
from typing import Dict, Optional
from datetime import datetime
from enum import Enum


class AssetType(str, Enum):
    S3_BUCKET = "S3_BUCKET"
    RDS_DATABASE = "RDS_DATABASE"
    DYNAMODB_TABLE = "DYNAMODB_TABLE"
    SNOWFLAKE_TABLE = "SNOWFLAKE_TABLE"


class DataClassification(str, Enum):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    PII = "PII"
    PCI = "PCI"


class CloudProvider(str, Enum):
    AWS = "AWS"
    AZURE = "AZURE"
    GCP = "GCP"


class AssetMetadata(BaseModel):
    encryption_enabled: bool
    public_access: bool
    data_classification: DataClassification
    tags: Dict[str, str] = Field(default_factory=dict)


class AssetDiscoveryEvent(BaseModel):
    event_id: str
    timestamp: str
    asset_id: str
    asset_type: AssetType
    cloud_provider: CloudProvider
    region: str
    discovered_by: str
    metadata: AssetMetadata


class ViolationSeverity(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ViolationType(str, Enum):
    UNENCRYPTED_PII_DATA = "UNENCRYPTED_PII_DATA"
    UNENCRYPTED_PCI_DATA = "UNENCRYPTED_PCI_DATA"
    PUBLIC_ACCESS_ENABLED = "PUBLIC_ACCESS_ENABLED"
    MISSING_OWNER_TAG = "MISSING_OWNER_TAG"
    MISSING_DATA_CLASSIFICATION = "MISSING_DATA_CLASSIFICATION"


class PolicyViolationEvent(BaseModel):
    event_id: str
    timestamp: str
    asset_id: str
    violation_type: ViolationType
    severity: ViolationSeverity
    policy_id: str
    policy_name: str
    description: str
    source_event_id: str


class RemediationType(str, Enum):
    ENABLE_ENCRYPTION = "ENABLE_ENCRYPTION"
    DISABLE_PUBLIC_ACCESS = "DISABLE_PUBLIC_ACCESS"
    ADD_REQUIRED_TAGS = "ADD_REQUIRED_TAGS"
    UPDATE_DATA_CLASSIFICATION = "UPDATE_DATA_CLASSIFICATION"


class RemediationPriority(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class RemediationRequestEvent(BaseModel):
    event_id: str
    timestamp: str
    asset_id: str
    violation_event_id: str
    remediation_type: RemediationType
    priority: RemediationPriority
    auto_remediate: bool
    assigned_to: str
    due_date: str
