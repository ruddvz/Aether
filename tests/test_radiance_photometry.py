from pathlib import Path
import json
import math

import pytest
from jsonschema import Draft202012Validator

from scripts.validate_radiance_photometry import (
    RadianceValidationError,
    interpolate,
    load_toolchain,
    make_samples,
    validate,
)
from tools.photometry.ies_lm63 import parse_ies

ROOT = Path(__file__).resolve().parents[1]
SYNTHETIC = ROOT / "tests/fixtures/photometry/synthetic-narrow.ies"
TOOLCHAIN = ROOT / "fixtures/vx4800/photometry/radiance/toolchain-v1.json"
REPORT_SCHEMA = ROOT / "schemas/aether-radiance-validation-report.schema.json"


def test_radiance_toolchain_is_pinned_to_stable_release_and_digest():
    toolchain = load_toolchain(TOOLCHAIN)
    radiance = toolchain["radiance"]
    assert radiance["release"] == "6.0.2"
    assert radiance["tag"] == "rad6R0P2"
    assert radiance["linuxAsset"] == "Radiance_c1700d56_Linux.zip"
    assert radiance["linuxAssetSha256"] == "04ee53cafbb64b943a53616b3d0ee379dd7ef80379c83aa7a145e547d9809c28"
    assert set(radiance["requiredExecutables"]) == {"ies2rad", "oconv", "rtrace"}


def test_toolchain_never_promotes_synthetic_or_radiance_only_to_product_authority():
    toolchain = load_toolchain(TOOLCHAIN)
    boundary = toolchain["validationBoundary"]
    assert boundary["radianceIsIndependentOfAetheriaParser"] is True
    assert boundary["syntheticFixtureCanValidatePipelineOnly"] is True
    assert boundary["syntheticFixtureCanQualifyProductPhotometry"] is False
    assert boundary["supplierOrLabRawIesRequiredForProductValidation"] is True
    assert boundary["rawIesSha256MustBeControlled"] is True
    assert boundary["exactHeadOpticConfigurationMustBeControlled"] is True
    assert boundary["radiancePassAloneApprovesLuminaire"] is False


def test_report_schema_is_valid_and_product_approved_is_const_false():
    schema = json.loads(REPORT_SCHEMA.read_text())
    Draft202012Validator.check_schema(schema)
    approved = schema["properties"]["summary"]["properties"]["productPhotometryApproved"]
    assert approved["const"] is False


def test_interpolation_is_linear_and_bounded():
    assert interpolate([0, 10, 20], [100, 50, 0], 5) == pytest.approx(75)
    assert interpolate([0, 10, 20], [100, 50, 0], 10) == pytest.approx(50)
    with pytest.raises(ValueError):
        interpolate([0, 10, 20], [100, 50, 0], 21)


def test_constant_plane_sampling_uses_candela_ratio_times_cos_cubed():
    parsed = parse_ies(SYNTHETIC)
    samples = {sample.angle_deg: sample for sample in make_samples(parsed, [0.0, 10.0, 20.0], 10.0)}
    assert samples[0.0].expected_ratio == pytest.approx(1.0)
    assert samples[10.0].expected_candela == pytest.approx(30.0)
    assert samples[10.0].expected_ratio == pytest.approx((30.0 / 1000.0) * math.cos(math.radians(10)) ** 3)
    assert samples[20.0].expected_candela == pytest.approx(3.0)
    assert samples[20.0].expected_ratio == pytest.approx((3.0 / 1000.0) * math.cos(math.radians(20)) ** 3)
    assert samples[20.0].x_m == pytest.approx(10.0 * math.tan(math.radians(20)))
    assert samples[20.0].z_m == pytest.approx(-10.0)


def test_synthetic_input_requires_explicit_opt_in_before_radiance_lookup(tmp_path):
    with pytest.raises(RadianceValidationError, match="--allow-synthetic-test"):
        validate(
            SYNTHETIC,
            tmp_path,
            provenance="synthetic-test",
            allow_synthetic_test=False,
            configuration_id=None,
            configuration_controlled=False,
            toolchain=load_toolchain(),
        )


def test_controlled_configuration_requires_identifier_before_radiance_lookup(tmp_path):
    with pytest.raises(RadianceValidationError, match="--configuration-id"):
        validate(
            SYNTHETIC,
            tmp_path,
            provenance="supplier",
            allow_synthetic_test=False,
            configuration_id=None,
            configuration_controlled=True,
            toolchain=load_toolchain(),
        )


def test_synthetic_fixture_is_explicitly_not_product_photometry():
    text = SYNTHETIC.read_text()
    assert "NOT PRODUCT PHOTOMETRY" in text
    assert "AETHERIA TEST ONLY" in text
