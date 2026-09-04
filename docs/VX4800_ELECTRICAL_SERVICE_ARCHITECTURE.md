# VX4800 electrical and service architecture

Date: 2026-09-04

Status: engineering-development input, not construction release.

This document defines the electrical/service architecture that can be fixed before final accent-head, driver, motor and market-supply selections are complete.

## Core architecture decision

Keep lighting and kinetic electrical systems in the fixed canopy.

The 14 accent heads are fixed relative to the canopy. The 240 butterflies, their suspension lines and the rotating carrier have no planned electrical loads. Therefore the present architecture does not require a slip ring for lighting power or control.

This is an intentional simplification and reliability benefit, not a permanent prohibition. If a future design introduces powered devices, sensors or displays on the rotating carrier, the rotary power/data-transfer problem must be reopened through change control.

## Electrical domains

### Lighting domain

Purpose: power and control the 14 fixed adjustable accent heads.

Requirements:

- independently isolatable from the kinetic drive for service;
- all power supplies/control gear in the fixed canopy or another approved fixed service zone;
- each head replaceable without destructive canopy work;
- head identifiers linked to the controlled LED setout;
- final driver topology selected only after the exact head family/configuration is controlled;
- DALI-2 preferred where the selected control gear supports it.

The current conceptual optical roles are:

- 4 deep-tail narrow heads;
- 6 mid-field spot heads;
- 4 upper-field flood heads.

These roles are commissioning/scene intent, not a requirement to hardwire three electrical circuits. Where the final DALI/control-gear topology allows it, software-defined groups and scenes are preferred because optics or focus may change during commissioning without rewiring the fixture.

## DALI-2 direction

DALI is standardized under IEC 62386. DALI-2 extends certification and interoperability testing across control gear and control devices.

A DALI system includes control gear, control devices and a powered DALI bus. DALI power and data share the same two-wire pair. The final VX4800 DALI architecture must therefore include a defined bus power supply and application controller or other project control interface where DALI is released.

Do not confuse the DALI bus with LED power wiring.

The exact DALI products, addresses, groups and scenes remain commissioning outputs, not current controlled product data.

Official DALI Alliance references:

- https://www.dali-alliance.org/dali/
- https://www.dali-alliance.org/dali/systems.html
- https://www.dali-alliance.org/dali/keyfeatures.html

## Candidate-specific 24 V reference

Precision Lighting by Luminii Evo 16 remains the current photometric-data reference candidate, not the final head.

Its current manufacturer page describes a 24 V constant-voltage single-source LED spotlight with an onboard 24 V DC driver and an external AC-to-24 V power supply requirement, and lists DALI and 1-10 V dimming.

That makes a fixed-canopy 24 V distribution architecture technically plausible for the Precision path. It does not make 24 V the canonical AETHERIA architecture.

If Reggiani or another finalist is selected, its exact power/control topology governs.

Reference:

- https://www.luminii.com/product/evo-16/

## Driver topology studies

### One control gear / PSU channel per head

Preferred serviceability study, where supported by the selected luminaire family.

Advantages:

- individual fault localization;
- individual isolation/replacement;
- maximum addressing flexibility;
- a single failed control gear affects one head.

Tradeoffs:

- component count;
- canopy space;
- heat;
- wiring count;
- cost.

### Manufacturer multi-head power architecture

Supplier-dependent alternative.

Advantages:

- fewer power supplies;
- potentially less occupied canopy volume;
- potentially simpler AC-side distribution.

Tradeoffs:

- one failure may affect several heads;
- head-level addressing may be reduced depending on architecture;
- output/channel protection must be understood;
- service replacement can affect multiple heads.

Do not choose between these architectures until exact head/control gear data is available.

## Kinetic electrical domain

The kinetic electrical system is separate from lighting.

It will eventually include some combination of:

- motor;
- motor drive/controller;
- braking or safe stopping function;
- speed/position feedback;
- motion permissives/interlocks;
- service controls;
- emergency stop/safety chain as required by the released risk assessment;
- jam/abnormal-motion detection where required.

The motor, drive, braking function and safety performance are unresolved. This document does not select them.

The preferred physical architecture keeps the motor/drive electronics fixed. Mechanical torque crosses the fixed/rotating interface; routine electrical wiring should not.

## Auxiliary / sensing domain

Prefer fixed, non-contact sensing wherever practical. Examples may eventually include position reference, speed sensing or canopy condition sensors.

