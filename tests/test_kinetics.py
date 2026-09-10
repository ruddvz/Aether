from pathlib import Path
import json

import pandas as pd
from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
ARCH = ROOT / "fixtures/vx4800/kinetics/architecture-v1.json"
SHORTLIST = ROOT / "fixtures/vx4800/kinetics/qualification/shortlist-v1.json"
ARCH_SCHEMA = ROOT / "schemas/aether-kinetic-architecture.schema.json"
SHORTLIST_SCHEMA = ROOT / "schemas/aether-kinetic-qualification.schema.json"
FIXTURE = ROOT / "fixtures/vx4800/fixture.json"
GEOMETRY = ROOT / "fixtures/vx4800/geometry/parameters-v1.3.0.json"
SCHEDULE = ROOT / "fixtures/vx4800/composition/engineering-v1.3.0.csv"
ELECTRICAL = ROOT / "fixtures/vx4800/electrical/architecture-v1.json"


def load_json(path: Path):
    return json.loads(path.read_text())


def test_kinetic_architecture_schema_and_identity():
    architecture = load_json(ARCH)
    schema = load_json(ARCH_SCHEMA)
    errors = list(Draft202012Validator(schema).iter_errors(architecture))
    assert not errors, [e.message for e in errors]
    assert architecture["fixtureId"] == "vx4800-bf-01"
    assert architecture["architectureRevision"] == "1.0.0"


def test_kinetic_shortlist_schema_and_is_not_approved():
    shortlist = load_json(SHORTLIST)
    schema = load_json(SHORTLIST_SCHEMA)
    errors = list(Draft202012Validator(schema).iter_errors(shortlist))
    assert not errors, [e.message for e in errors]
    assert shortlist["finalKineticComponentSetApproved"] is False
    assert shortlist["status"] != "approved"
    assert shortlist["authority"] != "controlled"


def test_controlled_product_baseline_is_unchanged():
    architecture = load_json(ARCH)
    fixture = load_json(FIXTURE)
    geometry = load_json(GEOMETRY)
    schedule = pd.read_csv(SCHEDULE)
    baseline = architecture["controlledBaseline"]

    assert fixture["composition"]["elementCount"] == 240
    assert schedule["size"].value_counts().to_dict() == {"M": 144, "S": 66, "L": 30}
    assert baseline["sizeAllocation"] == {"S": 66, "M": 144, "L": 30}
    assert geometry["canopy"] == {"widthMm": 2400, "depthMm": 1500, "heightMm": 150, "cornerRadiusMm": 260}
    assert geometry["rotatingCarrier"]["widthMm"] == 2260
    assert geometry["rotatingCarrier"]["depthMm"] == 1330
    assert geometry["rotatingCarrier"]["thicknessMm"] == 24
    assert fixture["optical"]["emitters"][0]["quantity"] == 14
    assert baseline["fixedAccentHeadCount"] == 14


def test_no_slip_ring_or_powered_rotor_was_introduced():
    architecture = load_json(ARCH)
    electrical = load_json(ELECTRICAL)
    baseline = architecture["controlledBaseline"]
    feedback = architecture["feedbackArchitecture"]

    assert baseline["rotatingElectricalLoadStatus"] == "none-planned"
    assert baseline["slipRingStatus"] == "not-required-by-current-architecture"
    assert electrical["fixedRotatingBoundary"]["slipRingStatus"] == "not-required-by-current-architecture"
    assert "powered sensing electronics fixed-side" in feedback["principle"]
    assert any("no powered rotating encoder electronics" in req for req in feedback["requirements"])


