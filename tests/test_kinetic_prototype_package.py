from pathlib import Path
import json

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
PROTO = ROOT / "fixtures/vx4800/kinetics/prototype-package-v1.json"
RFQ = ROOT / "fixtures/vx4800/kinetics/qualification/rfq-requirements-v1.json"
RIG = ROOT / "fixtures/vx4800/kinetics/qualification/t1-t2-test-rig-v1.json"
EVIDENCE = ROOT / "fixtures/vx4800/kinetics/qualification/vendor-evidence-v1.json"
PROTO_SCHEMA = ROOT / "schemas/aether-kinetic-prototype-package.schema.json"
RFQ_SCHEMA = ROOT / "schemas/aether-kinetic-rfq.schema.json"
RIG_SCHEMA = ROOT / "schemas/aether-kinetic-test-rig.schema.json"
EVIDENCE_SCHEMA = ROOT / "schemas/aether-kinetic-vendor-evidence.schema.json"


def load_json(path: Path):
    return json.loads(path.read_text())


def validate(instance_path: Path, schema_path: Path):
    instance = load_json(instance_path)
    schema = load_json(schema_path)
    errors = list(Draft202012Validator(schema).iter_errors(instance))
    assert not errors, [e.message for e in errors]
    return instance, schema


def test_preprototype_artifacts_validate_against_schemas():
    validate(PROTO, PROTO_SCHEMA)
    validate(RFQ, RFQ_SCHEMA)
    validate(RIG, RIG_SCHEMA)
    validate(EVIDENCE, EVIDENCE_SCHEMA)


def test_prototype_package_preserves_controlled_product_baseline():
    proto = load_json(PROTO)
    baseline = proto["controlledBaseline"]
    boundary = proto["packageBoundary"]

    assert baseline["elementCount"] == 240
    assert baseline["sizeAllocation"] == {"S": 66, "M": 144, "L": 30}
    assert baseline["canopyEnvelopeMm"] == [2400, 1500, 150]
    assert baseline["rotatingCarrierCoordinationMm"] == {"width": 2260, "depth": 1330, "thicknessParameter": 24}
    assert baseline["speedRpm"] == {"minimum": 0.08, "nominal": 0.36, "maximum": 0.65}
    assert baseline["fixedAccentHeadCount"] == 14
    assert baseline["slipRingStatus"] == "not-required-by-current-architecture"
    assert boundary["manufacturingGeometryAuthorityChanged"] is False
    assert boundary["controlledSetoutChanged"] is False
    assert boundary["poweredRotatingDeviceIntroduced"] is False


def test_interface_zones_cover_all_critical_mechanical_functions():
    proto = load_json(PROTO)
    zones = {zone["id"]: zone for zone in proto["interfaceZones"]}
    required = {
        "KZ-PRIMARY-BEARING",
        "KZ-POSITIVE-DRIVE",
        "KZ-DIRECT-CARRIER-BRAKE",
        "KZ-SERVICE-LOCK",
        "KZ-SECONDARY-RETENTION",
        "KZ-FEEDBACK",
        "KZ-BALANCE-TRIM",
        "KZ-SERVICE-CORRIDOR",
    }
    assert required.issubset(zones)
    assert all(zone["envelopeStatus"] == "coordination-only-tbd" for zone in zones.values())

    brake = zones["KZ-DIRECT-CARRIER-BRAKE"]
    assert any("passive annular brake ring" in item for item in brake["rotatingSide"])
    assert "mechanical service lock" in " ".join(brake["mustNotBecomeLoadPath"]).lower()

    feedback = zones["KZ-FEEDBACK"]
    assert any("passive" in item.lower() for item in feedback["rotatingSide"])


def test_load_dependent_dimensions_are_not_invented():
    proto = load_json(PROTO)
    dimensions = {item["id"]: item for item in proto["loadDependentDimensions"]}
    required = {
        "bearingPitchDiameterAndSection",
        "bearingSupportRingThicknessAndRibbing",
        "bearingBoltPatternAndPreload",
        "driveRingPitchDiameter",
        "beltOrGearWidthAndPretension",
        "brakeEffectiveRadius",
        "brakeRingThicknessAndMaterial",
        "serviceLockPinDiameterAndReceiverSection",
        "secondaryRetentionGapAndEngagementTravel",
        "secondaryRetentionSectionAndFasteners",
        "feedbackRingDiameterAndReadheadAirGap",
        "trimStationCapacity",
    }
    assert required.issubset(dimensions)
    assert all(item["status"] == "tbd" for item in dimensions.values())


