# VX4800 kinetic risk-assessment input

Date: 2026-09-04

Status: hazard-identification input, not a released risk assessment.

This document accompanies `fixtures/vx4800/kinetics/risk-register-v1.json`.

The rotating-carrier track now has enough architecture to identify hazards, but not enough physical evidence to assign final risk estimates or safety-related control performance.

## Current standards inputs

`ISO 12100:2010` remains the current published ISO machinery risk-assessment/risk-reduction methodology standard as of this review. ISO states that the 2010 edition was reviewed and confirmed in 2022 and remains current while a replacement draft is under development.

Source: https://www.iso.org/standard/51528.html

`ISO 13850:2015` remains the current published ISO emergency-stop principles standard as of this review.

Source: https://www.iso.org/standard/59970.html

These are applicability inputs only. The repository does not claim that VX4800 is a machine within every jurisdictional definition, that either standard alone defines the released conformity route, or that compliance has been achieved.

## Why no PL, SIL or category is assigned

The final risk assessment must first establish:

- intended use and reasonably foreseeable misuse;
- hazard severity/exposure/avoidance method selected by the responsible safety engineering process;
- which risk-reduction measures are inherently mechanical;
- which functions must be implemented in safety-related controls;
- whether emergency stop reduces risk for the relevant scenarios;
- required validation and diagnostic coverage;
- residual risk/instructions.

Without that work, attaching a PL, SIL or category to an encoder, brake or emergency stop would be a false claim.

The current risk register therefore records candidate safety-related functions with `performanceLevelOrSil: null`.

## Mechanical hazard families identified

The register currently includes:

1. fall or major displacement of the complete rotating field;
2. impact/overload when secondary retention engages;
3. unexpected start or automatic restart;
4. uncontrolled/excess carrier speed;
5. pinch/shear/trapping at fixed/rotating canopy interfaces;
6. suspension/foreign-object snag;
7. dynamic butterfly/cable/fixed-head/canopy collision;
8. uncontrolled manual release/free motion;
9. service-lock partial engagement or false indication;
10. loose trim/fastener/service hardware;
11. butterfly material/attachment fracture;
12. suspension cable/gripper/bridle failure;
13. kinetic electrical state not matching mechanical state;
14. severe suspended-field transient during fault/power-loss stop;
15. unintended normal-operation contact with secondary retention;
16. installation/service work-at-height and dropped-object hazards.

The list is intentionally broader than the rotating mechanism alone because a useful risk assessment must cover its interfaces with the suspension, butterfly, electrical and site-structure tracks.

## Candidate safety-related functions

The following are currently candidates only:

- prevent automatic restart after power restoration or fault reset;
- stop/inhibit motion on overspeed or feedback disagreement;
- inhibit powered motion while the mechanical service lock is engaged;
- stop/inhibit repeated motion after abnormal drag/jam;
- establish a held non-moving state after normal propulsion power is lost.

Whether each function needs a safety-related control implementation, and at what performance, remains open.

## Mechanical measures that do not depend on software

The architecture deliberately retains several risk-reduction measures outside software:

- primary engineered structural load path;
- independent secondary-retention concept;
- positive mechanical service lock;
- direct-carrier holding/brake architecture under qualification;
- passive rotating field with no powered rotor electronics;
- guarded fixed/rotating pinch zones;
- positively retained/captured trim hardware;
- physical full-field clearance testing.

Software monitoring can improve detection and response. It does not replace these mechanical measures.

## Next risk-assessment work

Before `finalRiskAssessmentReleased` can become true:

- define intended use and foreseeable misuse;
- select/approve the formal risk-estimation method;
- review the hazard register with mechanical, electrical, structural, product and certification owners;
- link every risk-reduction measure to controlled design evidence;
- allocate any safety-related control functions to Issue #11/final controls;
- resolve emergency-stop need and behaviour;
- validate the measures through the staged physical test plan;
- document residual risks, installation/service instructions and configuration boundaries.

Until then every risk-register promotion gate remains false.
