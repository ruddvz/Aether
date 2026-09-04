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

## Visualization revision 0.3.0 review

The 0.3.0 Cycles preview was produced by workflow run 33898655806 from source commit `d4c99ab1c8323123bca268d3a56fdbff37908eeb`.

Improvements visible in the render:

- the floor and diagonal studio seam are gone;
- the conceptual 14-head beams are suppressed in the clean preview instead of blowing out the lower stage;
- the hero viewpoint now reads the canopy from below;
- the dark background gives the complete controlled fixture silhouette strong separation;
- broad optical wing faces reduce the earlier glitter/fan-facet effect.

Remaining defects:

1. Suspension is still brighter than intended and remains visually competitive with the butterfly field.
2. At full-fixture distance, transparent wings naturally collapse into specular edge highlights, so the hero render alone cannot prove whether the optical material is believable.
3. A close optical view is needed before changing glass parameters further; otherwise lookdev risks tuning the material to compensate for a camera-scale problem.

## Visualization revision 0.4.0 goals

- Further quiet the suspension appearance using only visualization display diameter and roughness changes, with no rated-hardware claim.
- Add a single butterfly macro camera aimed at the controlled `VX-001` L instance without moving or altering the instance.
- Render both hero and macro previews in CI so every lookdev revision is judged at fixture scale and optical-detail scale.
- Introduce a subtle blue-green edge absorption study in the glass while explicitly labelling the absorption density as a visualization lookdev value rather than a commercial material property.
- Keep thin-film interference disabled. Blender 5.2 supports it, but rainbow interference would be inappropriate without a specified optical coating and would push the material toward fantasy glass.

## Blender 5.2 rendering basis

Cycles remains the production renderer. The optical material uses full transmission, an IOR-based dielectric surface, very low surface roughness and light volume absorption. The scene keeps sufficient transmission bounces for stacked glass views. Refractive caustics are not treated as measured optical output and should only be enabled selectively where the render benefit justifies the noise/performance cost.
