from copy import deepcopy
from pathlib import Path
import json

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
INTERFACE = ROOT / "fixtures/vx4800/kinetics/interface-control-v1.json"
CALCS = ROOT / "fixtures/vx4800/kinetics/qualification/calculation-register-v1.json"
INTERFACE_SCHEMA = ROOT / "schemas/aether-kinetic-interface-control.schema.json"
CALCS_SCHEMA = ROOT / "schemas/aether-kinetic-calculation-register.schema.json"


def load_json(path: Path):
    return json.loads(path.read_text())


def validate(instance_path: Path, schema_path: Path):
    instance = load_json(instance_path)
    schema = load_json(schema_path)
    errors = list(Draft202012Validator(schema).iter_errors(instance))
    assert not errors, [e.message for e in errors]
    return instance, schema


def test_interface_and_calculation_artifacts_validate():
    validate(INTERFACE, INTERFACE_SCHEMA)
    validate(CALCS, CALCS_SCHEMA)


def test_interface_control_preserves_product_and_power_boundaries():
    interface = load_json(INTERFACE)
    baseline = interface["controlledBaseline"]
    assert baseline["elementCount"] == 240
    assert baseline["sizeAllocation"] == {"S": 66, "M": 144, "L": 30}
    assert baseline["canopyEnvelopeMm"] == [2400, 1500, 150]
    assert baseline["rotatingCarrierCoordinationMm"] == {"width": 2260, "depth": 1330, "thicknessParameter": 24}
    assert baseline["speedRpm"] == {"minimum": 0.08, "nominal": 0.36, "maximum": 0.65}
    assert baseline["fixedAccentHeadCount"] == 14
    assert baseline["slipRingStatus"] == "not-required-by-current-architecture"

    text = json.dumps(interface).lower()
    assert "powered rotating encoder introduced without architecture change" in text
    assert "rotating electrical power" in text


def test_interface_control_has_independent_mechanical_functions():
    interface = load_json(INTERFACE)
    interfaces = {item["id"]: item for item in interface["mechanicalInterfaces"]}
    required = {
        "KI-BEARING",
        "KI-DRIVE",
        "KI-BRAKE",
        "KI-SERVICE-LOCK",
        "KI-SECONDARY-RETENTION",
        "KI-FEEDBACK-PRIMARY",
        "KI-FEEDBACK-DIVERSE",
        "KI-BALANCE-TRIM",
        "KI-SERVICE-ACCESS",
    }
    assert required == set(interfaces)

    brake = json.dumps(interfaces["KI-BRAKE"]).lower()
    lock = json.dumps(interfaces["KI-SERVICE-LOCK"]).lower()
    retention = json.dumps(interfaces["KI-SECONDARY-RETENTION"]).lower()
    assert "failed drive transmission" in brake
    assert "mechanical service lock" in brake
    assert "brake status substituted for lock engagement" in lock
    assert "bearing bolts" in retention
    assert "routine retention rubbing" in retention


def test_rotation_axis_direction_does_not_fake_xy_physical_datum():
    interface = load_json(INTERFACE)
    datums = {item["id"]: item for item in interface["datumFramework"]}
    axis = datums["KD-B-ROTATION-AXIS"]
    assert axis["status"] == "functional-reference"
    assert "direction only" in axis["rule"].lower()
    assert "composition origin must not be substituted" in axis["rule"].lower()

    params = {item["id"]: item for item in interface["interfaceParameters"]}
    axis_xy = params["rotationAxisXYPhysicalDatum"]
    assert axis_xy["status"] == "tbd"
    assert axis_xy["value"] is None
    assert "composition origin is not sufficient evidence" in axis_xy["dependency"].lower()


def test_interface_parameters_are_traceable_tbd_not_fake_dimensions():
    interface = load_json(INTERFACE)
    params = {item["id"]: item for item in interface["interfaceParameters"]}
    required = {
        "rotationAxisXYPhysicalDatum",
        "bearingMountingDiameter",
        "bearingSupportFlatness",
        "bearingBoltCircleAndPreload",
        "driveRingPitchDiameter",
        "driveBeltOrGearWidth",
        "drivePretension",
        "brakeEffectiveRadius",
        "brakeRingThickness",
        "brakeCaliperMountOffset",
        "serviceLockPinDiameter",
        "serviceLockEngagementTravel",
        "retentionNormalClearance",
        "retentionAbnormalEngagementTravel",
        "feedbackPrimaryAirGap",
        "feedbackDiverseAirGap",
        "trimStationCapacity",
        "componentExtractionEnvelope",
    }
    assert required == set(params)
    assert all(item["status"] == "tbd" for item in params.values())
    assert all(item["value"] is None for item in params.values())
    assert all(item["dependency"] for item in params.values())


def test_tolerance_closures_include_critical_runout_alignment_and_access_loops():
    interface = load_json(INTERFACE)
    closures = {item["id"]: item for item in interface["toleranceClosures"]}
    required = {
        "TC-BEARING-MOUNT",
        "TC-DRIVE-ALIGN",
        "TC-BRAKE-RUNOUT",
        "TC-LOCK-ENGAGEMENT",
        "TC-RETENTION-NORMAL-CLEARANCE",
        "TC-FEEDBACK-AIR-GAP",
        "TC-SERVICE-EXTRACTION",
    }
    assert required == set(closures)
    assert all(item["status"] == "tbd" for item in closures.values())
    assert all(len(item["contributors"]) >= 2 for item in closures.values())


