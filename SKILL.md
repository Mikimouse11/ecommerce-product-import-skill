---
name: shopify-product-importer
description: Import products from any website into Shopify via CSV with automated image enhancement. Use when the user provides a URL to a product page and wants to add it to their Shopify store. On first use, collects configuration (template image, ContentGecko API key, required product fields). Extracts product details from the page, generates enhanced product images using ContentGecko API, and creates a Shopify-compatible CSV for import.
---

# Shopify Product Importer (CSV)

Import products from any website by generating Shopify-compatible CSV import files with AI-enhanced product images.

## First-Time Setup

On first use, check for a config file at `~/.claude/shopify-importer-config.json`. If it does not exist, ask the user for the following before proceeding:

1. **Template image**: Ask the user to provide a local file path or URL to their product image template — the background/scene image that product photos will be composited onto (e.g., a branded background, lifestyle scene, or display surface).

2. **ContentGecko API key**: Ask the user for their ContentGecko API key (format: `sk_...`). They can get one at https://contentgecko.io.

3. **Custom product fields**: Ask the user what product-specific attributes they want to extract for each product. These are attributes beyond the standard title/description/price — for example:
   - A coffee shop might say: "variety, process method, origin, roast level, tasting notes"
   - A clothing store might say: "material, fit, care instructions"
   - A furniture store might say: "dimensions, material, assembly required"

   These fields will be extracted from each product page and included in the Shopify product's HTML description.

Once collected, save the config to `~/.claude/shopify-importer-config.json`:
```json
{
  "template_image": "<path or URL>",
  "api_key": "<ContentGecko API key>",
  "custom_fields": ["field1", "field2", "..."]
}
```

On subsequent uses, load this config automatically without asking. If the user wants to update their config, they can ask to "reconfigure the importer".

---

## Workflow

When the user provides a product URL, follow these steps:

### 1. Load Configuration and CSV Template

Load configuration from `~/.claude/shopify-importer-config.json`.

Load the CSV template headers from `references/product_import_template.csv`.

### 2. Fetch Product Page Content

Use the `web_fetch` tool to retrieve the product page. **Always prepend `https://markdown.new/` to the product URL** — this automatically converts the page to clean Markdown, making it easier to extract structured data.

For example, if the user provides `https://example.com/products/blue-widget`, fetch:
```
https://markdown.new/https://example.com/products/blue-widget
```

**IMPORTANT: All extracted text must be translated to English if the source website is in another language.**

If critical information cannot be extracted from the fetched content, fall back to using browser tools to navigate and extract interactively.

**Always extract:**
- **Product title** — The core product name
- **Product description** — Full description translated to English, converted to HTML with proper `<p>` tags
- **Vendor / brand name**
- **Price** — Numeric value only, in the store's listed currency
- **Main product image URL** — Primary image only (one per product)

**Custom fields** — Extract each field listed in `custom_fields` from the config. Pull from the product description, specs, or details section. Translate to English if needed.

If critical data (price, vendor, or any required custom field) cannot be extracted, ask the user to provide the missing values before continuing.

### 3. Generate Enhanced Product Image

Run the image generation script to composite the product image onto the user's template:

```
python scripts/generate_product_image.py <product_image_url> \
  --api-key <api_key from config> \
  --template <template_image from config>
```

The script sends the product image URL and template to the ContentGecko API and returns an S3 URL for the generated image. Capture both the S3 URL (enhanced) and the original product image URL.

### 4. Generate CSV Row

Create a CSV row using the headers from `references/product_import_template.csv`.

**Row 1 — Main product row:**
- **Handle**: `<vendor>-<title>` in lowercase with hyphens, spaces removed (e.g., `acme-blue-widget`)
- **Title**: Product name
- **Body (HTML)**: Custom fields formatted as bold labels, followed by the description:
  ```html
  <p><b>field1:</b> value1<br><b>field2:</b> value2<br></p><p>Full product description here.</p>
  ```
- **Vendor**: Brand name
- **Type**: Leave empty
- **Published**: `true`
- **Option1 Name**: `Title`
- **Option1 Value**: `Default Title`
- **Variant SKU**: `<title>_<vendor>` in lowercase with underscores (e.g., `blue_widget_acme`)
- **Variant Grams**: Weight in grams if available, otherwise leave empty
- **Variant Inventory Tracker**: `shopify`
- **Variant Inventory Qty**: `1`
- **Variant Inventory Policy**: `deny`
- **Variant Fulfillment Service**: `manual`
- **Variant Price**: Extracted price (numeric only)
- **Variant Requires Shipping**: `true`
- **Variant Taxable**: `true`
- **Image Src**: S3 URL of the enhanced image (from script output)
- **Image Position**: `1`
- **Variant Weight Unit**: `kg`
- **Status**: `active`

**Row 2 — Original image row:**
- **Handle**: Same as row 1
- **Image Src**: Original product image URL
- **Image Position**: `2`
- All other fields: Leave empty

### 5. Create or Append CSV File

- **First product**: Create a new CSV file with template headers, then add the product rows.
- **Additional products**: Append new rows to the existing file.

Name the file descriptively: `shopify_import_YYYYMMDD.csv`

### 6. Present Summary

Show the user a brief summary:
- Product title and vendor
- Price
- Enhanced image URL and original image URL
- CSV file name

Then instruct them to import via Shopify:
> **Products → Import → Upload file**

---

## Notes

- **Extraction method**: Always fetch via `https://markdown.new/<product_url>` for clean Markdown output; fall back to browser tools if content is missing
- **Language**: Always translate non-English content to English
- **Images**: Each product has exactly 2 rows — enhanced image (position 1) and original (position 2)
- **Handles**: lowercase, hyphens, no special characters
- **SKUs**: lowercase, underscores, no special characters
- **Price**: Strip currency symbols before writing to CSV
- **Missing data**: Always ask the user rather than guessing critical values
- **Config updates**: If the user says "reconfigure" or "update settings", delete and recreate `~/.claude/shopify-importer-config.json`
