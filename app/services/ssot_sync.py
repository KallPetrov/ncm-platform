import httpx
from typing import List, Dict, Any
from sqlalchemy.orm import Session
from app.models.device import Device, DeviceType, DeviceStatus
from app.services.audit import AuditService


class SSOTSyncService:
    """
    NetBox / Nautobot Single Source of Truth Synchronization Service (Module 4.3)

    Provides bidirectional integration to automatically synchronize local device inventory,
    metadata, and operational statuses with enterprise Single Source of Truth APIs.
    """

    @classmethod
    def sync_devices_from_netbox(
        cls, db: Session, netbox_url: str, api_token: str, is_testing: bool = True
    ) -> Dict[str, Any]:
        """
        Synchronizes device inventory from NetBox to local NCM:
        1. Queries NetBox /api/dcim/devices/
        2. Compares IP addresses and hostnames.
        3. Imports missing devices and updates modified ones.
        """
        if is_testing:
            # Simulated NetBox API Response for validation
            netbox_devices = [
                {
                    "name": "NetBox-Router-1",
                    "primary_ip": {"address": "192.168.10.1/24"},
                    "device_role": {"slug": "router"},
                    "device_type": {"model": {"name": "Cisco 2911"}},
                    "platform": {"slug": "cisco_ios"},
                    "site": {"name": "Sofia-DC"}
                },
                {
                    "name": "NetBox-Switch-2",
                    "primary_ip": {"address": "192.168.10.2/24"},
                    "device_role": {"slug": "switch"},
                    "device_type": {"model": {"name": "Cisco 3750"}},
                    "platform": {"slug": "cisco_ios"},
                    "site": {"name": "Plovdiv-Office"}
                }
            ]
        else:
            try:
                headers = {"Authorization": f"Token {api_token}"}
                response = httpx.get(f"{netbox_url}/api/dcim/devices/", headers=headers, timeout=5)
                if response.status_code != 200:
                    return {"success": False, "error": f"NetBox API returned status {response.status_code}"}
                netbox_devices = response.json().get("results", [])
            except Exception as e:
                return {"success": False, "error": f"Failed to connect to NetBox: {str(e)}"}

        added_count = 0
        updated_count = 0

        for nb_dev in netbox_devices:
            # Parse primary IP
            ip_obj = nb_dev.get("primary_ip")
            if not ip_obj:
                continue
            raw_ip = ip_obj.get("address", "")
            ip_address = raw_ip.split("/")[0] if "/" in raw_ip else raw_ip

            if not ip_address:
                continue

            # Query existing local device
            existing = db.query(Device).filter(Device.ip_address == ip_address).first()

            # Map NetBox device role to local DeviceType
            role_slug = nb_dev.get("device_role", {}).get("slug", "other")
            dev_type = DeviceType.ROUTER if "router" in role_slug else DeviceType.SWITCH if "switch" in role_slug else DeviceType.OTHER

            if existing:
                # Update details if changed
                existing.name = nb_dev.get("name", existing.name)
                existing.location = nb_dev.get("site", {}).get("name", existing.location)
                existing.model = nb_dev.get("device_type", {}).get("model", {}).get("name", existing.model)
                updated_count += 1
            else:
                # Create missing device
                new_device = Device(
                    name=nb_dev.get("name", "Imported Device"),
                    ip_address=ip_address,
                    device_type=dev_type,
                    vendor=nb_dev.get("platform", {}).get("slug", "Cisco").capitalize(),
                    model=nb_dev.get("device_type", {}).get("model", {}).get("name", "Unknown"),
                    location=nb_dev.get("site", {}).get("name", "Default"),
                    username="admin",  # Default imported credentials
                    password="temp_password",
                    status=DeviceStatus.UNKNOWN
                )
                db.add(new_device)
                added_count += 1

        db.commit()

        # Audit Sync completion
        AuditService.log_action(
            db,
            None,
            "ssot_sync_completed",
            resource_type="system",
            resource_id=0,
            details=f"NetBox synchronization completed. Added {added_count}, updated {updated_count} devices."
        )

        return {
            "success": True,
            "added_count": added_count,
            "updated_count": updated_count
        }

    @classmethod
    def push_local_changes_to_netbox(
        cls, db: Session, device_id: int, netbox_url: str, api_token: str, is_testing: bool = True
    ) -> Dict[str, Any]:
        """
        Publishes discovered local hardware/OS details back to NetBox to ensure
        the SSOT contains up-to-date real-world state.
        """
        device = db.query(Device).filter(Device.id == device_id).first()
        if not device:
            return {"success": False, "error": "Device not found"}

        payload = {
            "custom_fields": {
                "ncm_last_backup": device.last_backup.isoformat() if device.last_backup else None,
                "ncm_os_version": device.model or "unknown"
            }
        }

        if is_testing:
            success = True
            status_code = 200
        else:
            try:
                headers = {"Authorization": f"Token {api_token}"}
                response = httpx.patch(f"{netbox_url}/api/dcim/devices/?name={device.name}", json=payload, headers=headers, timeout=5)
                success = response.status_code in [200, 201, 204]
                status_code = response.status_code
            except Exception as e:
                return {"success": False, "error": f"Failed to push updates to NetBox: {str(e)}"}

        if not success:
            return {"success": False, "error": f"NetBox update failed with status {status_code}"}

        return {"success": True, "message": f"Successfully pushed device '{device.name}' status to NetBox."}
