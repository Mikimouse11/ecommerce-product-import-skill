# Shopify Product Importer — Claude Code Skill

A Claude Code skill for importing products from any website into Shopify via CSV, with AI-enhanced product images powered by the [ContentGecko API](https://contentgecko.io).

## What it does

Give Claude a product URL from any website and this skill will:
1. Extract product details (title, description, price, images, and your custom fields)
2. Generate an enhanced product image by compositing the product onto your branded template
3. Output a Shopify-compatible CSV ready to import via **Products → Import**

Works with any product type — coffee, clothing, furniture, electronics, etc.

## Installation

1. Download `shopify-product-importer.skill`
2. In Claude Code, install it:
   ```
   /install shopify-product-importer.skill
   ```
   Or drag and drop the `.skill` file into Claude Code.

## First-time setup

On first use, Claude will ask you for three things:

| Setting | Description |
|---------|-------------|
| **Template image** | A local file path or URL to your branded background/scene image. Product photos will be composited onto this. |
| **ContentGecko API key** | Your API key from [contentgecko.io](https://contentgecko.io) (format: `sk_...`) |
| **Custom product fields** | The product-specific attributes to extract per product (e.g. `material, color, size` or `origin, process, roast level`) |

These are saved to `~/.claude/shopify-importer-config.json` and reused automatically.

To update your settings later, ask Claude to **"reconfigure the importer"**.

## Usage

After setup, just paste a product URL:

```
/shopify-product-importer

> Here's the product I want to add: https://example.com/products/blue-widget
```

Claude will extract the product data, generate an enhanced image, and produce a CSV file.

## Requirements

- [Claude Code](https://claude.ai/code)
- A [ContentGecko](https://contentgecko.io) account and API key
- Python 3.x with `requests` installed (`pip install requests`)
- A Shopify store

## Image generation script

The included `scripts/generate_product_image.py` can also be used standalone:

```bash
python scripts/generate_product_image.py <product_image_url> \
  --api-key sk_your_key_here \
  --template /path/to/template.jpg
```

Or via environment variables:

```bash
export CONTENTGECKO_API_KEY=sk_your_key_here
export TEMPLATE_IMAGE=/path/to/template.jpg
python scripts/generate_product_image.py <product_image_url>
```

## Repository contents

| Path | Description |
|------|-------------|
| `SKILL.md` | Skill definition — instructions for Claude |
| `references/product_import_template.csv` | Shopify CSV column headers |
| `references/example_output.csv` | Example of a completed import CSV |
| `scripts/generate_product_image.py` | Image generation script (ContentGecko API) |
| `assets/template_compressed.jpg` | Example template image (replace with your own) |

## License

MIT
