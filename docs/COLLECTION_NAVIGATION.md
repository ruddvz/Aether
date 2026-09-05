# AETHERIA collection navigation

AETHERIA collections are catalog taxonomy. They do not create engineering, manufacturing, photometry, certification or release authority.

## Source of truth

`project.json` defines which collection identities are registered and how they are presented in the public catalog. Product membership is not duplicated in the product registry. A registered product belongs to the collection declared by its canonical fixture at:

`identity.collection`

That rule prevents the catalog and the controlled fixture from silently disagreeing about product identity.

The current registered collection set is:

- `FLIGHT` — active
- `OCEAN` — planned
- `BOTANICA` — planned
- `CELESTIAL` — planned
- `ABSTRACT MOTION` — planned

VORTEX `VX4800-BF-01` is currently the only registered product and its canonical fixture places it in `FLIGHT`.

The four planned collections intentionally contain zero products. The repository does not create placeholder models, invented SKUs, fake launch dates or speculative engineering data to fill an empty collection page.

## Project registry contract

`schemas/aether-project.schema.json` validates the project registry. The registry controls:

- repository identity;
- default registered product;
- public schema paths;
- collection slug, identity, display name, status and sort order;
- product source paths and public route metadata.

Repository validation then cross-checks every product record against the canonical fixture referenced by `fixtureManifest`.

For each registered product the validator requires:

- fixture brand matches the project brand;
- fixture name matches product `displayName`;
- fixture `productCode` matches product `model`;
- design revision matches;
- presentation revision matches;
- fixture collection is registered;
- fixture IDs and product codes are unique;
- product public paths are unique and match the product slug;
- all referenced product source files exist.

Collection state is also checked. An `active` collection must contain at least one registered product. A `planned` collection must contain none. A product entering a planned collection therefore requires an explicit collection-state change rather than silently becoming public.

## Generated Pages outputs

`scripts/build_site.py` generates:

- `/collections.json` — machine-readable collection registry and membership summary;
- `/collections/flight/`;
- `/collections/ocean/`;
- `/collections/botanica/`;
- `/collections/celestial/`;
- `/collections/abstract-motion/`.

The root catalog includes navigation to every registered collection.

Active collection pages list their actual registered products. Planned empty pages explicitly state that no registered products are currently published in that collection.

Generated `products.json` records also include the canonical collection identity, slug, display name and collection route so downstream browser tools do not need to rediscover the mapping.

## Adding a product

Adding a product requires all of the following in one reviewed change:

1. Add a canonical fixture and supporting controlled product files.
2. Set the fixture `identity.collection` to an already registered collection identity.
3. Add the product record to `project.json` with source paths and public path.
4. If the target collection was `planned`, deliberately change its registry status to `active`.
5. Pass project-schema validation and canonical fixture cross-checks.
6. Pass product build, Pages build and public-entry validation.

Adding a product does not require editing collection-page HTML. Collection membership and routes are generated from registry and canonical fixture data.

## What collection navigation does not mean

A collection page is a discovery and catalog surface only. It does not imply that a listed product is production released, available for sale, certified for a market, approved for a project, or physically qualified beyond the status expressed by its controlled product data.