def test_prototype_release_is_schema_blocked_while_gates_are_false():
    proto, schema = validate(PROTO, PROTO_SCHEMA)
    assert proto["finalPrototypePackageReleased"] is False
    assert not any(proto["prototypePromotionGate"].values())

    promoted = dict(proto)
    promoted["finalPrototypePackageReleased"] = True
    errors = list(Draft202012Validator(schema).iter_errors(promoted))
    assert errors, "Prototype package schema must reject release while any required gate is false"


def test_rfq_has_separate_supplier_packages_and_forbids_fake_selection():
    rfq = load_json(RFQ)
    packages = {item["id"]: item for item in rfq["supplierPackages"]}
    required = {
        "RFQ-KIN-BRG-01",
        "RFQ-KIN-DRV-01",
        "RFQ-KIN-BELT-01",
        "RFQ-KIN-BRK-01",
        "RFQ-KIN-FBK-01",
        "RFQ-KIN-FAB-01",
    }
    assert required == set(packages)
    assert all(item["selectionStatus"] != "selected" for item in packages.values())
    assert "no powered rotating loads" in " ".join(rfq["commonInformationToAllSuppliers"]).lower()
    assert "measured inputs" in rfq["releaseRule"].lower()


def test_bearing_belt_and_brake_rfq_capture_hardening_findings():
    rfq = load_json(RFQ)
    packages = {item["id"]: item for item in rfq["supplierPackages"]}

    bearing = " ".join(packages["RFQ-KIN-BRG-01"]["requiredSupplierResponse"]).lower()
    assert "mounting flatness" in bearing
    assert "preload" in bearing
    assert "starting/running torque" in bearing

    belt = " ".join(packages["RFQ-KIN-BELT-01"]["requiredSupplierResponse"]).lower()
    assert "installation tension" in belt
    assert "separation forces" in belt
    assert "ratcheting" in belt

    brake = " ".join(packages["RFQ-KIN-BRK-01"]["requiredSupplierResponse"]).lower()
    assert "spring-applied" in brake
    assert "static holding versus dynamic-stop capability" in brake
    assert "manual release" in brake


def test_t1_t2_rig_uses_controlled_schedule_and_cannot_be_built_from_assumed_mass():
    rig = load_json(RIG)
    stages = {stage["id"]: stage for stage in rig["rigStages"]}

    assert "engineering-v1.3.0.csv" in stages["T1"]["geometrySource"]
    assert "engineering-v1.3.0.csv" in stages["T2"]["geometrySource"]
    assert "relative X/Y coordinates" in stages["T2"]["geometrySource"]
    assert stages["T1"]["loadCapacityStatus"] == "tbd-measured-mass-required"
    assert stages["T2"]["loadCapacityStatus"] == "tbd-measured-mass-required"
    assert all(value is False for value in rig["buildGate"].values())
    assert rig["safetyBoundary"]["physicalGuardingRequired"] is True
    assert rig["safetyBoundary"]["emergencyStopRequired"] is True
    assert rig["safetyBoundary"]["occupiedInstallationSimulator"] is False


def test_t1_t2_instrumentation_requires_calibration_and_raw_traceability():
    rig = load_json(RIG)
    ids = {instrument["id"] for instrument in rig["instrumentation"]}
    required = {"INST-ANGLE-SPEED", "INST-DRIVE-LOAD", "INST-CABLE-TENSION", "INST-MOTION-VIDEO", "INST-CLEARANCE", "INST-TIME-SYNC"}
    assert required.issubset(ids)
    assert all(instrument["calibrationRequired"] is True for instrument in rig["instrumentation"])
    data = " ".join(rig["dataRequirements"]).lower()
    assert "record raw data" in data
    assert "retain failed/aborted runs" in data
    assert "acceptance criteria" in data


def test_vendor_evidence_remains_architecture_evidence_not_selection():
    evidence = load_json(EVIDENCE)
    manufacturers = {record["manufacturer"] for record in evidence["records"]}
    assert {"Kaydon Bearings", "Gates Corporation", "RINGSPANN GmbH", "HEIDENHAIN"}.issubset(manufacturers)
    assert all(record["finalVariantSelected"] is False for record in evidence["records"])
    assert all(record["accessedDate"] == "2026-09-04" for record in evidence["records"])
    assert "no record" in evidence["selectionRule"].lower()


def test_cad_rules_protect_setout_and_separate_normal_from_failure_states():
    proto = load_json(PROTO)
    rules = " ".join(proto["drawingAndCadRequirements"]["cadRules"]).lower()
    assert "do not modify controlled cable-exit coordinates" in rules
    assert "do not modify 14 fixed led coordinates" in rules
    assert "normal retention clearance and abnormal engagement" in rules
    assert "service-tool and removal envelopes" in rules