def test_failure_state_cad_models_cover_common_cause_and_recovery():
    interface = load_json(INTERFACE)
    states = {item["id"]: item for item in interface["failureStateModels"]}
    required = {
        "FS-NORMAL-RUN",
        "FS-TRANSMISSION-DISCONNECTED",
        "FS-BRAKE-APPLIED",
        "FS-SERVICE-LOCKED",
        "FS-PRIMARY-SUPPORT-SEPARATION",
        "FS-RETENTION-ENGAGED",
        "FS-MANUAL-RECOVERY",
        "FS-FEEDBACK-FAULT",
    }
    assert required == set(states)
    assert "failed transmission" in " ".join(states["FS-TRANSMISSION-DISCONNECTED"]["mustRemainTrue"]).lower()
    assert "out of service" in " ".join(states["FS-RETENTION-ENGAGED"]["mustRemainTrue"]).lower()
    assert "positively restrained" in " ".join(states["FS-MANUAL-RECOVERY"]["mustRemainTrue"]).lower()


def test_interface_release_cannot_be_faked_with_tbd_parameters():
    interface, schema = validate(INTERFACE, INTERFACE_SCHEMA)
    assert interface["finalInterfaceControlReleased"] is False
    assert not any(interface["releaseGates"].values())

    promoted = deepcopy(interface)
    promoted["finalInterfaceControlReleased"] = True
    promoted["authority"] = "controlled"
    promoted["status"] = "released"
    promoted["releaseGates"] = {key: True for key in promoted["releaseGates"]}
    errors = list(Draft202012Validator(schema).iter_errors(promoted))
    assert errors, "Interface release must remain blocked while datums, dimensions or tolerance closures are unresolved"


def test_calculation_register_has_complete_abnormal_and_normal_case_set():
    calcs = load_json(CALCS)
    cases = {item["id"]: item for item in calcs["loadCases"]}
    assert set(cases) == {f"KLC-{index:03d}" for index in range(1, 14)}
    names = {item["name"] for item in cases.values()}
    assert "jerk-limited start transient" in names
    assert "power-loss and fault stop" in names
    assert "snag and abnormal added-drag detection" in names
    assert "transmission-disconnect holding" in names
    assert "mechanical service-lock proof case" in names
    assert "primary-support failure and secondary-retention engagement" in names
    assert "manual recovery restrained state" in names


def test_calculation_register_contains_no_invented_results():
    calcs = load_json(CALCS)
    assert all(case["status"] == "blocked-inputs" for case in calcs["loadCases"])
    outputs = [output for case in calcs["loadCases"] for output in case["outputs"]]
    assert outputs
    assert all(output["value"] is None for output in outputs)
    assert all(output["status"] == "tbd" for output in outputs)
    assert not any(calcs["releaseGates"].values())


def test_suspended_field_dynamics_are_required_for_transient_cases():
    calcs = load_json(CALCS)
    cases = {item["id"]: item for item in calcs["loadCases"]}
    for case_id in ["KLC-002", "KLC-005", "KLC-006"]:
        text = json.dumps(cases[case_id]).lower()
        assert "prototype-measurement" in text
        assert "t1/t2" in text
    assert "rigid-body polar inertia" in " ".join(calcs["calculationRules"]).lower()
    assert "screening" in " ".join(calcs["calculationRules"]).lower()


def test_bearing_case_consumes_mounting_and_drive_reactions():
    calcs = load_json(CALCS)
    static_case = next(case for case in calcs["loadCases"] if case["id"] == "KLC-001")
    text = json.dumps(static_case).lower()
    assert "drive pretension" in text
    assert "bearing" in text
    assert "combined-load" in text


def test_service_lock_and_retention_are_not_collapsed_into_operating_brake():
    calcs = load_json(CALCS)
    cases = {item["id"]: item for item in calcs["loadCases"]}
    lock_text = json.dumps(cases["KLC-011"]).lower()
    retention_text = json.dumps(cases["KLC-012"]).lower()
    brake_text = json.dumps(cases["KLC-010"]).lower()
    assert "independent of motor/brake torque" in lock_text
    assert "failure coverage/fmea" in retention_text
    assert "direct-carrier brake" in brake_text


def test_calculation_release_requires_verified_cases_outputs_and_gates():
    calcs, schema = validate(CALCS, CALCS_SCHEMA)
    promoted = deepcopy(calcs)
    promoted["finalCalculationPackageReleased"] = True
    promoted["authority"] = "controlled"
    promoted["status"] = "released"
    promoted["releaseGates"] = {key: True for key in promoted["releaseGates"]}
    for case in promoted["loadCases"]:
        case["status"] = "calculation-ready"
    errors = list(Draft202012Validator(schema).iter_errors(promoted))
    assert errors, "Calculation package must not release with merely calculation-ready cases or unresolved outputs"


def test_no_safety_integrity_level_is_invented_in_new_engineering_layer():
    text = (INTERFACE.read_text() + CALCS.read_text()).lower()
    forbidden_assignment_tokens = ["sil 1", "sil 2", "sil 3", "pl a", "pl b", "pl c", "pl d", "pl e"]
    assert not any(token in text for token in forbidden_assignment_tokens)
