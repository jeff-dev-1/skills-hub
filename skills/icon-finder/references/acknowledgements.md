# Acknowledgements And License Boundaries

## Methodology Reference

This skill was inspired by the public [`icon-finder`](https://github.com/zm1990s/skills/tree/main/skills/icon-finder) workflow in `zm1990s/skills`, particularly its search-select-save interaction and its preference for vector assets in presentations.

At review commit `3c0b558`, the upstream scripts depended on an environment-specific `http://localhost:8000/icons/search` service and the repository did not expose an explicit root license file. No upstream source code, scripts, templates, or assets were copied. This implementation was written independently against the public Iconify API documentation.

## Runtime Data Source

The default runtime data source is the [Iconify API](https://iconify.design/docs/api/). Iconify provides search and SVG endpoints, but each icon collection retains its own author and license metadata.

The generated `icon-manifest.json` records the selected collection, author, license, source URL, retrieval time, and SVG hash. Keep that manifest with the presentation or document source.

Iconify's software license does not replace the license of an individual icon collection. Review the recorded collection license before commercial or external distribution and satisfy attribution requirements where applicable.

## Optional Rendering Dependency

PNG rendering is optional and uses CairoSVG when requested. HTTPS requests use the system CA store or an installed `certifi` CA bundle when available. CairoSVG and certifi are not vendored by this skill and remain governed by their own package licenses and dependencies. SVG search, download, normalization, inspection, and manifest generation otherwise use the Python standard library.

## Future Changes

Before adding another icon provider or copying upstream implementation code, record:

- repository and source path;
- commit or release;
- applicable license;
- copied or modified files;
- provider authorization and attribution requirements.
