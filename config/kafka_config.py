from enum import Enum


class EnumBase(Enum):
    """
    Base class for enumerations to allow easy access to the value.
    """
    def __get__(self, instance, owner):
        return self.value


class EnvironmentTesting(EnumBase):
    TESTING = "test-bucket"
    PRODUCTION = "prod-bucket"


class Provider(EnumBase):
    AWS = "AWS"
    AZURE = "AZURE"
    GCP = "GCP"


class DiscoveryAssetType(EnumBase):
    S3_BUCKET = "S3_BUCKET"
    RDS_DATABASE = "RDS_DATABASE"
    DYNAMODB_TABLE = "DYNAMODB_TABLE"
    SNOWFLAKE_TABLE = "SNOWFLAKE_TABLE"


class DiscoveryAssetIdPrefix(EnumBase):
    S3 = "s3://"
    RDS = "rds://"
    DYNAMODB = "dynamodb://"
    SNOWFLAKE = "snowflake://"


class DiscoveryDataClassification(EnumBase):
    PUBLIC = "PUBLIC"
    INTERNAL = "INTERNAL"
    CONFIDENTIAL = "CONFIDENTIAL"
    PII = "PII"
    PCI = "PCI"


class ViolationType(EnumBase):
    UNENCRYPTED_PII_DATA = "UNENCRYPTED_PII_DATA"
    UNENCRYPTED_PCI_DATA = "UNENCRYPTED_PCI_DATA"
    PUBLIC_ACCESS_ENABLED = "PUBLIC_ACCESS_ENABLED"
    MISSING_OWNER_TAG = "MISSING_OWNER_TAG"


class ViolationSeverity(EnumBase):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


class RemediationType(EnumBase):
    ENABLE_ENCRYPTION = "ENABLE_ENCRYPTION"
    DISABLE_PUBLIC_ACCESS = "DISABLE_PUBLIC_ACCESS"
    ADD_OWNER_TAG = "ADD_OWNER_TAG"


class RemediationPriority(EnumBase):
    CRITICAL = "CRITICAL"
    HIGH = "HIGH"
    MEDIUM = "MEDIUM"
    LOW = "LOW"


KAFKA_BOOTSTRAP_SERVERS = "localhost:9092"

DISCOVERY_TOPIC = "dspm.discovery.asset"
VIOLATION_TOPIC = "dspm.policy.violation"
REMEDIATION_TOPIC = "dspm.remediation.requested"

ASSET_TYPE = DiscoveryAssetType.S3_BUCKET
PROVIDER = Provider.AWS
TESTING_ENVIRONMENT = EnvironmentTesting.TESTING
ASSET_ID_PREFIX = DiscoveryAssetIdPrefix.S3
