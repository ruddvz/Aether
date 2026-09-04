from pathlib import Path
import importlib.util
import json

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts/assemble_vx4800_photometry_role_set.py"
SCHEMA = ROOT / "schemas/aether-photometry-role-set.schema.json"
FIXTURE = ROOT / "fixtures/vx4800/fixture.json"
BRIEF = ROOT / "fixtures/vx4800/photometry/selection-brief.json"

ROLES = (
    ("deep-tail narrow", "N", "CFG-N", "UN"),
    ("mid-field spot", "S", "CFG-S", "ME"),
    ("upper-field flood", "F", "CFG-F", "FL"),
)


def load_module():
    spec = importlib.util.spec_from_file_location("assemble_vx4800_photometry_role_set", SCRIPT)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def write_package(path: Path, *, role: str, package_suffix: str, configuration_id: str, optic: str, manufacturer: str = "Test Manufacturer", family: str = "Test Family", cct: int = 3000, eligible: bool = True) -> Path:
    value = {
        "schemaVersion": "1.0.0",
        "fixtureId": "vx4800-bf-01",
        "packageId": f"test-{package_suffix.lower()}",
        "authority": "derived-evidence-package",
        "status": "eligible-for-further-review" if eligible else "incomplete",
        "configuration": {
            "configurationId": configuration_id,
            "candidateId": "test-head",
            "manufacturer": manufacturer,
            "family": family,
            "role": role,
            "exactModelCode": f"TEST-{package_suffix}-30K",
            "opticCode": optic,
            "cctK": cct,
            "candidateExactConfigurationConfirmed": eligible,
        },
        "eligibility": {
            "packageEligibleForFurtherReview": eligible,
            "productPhotometryApproved": False,
        },
    }
    path.write_text(json.dumps(value, indent=2) + "\n", encoding="utf-8")
    return path


def make_role_paths(tmp_path: Path, **overrides):
    paths = {}
    for role, suffix, configuration_id, optic in ROLES:
        options = overrides.get(role, {})
        paths[role] = write_package(
            tmp_path / f"{suffix}.json",
            role=options.get("role", role),
            package_suffix=suffix,
            configuration_id=options.get("configuration_id", configuration_id),
            optic=optic,
            manufacturer=options.get("manufacturer", "Test Manufacturer"),
            family=options.get("family", "Test Family"),
            cct=options.get("cct", 3000),
            eligible=options.get("eligible", True),
        )
    return paths


def test_three_exact_role_packages_become_system_validation_input_not_product_approval(tmp_path):
    module = load_module()
    result = module.assemble_role_set(
        fixture_path=FIXTURE,
        selection_brief_path=BRIEF,
        role_package_paths=make_role_paths(tmp_path),
    )

    schema = json.loads(SCHEMA.read_text(encoding="utf-8"))
    errors = list(Draft202012Validator(schema).iter_errors(result))
    assert not errors, [error.message for error in errors]
    assert result["status"] == "eligible-for-system-validation"
    assert [entry["quantity"] for entry in result["roles"]] == [4, 6, 4]
    assert sum(entry["quantity"] for entry in result["roles"]) == 14
    assert result["consistency"]["allSystemInputChecksPass"] is True
    assert result["eligibility"]["roleSetEligibleForSystemValidation"] is True
    assert result["eligibility"]["full14HeadPhotometricValidationCompleted"] is False
    assert result["eligibility"]["applicationPerformanceValidated"] is False
    assert result["eligibility"]["productPhotometryApproved"] is False


def test_duplicate_configuration_ids_are_blocked(tmp_path):
    module = load_module()
    result = module.assemble_role_set(
        fixture_path=FIXTURE,
        selection_brief_path=BRIEF,
        role_package_paths=make_role_paths(
            tmp_path,
            **{
                "mid-field spot": {"configuration_id": "CFG-N"},
            },
        ),
    )
    assert result["consistency"]["configurationIdsUnique"] is False
    assert result["eligibility"]["roleSetEligibleForSystemValidation"] is False
    assert result["status"] == "incomplete"


def test_wrong_package_role_is_blocked(tmp_path):
    module = load_module()
    result = module.assemble_role_set(
        fixture_path=FIXTURE,
        selection_brief_path=BRIEF,
        role_package_paths=make_role_paths(
            tmp_path,
            **{
                "upper-field flood": {"role": "mid-field spot"},
            },
        ),
    )
    assert result["consistency"]["allRoleNamesMatchPackages"] is False
    assert result["eligibility"]["roleSetEligibleForSystemValidation"] is False


def test_wrong_cct_is_blocked(tmp_path):
    module = load_module()
    result = module.assemble_role_set(
        fixture_path=FIXTURE,
        selection_brief_path=BRIEF,
        role_package_paths=make_role_paths(
            tmp_path,
            **{
                "deep-tail narrow": {"cct": 2700},
            },
        ),
    )
    assert result["consistency"]["allCctMatch"] is False
    assert result["eligibility"]["roleSetEligibleForSystemValidation"] is False


def test_incomplete_exact_package_is_blocked(tmp_path):
    module = load_module()
    result = module.assemble_role_set(
        fixture_path=FIXTURE,
        selection_brief_path=BRIEF,
        role_package_paths=make_role_paths(
            tmp_path,
            **{
                "mid-field spot": {"eligible": False},
            },
        ),
    )
    assert result["consistency"]["allRolePackagesEligible"] is False
    assert result["eligibility"]["roleSetEligibleForSystemValidation"] is False


def test_single_family_strategy_is_preferred_but_not_falsely_mandatory(tmp_path):
    module = load_module()
    result = module.assemble_role_set(
        fixture_path=FIXTURE,
        selection_brief_path=BRIEF,
        role_package_paths=make_role_paths(
            tmp_path,
            **{
                "upper-field flood": {"manufacturer": "Alternate Manufacturer", "family": "Alternate Family"},
            },
        ),
    )
    assert result["consistency"]["singleManufacturerFamily"] is False
    assert result["consistency"]["allSystemInputChecksPass"] is True
    assert result["eligibility"]["roleSetEligibleForSystemValidation"] is True


def test_controlled_product_binding_is_4_6_4_and_14_heads():
    fixture = json.loads(FIXTURE.read_text(encoding="utf-8"))
    brief = json.loads(BRIEF.read_text(encoding="utf-8"))
    quantities = {entry["role"]: entry["quantity"] for entry in brief["optics"]}
    assert quantities == {
        "deep-tail narrow": 4,
        "mid-field spot": 6,
        "upper-field flood": 4,
    }
    assert fixture["optical"]["emitters"][0]["quantity"] == 14
    assert sum(quantities.values()) == 14


def test_role_set_script_cannot_approve_product_photometry():
    text = SCRIPT.read_text(encoding="utf-8")
    assert '"productPhotometryApproved": False' in text
    assert '"full14HeadPhotometricValidationCompleted": False' in text
    assert '"applicationPerformanceValidated": False' in text
    assert "--product-photometry-approved" not in text
