from __future__ import annotations

from dataclasses import dataclass, asdict
from typing import Any


ROLE_TARGETS = {
    "deep-tail narrow": {"quantity": 4},
    "mid-field spot": {"quantity": 6},
    "upper-field flood": {"quantity": 4},
}


@dataclass
class Finding:
    severity: str  # pass | warning | blocker
    code: str
    message: str
    configuration: str | None = None


def _role_spec(brief: dict, role: str) -> dict | None:
    for item in brief.get("optics", []):
        if item.get("role") == role:
            return item
    return None


def evaluate_candidate(candidate: dict, brief: dict) -> dict:
    findings: list[Finding] = []
    cfgs = candidate.get("configurations", [])
    cfg_by_role: dict[str, list[dict]] = {}
    for cfg in cfgs:
        cfg_by_role.setdefault(cfg.get("role", "other"), []).append(cfg)

    if not candidate.get("review", {}).get("exactConfigurationConfirmed"):
        findings.append(Finding("blocker", "exact-configuration-unconfirmed", "Exact LED/CCT/optic configuration is not confirmed."))
    else:
        findings.append(Finding("pass", "exact-configuration-confirmed", "Exact configuration is confirmed."))

    if not candidate.get("review", {}).get("officialPhotometryAvailable"):
        findings.append(Finding("blocker", "official-photometry-missing", "Official supplier/laboratory photometry is not available."))
    else:
        findings.append(Finding("pass", "official-photometry-available", "Official photometry is available."))

    cct_target = brief["lightQuality"]["cctK"]
    cri_min = brief["lightQuality"]["criMinimum"]
    power_min, power_max = brief["electricalTargets"]["powerPerHeadWPreliminaryRange"]

    for role, requirement in ROLE_TARGETS.items():
        role_cfgs = cfg_by_role.get(role, [])
        if not role_cfgs:
            findings.append(Finding("blocker", "role-missing", f"No exact configuration supplied for {role}.", role))
            continue

        cfg = role_cfgs[0]
        label = cfg.get("exactModelCode") or role
        spec = _role_spec(brief, role)

        if not cfg.get("exactModelCode"):
            findings.append(Finding("blocker", "exact-model-code-missing", "Exact model/configuration code is not confirmed.", role))
        if not cfg.get("opticCode"):
            findings.append(Finding("blocker", "optic-code-missing", "Exact optic code is not confirmed.", label))

        cct = cfg.get("cctK")
        if cct is None:
            findings.append(Finding("blocker", "cct-unconfirmed", f"Exact CCT is not confirmed; controlled target is {cct_target} K.", label))
        elif cct != cct_target:
            findings.append(Finding("blocker", "cct-mismatch", f"CCT {cct} K does not match controlled research target {cct_target} K.", label))
        else:
            findings.append(Finding("pass", "cct-match", f"CCT matches {cct_target} K target.", label))

        cri = cfg.get("cri")
        if cri is None:
            findings.append(Finding("blocker", "cri-unconfirmed", f"Exact CRI is not confirmed; minimum is {cri_min}.", label))
        elif cri < cri_min:
            findings.append(Finding("blocker", "cri-below-minimum", f"CRI {cri:g} is below required minimum {cri_min}.", label))
        else:
            findings.append(Finding("pass", "cri-pass", f"CRI {cri:g} meets minimum {cri_min}.", label))

        beam = cfg.get("beamAngleDegPublished")
        if spec:
            lo, hi = spec["acceptableRangeDeg"]
            if beam is None:
                findings.append(Finding("warning", "beam-unpublished", f"Published beam angle is missing; IES must be used to verify the {lo}-{hi}° role.", label))
            elif not (lo <= beam <= hi):
                findings.append(Finding("blocker", "beam-out-of-range", f"Published beam {beam:g}° is outside the {lo}-{hi}° acceptance window.", label))
            else:
                findings.append(Finding("pass", "beam-in-range", f"Published beam {beam:g}° is inside the {lo}-{hi}° acceptance window.", label))

        power = cfg.get("powerW")
        if power is None:
            findings.append(Finding("warning", "power-missing", "Input power is not recorded.", label))
        elif not (power_min <= power <= power_max):
            findings.append(Finding("warning", "power-outside-preliminary-range", f"Power {power:g} W is outside preliminary {power_min}-{power_max} W target; engineering review required.", label))
        else:
            findings.append(Finding("pass", "power-in-range", f"Power {power:g} W is inside preliminary range.", label))

        pstatus = cfg.get("photometryStatus")
        if pstatus in {"parsed", "verified"}:
            if cfg.get("iesPath") and cfg.get("iesSha256"):
                findings.append(Finding("pass", "ies-controlled", f"IES asset is {pstatus} with path and SHA-256 recorded.", label))
            else:
                findings.append(Finding("blocker", "ies-integrity-missing", f"Photometry status is {pstatus} but path/SHA-256 is incomplete.", label))
        elif pstatus in {"downloaded", "linked"}:
            findings.append(Finding("warning", "ies-not-yet-verified", f"Photometry is only {pstatus}; ingest and verify it before approval.", label))
        else:
            findings.append(Finding("blocker", "ies-missing", "No controlled IES photometry is attached.", label))

        if cfg.get("lumens") is None:
            findings.append(Finding("warning", "lumens-missing", "Delivered lumen output for the exact configuration is not recorded.", label))

        if not cfg.get("driverModel"):
            findings.append(Finding("warning", "driver-model-missing", "Exact driver/power-supply model is not recorded.", label))

        dimming = {str(x).lower() for x in cfg.get("dimming", [])}
        has_dali = any("dali" in x for x in dimming)
        if brief["electricalTargets"].get("daliPreferred") and not has_dali:
            findings.append(Finding("warning", "dali-unavailable", "DALI is preferred but not recorded for this configuration.", label))
        elif has_dali:
            findings.append(Finding("pass", "dali-available", "DALI control is available or documented through a manufacturer gateway.", label))

        dims = cfg.get("dimensionsMm")
        if dims is None:
            findings.append(Finding("warning", "dimensions-missing", "Physical head dimensions are not recorded.", label))

    if not candidate.get("sources", {}).get("productPage"):
        findings.append(Finding("blocker", "product-source-missing", "Official product page is missing."))
    if not candidate.get("sources", {}).get("datasheet"):
        findings.append(Finding("blocker", "datasheet-missing", "Official datasheet is missing."))

    target_review = candidate.get("review", {})
    if target_review.get("meetsPhysicalTarget") is False:
        findings.append(Finding("warning", "physical-target-miss", "Candidate is documented as missing the preferred physical target."))
    elif target_review.get("meetsPhysicalTarget") is True:
        findings.append(Finding("pass", "physical-target-pass", "Candidate is documented as meeting the preferred physical target."))

    if not candidate.get("finishOptions"):
        findings.append(Finding("warning", "finish-options-missing", "Finish options are not recorded."))

    blocker_count = sum(f.severity == "blocker" for f in findings)
    warning_count = sum(f.severity == "warning" for f in findings)
    pass_count = sum(f.severity == "pass" for f in findings)
    decision = "reject-for-now" if blocker_count else ("shortlist-with-warnings" if warning_count else "technical-shortlist")

    return {
        "candidateId": candidate.get("candidateId"),
        "manufacturer": candidate.get("manufacturer"),
        "family": candidate.get("family"),
        "decision": decision,
        "counts": {"blocker": blocker_count, "warning": warning_count, "pass": pass_count},
        "findings": [asdict(f) for f in findings],
    }


def render_markdown(review: dict) -> str:
    lines = [
        f"# Photometry candidate review: {review['manufacturer']} {review['family']}",
        "",
        f"Decision: **{review['decision']}**",
        "",
        f"Blockers: {review['counts']['blocker']}  ",
        f"Warnings: {review['counts']['warning']}  ",
        f"Passes: {review['counts']['pass']}",
        "",
        "| Severity | Check | Configuration | Finding |",
        "| --- | --- | --- | --- |",
    ]
    for f in review["findings"]:
        lines.append(f"| {f['severity']} | `{f['code']}` | {f.get('configuration') or '-'} | {f['message']} |")
    lines.append("")
    lines.append("This review is an engineering research screen, not product approval.")
    return "\n".join(lines) + "\n"
