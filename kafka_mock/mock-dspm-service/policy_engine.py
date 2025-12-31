from models import (
    AssetDiscoveryEvent,
    PolicyViolationEvent,
    RemediationRequestEvent,
    ViolationType,
    ViolationSeverity,
    RemediationType,
    RemediationPriority,
    DataClassification,
)
from typing import List, Tuple, Optional
from datetime import datetime, timedelta
import uuid


class PolicyEngine:
    """
    Mock DSPM Policy Engine that evaluates discovered assets against security policies.
    
    Policy Rules:
    1. Unencrypted PII Data → CRITICAL violation → Remediation required
    2. Unencrypted PCI Data → CRITICAL violation → Remediation required
    3. Public access enabled → HIGH violation → Remediation required
    4. Missing owner tag → LOW violation → No remediation
    5. Compliant assets → No violations
    """
    
    def evaluate_asset(
        self, asset: AssetDiscoveryEvent
    ) -> Tuple[List[PolicyViolationEvent], List[RemediationRequestEvent]]:
        """
        Evaluate an asset against all policies.
        
        Returns:
            Tuple of (violations, remediation_requests)
        """
        violations = []
        remediations = []
        
        # Rule 1: Check for unencrypted PII data
        if (
            not asset.metadata.encryption_enabled
            and asset.metadata.data_classification == DataClassification.PII
        ):
            violation = self._create_violation(
                asset=asset,
                violation_type=ViolationType.UNENCRYPTED_PII_DATA,
                severity=ViolationSeverity.CRITICAL,
                policy_id="pol_encryption_pii_001",
                policy_name="PII Data Must Be Encrypted",
                description=f"Asset {asset.asset_id} contains PII data but encryption is not enabled",
            )
            violations.append(violation)
            
            remediation = self._create_remediation(
                asset=asset,
                violation=violation,
                remediation_type=RemediationType.ENABLE_ENCRYPTION,
                priority=RemediationPriority.CRITICAL,
                auto_remediate=False,
            )
            remediations.append(remediation)
        
        # Rule 2: Check for unencrypted PCI data
        if (
            not asset.metadata.encryption_enabled
            and asset.metadata.data_classification == DataClassification.PCI
        ):
            violation = self._create_violation(
                asset=asset,
                violation_type=ViolationType.UNENCRYPTED_PCI_DATA,
                severity=ViolationSeverity.CRITICAL,
                policy_id="pol_encryption_pci_001",
                policy_name="PCI Data Must Be Encrypted",
                description=f"Asset {asset.asset_id} contains PCI data but encryption is not enabled",
            )
            violations.append(violation)
            
            remediation = self._create_remediation(
                asset=asset,
                violation=violation,
                remediation_type=RemediationType.ENABLE_ENCRYPTION,
                priority=RemediationPriority.CRITICAL,
                auto_remediate=False,
            )
            remediations.append(remediation)
        
        # Rule 3: Check for public access
        if asset.metadata.public_access:
            violation = self._create_violation(
                asset=asset,
                violation_type=ViolationType.PUBLIC_ACCESS_ENABLED,
                severity=ViolationSeverity.HIGH,
                policy_id="pol_public_access_001",
                policy_name="Public Access Should Be Disabled",
                description=f"Asset {asset.asset_id} has public access enabled",
            )
            violations.append(violation)
            
            remediation = self._create_remediation(
                asset=asset,
                violation=violation,
                remediation_type=RemediationType.DISABLE_PUBLIC_ACCESS,
                priority=RemediationPriority.HIGH,
                auto_remediate=False,
            )
            remediations.append(remediation)
        
        # Rule 4: Check for missing owner tag
        if "owner" not in asset.metadata.tags or not asset.metadata.tags.get("owner"):
            violation = self._create_violation(
                asset=asset,
                violation_type=ViolationType.MISSING_OWNER_TAG,
                severity=ViolationSeverity.LOW,
                policy_id="pol_tagging_001",
                policy_name="Assets Must Have Owner Tag",
                description=f"Asset {asset.asset_id} is missing required 'owner' tag",
            )
            violations.append(violation)
            # No remediation for LOW severity violations
        
        return violations, remediations
    
    def _create_violation(
        self,
        asset: AssetDiscoveryEvent,
        violation_type: ViolationType,
        severity: ViolationSeverity,
        policy_id: str,
        policy_name: str,
        description: str,
    ) -> PolicyViolationEvent:
        """Create a policy violation event."""
        return PolicyViolationEvent(
            event_id=f"evt_violation_{uuid.uuid4().hex[:8]}",
            timestamp=datetime.utcnow().isoformat() + "Z",
            asset_id=asset.asset_id,
            violation_type=violation_type,
            severity=severity,
            policy_id=policy_id,
            policy_name=policy_name,
            description=description,
            source_event_id=asset.event_id,
        )
    
    def _create_remediation(
        self,
        asset: AssetDiscoveryEvent,
        violation: PolicyViolationEvent,
        remediation_type: RemediationType,
        priority: RemediationPriority,
        auto_remediate: bool,
    ) -> RemediationRequestEvent:
        """Create a remediation request event."""
        # Due date based on priority
        due_hours = {
            RemediationPriority.CRITICAL: 24,
            RemediationPriority.HIGH: 72,
            RemediationPriority.MEDIUM: 168,  # 1 week
            RemediationPriority.LOW: 720,  # 30 days
        }
        
        due_date = datetime.utcnow() + timedelta(hours=due_hours[priority])
        
        return RemediationRequestEvent(
            event_id=f"evt_remediation_{uuid.uuid4().hex[:8]}",
            timestamp=datetime.utcnow().isoformat() + "Z",
            asset_id=asset.asset_id,
            violation_event_id=violation.event_id,
            remediation_type=remediation_type,
            priority=priority,
            auto_remediate=auto_remediate,
            assigned_to="security-team",
            due_date=due_date.isoformat() + "Z",
        )