def test_unknown_physical_inputs_remain_explicitly_unknown():
    architecture = load_json(ARCH)
    unknowns = {entry["id"]: entry for entry in architecture["unknownPhysicalInputs"]}
    required = {
        "S_completeSuspendedAssemblyMass",
        "M_completeSuspendedAssemblyMass",
        "L_completeSuspendedAssemblyMass",
        "totalInstalledRotatingMass",
        "rotatingAssemblyCenterOfGravity",
        "productionMassVariation",
        "dynamicAmplification",
        "bearingDesignLoads",
        "driveTorque",
        "brakingTorque",
        "imbalance",
        "structuralReactions",
    }
    assert required.issubset(unknowns)
    assert all(entry["status"] == "unknown" for entry in unknowns.values())
    assert architecture["bearingArchitecture"]["selectionStatus"] == "not-selected"
    assert architecture["driveArchitecture"]["selectionStatus"] == "not-selected"
    assert architecture["brakingArchitecture"]["selectionStatus"] == "not-selected"


def test_primary_secondary_drive_brake_and_service_lock_paths_are_separate():
    architecture = load_json(ARCH)
    paths = architecture["loadPathArchitecture"]

    assert "primary bearing rolling/race elements and bolted rings" in paths["primaryLoadPath"]
    assert "normally-clear independent annular catch structure" in paths["secondaryRetentionPath"]
    assert "positive belt or geared transmission under qualification" in paths["driveTorquePath"]
    assert "fixed-side spring-applied or otherwise positively acting brake under qualification" in paths["brakingPath"]
    assert "positive mechanical lock pin/bolt in double-shear style support or equivalent" in paths["serviceLockPath"]

    prohibited = " ".join(paths["prohibitedAccidentalLoadPaths"]).lower()
    for term in ("decorative canopy skin", "false ceiling", "motor gearbox", "bearing seals", "electrical conduits"):
        assert term in prohibited


def test_service_lock_is_positive_mechanical_and_not_motor_brake():
    architecture = load_json(ARCH)
    lock = architecture["serviceLock"]
    requirements = " ".join(lock["requirements"]).lower()

    assert lock["status"] == "concept-to-prototype"
    assert "cannot depend on software or motor torque" in requirements
    assert "padlockable" in requirements
    assert "technician can verify full engagement directly" in requirements
    assert "motor brake is never the sole service restraint" in architecture["brakingArchitecture"]["serviceRestraint"]


def test_secondary_retention_is_normally_clear_and_structural():
    architecture = load_json(ARCH)
    retention = architecture["secondaryRetention"]
    requirements = " ".join(retention["requirements"]).lower()

    assert retention["normalLoadSharingIntent"].startswith("non-load-sharing")
    assert "annular catch/capture" in retention["concept"]
    assert "valid structural path" in requirements
    assert "continuous rotation without winding flexible tethers" in requirements
    assert "proof test" in requirements
    assert retention["finalRatingStatus"].startswith("unknown")


def test_motion_profile_prohibits_instant_reversal_and_auto_restart():
    architecture = load_json(ARCH)
    motion = architecture["motionProfile"]
    power = architecture["powerLossAndRestart"]

    assert motion["normalOperation"]["softStart"].startswith("required")
    assert motion["directionReversal"]["normalAutomaticReversal"] == "not-approved-at-this-stage"
    assert "never command instantaneous reversal" in motion["directionReversal"]["requirement"]
    assert power["powerLoss"]["automaticRestart"] is False
    assert "do not auto-resume previous motion command" in power["restartSequence"]


def test_feedback_and_fault_detection_use_fixed_side_passive_rotor_concept():
    architecture = load_json(ARCH)
    feedback = architecture["feedbackArchitecture"]
    faults = architecture["faultDetection"]

    assert "passive scale/targets/markers" in feedback["principle"]
    assert any("0.08 rpm" in req for req in feedback["requirements"])
    assert {"bearingSeizure", "foreignObjectOrSnag", "overspeed", "feedbackDisagreement", "failedRestart"}.issubset(faults["faults"])
    assert any("software fault detection never substitutes for secondary mechanical retention" in req for req in faults["requirements"])