Any sensor that is proposed on the rotating carrier must justify its power/data transfer method. Do not quietly introduce a rotating wire bundle or slip ring into a concept whose main reliability advantage is a passive rotating field.

## Service access

The canopy must be designed around service zones, not packed after mechanical design is complete.

Required service principles:

- drivers/control gear accessible behind removable service panels;
- lighting and kinetic modules independently replaceable;
- no routine electrical service inside the moving sweep while motion is enabled;
- mechanical lockout/restraint procedure before access near the carrier/bearing/drive;
- terminal blocks and connectors accessible without removing the 240 suspension lines;
- cable routes kept clear of the bearing, drive, carrier sweep, gripper service zones and structural interfaces;
- strain relief at removable modules and head feeds;
- sufficient conductor slack for service without entering moving zones;
- no destructive finish removal for normal driver/head/controller replacement.

## Identification and commissioning

Every serviceable component should have a unique controlled ID.

At minimum:

- head ID linked to the 14-head LED setout;
- driver/control gear/PSU ID;
- connector/terminal ID;
- lighting versus kinetic domain label;
- DALI address/group/scene record after commissioning where DALI is selected;
- replacement part number and approved configuration reference after supplier selection.

A replacement head must not depend on a technician visually guessing which optical role it serves.

## Protective earthing and bonding

Final electrical class and protective-earth architecture are not yet released.

However, one rule is already fixed: do not use bearings, sliding contacts or incidental mechanical contact as an intentional protective-earth current path.

If the released design is Class I or otherwise requires protective bonding of accessible conductive parts, provide a deliberate bonding architecture and verify continuity through the actual service/rotating assembly design.

The exact bonding method around the rotating carrier remains part of the final electrical/mechanical safety review.

## Supply variants

Do not hardcode a universal site supply into the product while target markets include India, IEC-oriented markets and North America.

The final release should define controlled supply variants with exact approved PSUs/control gear and protective devices for each intended market/project supply.

The product architecture can remain common while the input power module varies.

## Thermal design

Drivers and motor-control electronics are heat sources inside a relatively shallow 2400 × 1500 × 150 mm canopy.

Before release:

- identify every power dissipating device;
- obtain manufacturer ambient/derating requirements;
- assess worst-case concurrent lighting and kinetic operation;
- verify local temperatures in the installed orientation;
- ensure decorative finishes and nearby wiring remain inside ratings;
- keep service modules from blocking required airflow or heat conduction;
- validate with first-article thermal testing where analysis alone is insufficient.

Do not assume the large canopy automatically makes thermal performance acceptable.

## Wiring and voltage drop

Final conductor sizes cannot be selected until exact head input voltage/current, driver topology, run lengths, installation method, temperature and market requirements are known.

For a future low-voltage head architecture, calculate voltage drop to the most remote head and verify operation at worst-case supply and load conditions.

For constant-current architectures, follow the selected driver/head manufacturer's wiring constraints.

Do not mix constant-voltage and constant-current assumptions across candidate families.

## First-article electrical test direction

The released test plan should include, as applicable to the final architecture:

- protective-earth continuity/bonding;
- insulation/dielectric tests required by the selected certification path;
- input current/power and abnormal condition checks;
- driver/control gear functional tests;
- all 14 head outputs and optics/configuration identity;
- dimming and scene behavior;
- power interruption/restart behavior;
- lighting-domain isolation;
- kinetic-domain isolation;
- emergency/safe stop behavior after the kinetic safety design is released;
- thermal soak;
- service replacement of representative head/driver/controller modules;
- post-service functional revalidation.

Exact compliance tests must be finalized with the certification/test house and released product architecture.

## Promotion gate

The electrical architecture remains conceptual until all of the following are controlled:

1. exact accent head selected;
2. exact driver/power topology selected;
3. project/release supply variant defined;
4. lighting control gear controlled;
5. DALI commissioning architecture controlled where applicable;
6. protective earthing/bonding resolved;
7. wiring and voltage-drop calculations complete;
8. canopy thermal validation passed;
9. service access physically validated;
10. kinetic electrical safety architecture resolved;
11. first-article electrical tests passed.

## Explicit non-claims

This document does not claim:

- final input voltage;
- final driver count;
- final DALI addresses/groups;
- final motor/drive;
- final safety category or emergency-stop performance;
- final conductor sizes;
- final protection device ratings;
- final electrical class;
- certification or construction release.
