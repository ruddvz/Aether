# VX4800 Blender visual QA

This document tracks render-quality findings for the AETHERIA VORTEX VX4800-BF-01 Blender visualization master. It is visualization QA only. Controlled engineering data, manufacturing decisions and measured photometry remain upstream authority.

## Baseline reviewed

The first Blender-native baseline was the Cycles CPU preview produced by the successful `Build VX4800 Blender master` workflow run 33891009803 from source commit `44960367dae48b840272fd0a7f92c66d880a080e`.

The scene itself validated correctly: 240 butterfly instances, 66 S / 144 M / 30 L, 240 main suspension splines, 720 yoke/lead splines, 14 fixed LED-head placeholders, 14 conceptual render lights and six named cameras.

## Highest-impact visual deficiencies in the baseline preview

1. The overall vortex silhouette is difficult to read because the fixture is rendered against a very bright ivory field with insufficient edge separation.
2. The hero camera does not show the complete fixture. The canopy is outside the frame and the lower tail is clipped.
3. Butterflies read as small pale shards rather than premium optical objects. The prior wing geometry is mostly flat and the body language is too literal/anatomical for the intended sculptural abstraction.
4. Optical transmission and refraction are not legible. Most butterflies render nearly white, with weak edge highlights and little internal value variation.
5. The dense suspension field is too visually dominant relative to the butterfly field.
6. The photographic light rig is too flat. Key, fill and rim hierarchy is weak and the right side of the image is overexposed.
7. Canopy, carrier and LED-head finishes have limited material separation and do not yet read as premium PVD/brushed/satin studies.
8. The fixed LED heads and their role are difficult to see in the hero image.
9. The studio stage creates distracting bright geometry and gives little useful scale or depth information.
10. The image has excess unstructured negative space while still failing to contain the full product height.

## Visualization revision 0.2.0 goals

- Preserve every controlled element transform, ID and 66/144/30 size allocation.
- Replace flat wing slabs with closed faceted optical wing geometry that stays within the controlled nominal butterfly thickness.
- Replace literal segmented insect anatomy with a restrained sculptural central spine.
- Keep the optical shader explicitly labelled as a visualization material study because the commercial butterfly material is not locked.
- Add subtle micro-roughness variation to metal finish studies without presenting shader values as supplier specifications.
- Separate fixture-integrated conceptual 14-head lighting from photographic render-stage lighting through explicit object metadata.
- Use a dark premium studio baseline with stronger key/fill/rim separation so glass edges and metal highlights become legible.
- Reframe the existing six cameras before adding any new camera set.
- Reduce suspension display diameter as a visualization choice only, with explicit metadata that it is not a rated suspension diameter.
- Increase the quick Cycles preview to 64 samples with adaptive sampling so render reviews are less dominated by low-sample noise.

## Blender 5.2 rendering basis

Cycles remains the production renderer. The optical material uses full transmission, an IOR-based dielectric surface, very low surface roughness and light volume absorption. The scene keeps sufficient transmission bounces for stacked glass views. Refractive caustics are not treated as measured optical output and should only be enabled selectively where the render benefit justifies the noise/performance cost.
