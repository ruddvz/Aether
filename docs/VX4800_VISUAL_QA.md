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

## Visualization revision 0.2.0 review

The 0.2.0 Cycles preview was produced by workflow run 33898059475 from source commit `8b1370130e150e2a1b349648d2d6d2eb61f7209b`.

Improvements visible in the render:

- the full canopy and controlled lower tail fit in frame;
- the overall descending vortex is readable;
- the canopy and carrier have clearer metal response;
- linked butterfly geometry has moved away from literal insect anatomy;
- the dark studio direction provides substantially more contrast than the original ivory stage.

Remaining defects:

1. The 240 suspension lines still form a bright curtain and compete with the butterflies.
2. The separate floor and backdrop planes create a visible diagonal studio horizon through the composition.
3. The lower fixture dissolves into an overexposed floor pool. Much of that pool comes from the conceptual 14-head beam study, which should not be conflated with clean product photography.
4. The first radial fan facet layout creates too many small reflective triangles, so the optical wings can read like silver glitter rather than transparent decorative glass.
5. The hero viewpoint is too high and reveals the canopy top surface, weakening the installed architectural-lighting reading.
6. Background illumination is still too bright and uneven for a clean optical-product baseline.

## Visualization revision 0.3.0 goals

- Keep all controlled transforms, IDs, 66/144/30 allocation and 14 fixed head positions unchanged.
- Reduce only the visualization display diameter and specular prominence of suspension lines, explicitly without making a rated hardware claim.
- Replace radial fan facets with broad perimeter facets and a large central optical face, all within the controlled nominal wing thickness envelope.
- Use a single matte dark product backdrop without a floor seam in the clean studio hero.
- Turn the 14 conceptual fixture beams off in clean product presets while retaining the 14 objects, their controlled positions and an explicit renderer override for later lighting studies.
- Lower the hero and canopy-detail viewpoints so the canopy is primarily read from below.
- Retain restrained key/fill/rim/top photographic lighting for edge definition rather than fixture-beam effects.

## Blender 5.2 rendering basis

Cycles remains the production renderer. The optical material uses full transmission, an IOR-based dielectric surface, very low surface roughness and light volume absorption. The scene keeps sufficient transmission bounces for stacked glass views. Refractive caustics are not treated as measured optical output and should only be enabled selectively where the render benefit justifies the noise/performance cost.