def test_balance_architecture_consumes_mass_records_without_moving_setout():
    architecture = load_json(ARCH)
    balance = architecture["balanceAndTrim"]
    requirements = " ".join(balance["requirements"]).lower()

    assert "without moving controlled cable-exit coordinates" in balance["concept"]
    assert "issue #9" in requirements
    assert "replacement butterfly triggers balance review" in requirements
    assert balance["numericTrimRangeStatus"].startswith("TBD")


def test_dynamic_clearance_categories_and_staged_physical_testing_are_complete():
    architecture = load_json(ARCH)
    clearance = set(architecture["clearanceValidation"]["categories"])
    required_clearance = {
        "butterfly-to-butterfly",
        "cable-to-cable",
        "butterfly-to-cable",
        "field-to-fixed-head",
        "field-to-canopy",
        "carrier-to-fixed-canopy",
        "bearing/drive-to-service-components",
    }
    assert clearance == required_clearance

    program = architecture["dynamicTestProgram"]
    assert [stage["id"] for stage in program["stages"]] == ["T1", "T2", "T3", "T4"]
    assert program["stages"][-1]["name"] == "full 240-element factory pre-hang"
    assert "minimum observed dynamic clearances" in program["measurements"]
    assert "power interruption" in program["faultCases"]
    assert "occupied-space installation" in program["releaseRule"]


def test_calculation_framework_has_no_catalog_rating_shortcut():
    architecture = load_json(ARCH)
    calc = architecture["calculationFramework"]
    discipline = " ".join(architecture["researchDiscipline"]["rules"]).lower()

    assert "actual rotating mass and center of gravity" in " ".join(architecture["bearingArchitecture"]["selectionInputs"])
    assert "I_z = sum" in calc["rotatingMassAndInertia"]["equationReference"]
    assert "T_drive,required" in calc["driveTorque"]["equationReference"]
    assert "catalog maxima are not product design loads" in calc["bearingLoads"]["rule"]
    assert "do not convert catalog maximum load into vx4800 design load" in discipline


def test_candidate_research_remains_family_level_until_loads_exist():
    shortlist = load_json(SHORTLIST)
    bearings = {entry["candidateId"]: entry for entry in shortlist["bearingCandidates"]}
    drives = {entry["candidateId"]: entry for entry in shortlist["driveCandidates"]}
    feedback = {entry["candidateId"]: entry for entry in shortlist["feedbackCandidates"]}

    assert bearings["kaydon-slewing-ring-family"]["status"].endswith("not-selected")
    assert bearings["schaeffler-crossed-roller-family"]["status"].endswith("not-selected")
    assert drives["fixed-gearmotor-synchronous-ring-drive"]["status"] == "preferred-study-not-selected"
    assert drives["friction-wheel-drive"]["status"] == "not-preferred-primary-drive"
    assert feedback["fixed-readhead-passive-optical-ring"]["status"] == "shortlisted-reference-not-selected"
    assert "catalog data alone" in shortlist["selectionRule"]


def test_final_approval_is_impossible_with_open_required_gates():
    architecture = load_json(ARCH)
    gates = architecture["promotionGate"]
    required_gate_names = {
        "actualRotatingMassControlled",
        "centerOfGravityControlled",
        "productionMassVariationControlled",
        "bearingSelected",
        "bearingLoadCalculationApproved",
        "driveSelected",
        "driveTorqueCalculationApproved",
        "brakingArchitectureResolved",
        "serviceLockValidated",
        "secondaryRetentionValidated",
        "feedbackArchitectureValidated",
        "faultHandlingValidated",
        "dynamicClearanceValidated",
        "fullPreHangDynamicTestPassed",
        "maintenancePlanReleased",
    }
    assert set(gates) == required_gate_names
    assert architecture["finalSystemApproved"] is False
    assert not any(gates.values())

    schema = load_json(ARCH_SCHEMA)
    promoted = dict(architecture)
    promoted["finalSystemApproved"] = True
    errors = list(Draft202012Validator(schema).iter_errors(promoted))
    assert errors, "Schema must reject final approval while any required gate remains false"
