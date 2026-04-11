# docs/ — Agent Guide

This directory contains the Docusaurus documentation site for Biomes.

## Structure

| Path                   | Purpose                                                                              |
| ---------------------- | ------------------------------------------------------------------------------------ |
| `docs/`                | Markdown documentation content (subdirectories: `basics/`, `resources/`, `terrain/`) |
| `src/`                 | Docusaurus React components and custom pages                                         |
| `static/`              | Static assets (images, etc.)                                                         |
| `docusaurus.config.js` | Site configuration                                                                   |
| `sidebars.js`          | Documentation sidebar structure                                                      |
| `package.json`         | Docusaurus dependencies                                                              |

## Common tasks

### Adding or editing documentation

1. Edit or create `.md` / `.mdx` files in `docs/docs/`
2. If adding a new page, add it to `sidebars.js` if it should appear in navigation
3. Reference images via `/img/<filename>` in Markdown, or `require('@site/static/img/<filename>').default` in React components

### Validating changes

```bash
cd docs
yarn install
yarn build
```

The build will catch broken links, invalid MDX, and missing assets.

For live preview during editing:

```bash
cd docs && yarn start
```

## Constraints

- Keep documentation factual and up-to-date with the actual codebase
- Do not modify `docusaurus.config.js` for cosmetic reasons
- Use existing section structure — don't reorganize the sidebar without a clear reason
- Images go in `static/img/`
