#!/usr/bin/env python3
"""
Script to generate a product image using the ContentGecko API.

Takes a product image URL and composites it onto a template image,
then returns the S3 URL of the generated result.

Usage:
    python generate_product_image.py <product_image_url> --api-key <key> --template <path_or_url>

Environment variables (alternative to flags):
    CONTENTGECKO_API_KEY   Your ContentGecko API key
    TEMPLATE_IMAGE         Path or URL to the template image

Returns:
    Prints the S3 URL of the generated image to stdout
    Exits with code 0 on success, 1 on error
"""

import os
import sys
import argparse
import requests

API_BASE_URL = "https://api.contentgecko.io"
API_ENDPOINT = f"{API_BASE_URL}/product-image"
PROMPT = (
    "Replace the product package on the second template image with the product "
    "package in the first image. Product needs to be shown in full front view, "
    "like on the template. Square aspect ratio."
)


def get_image_base64(path_or_url):
    """Convert a local image file or remote URL to base64."""
    import base64
    if path_or_url.startswith("http://") or path_or_url.startswith("https://"):
        response = requests.get(path_or_url, timeout=30)
        response.raise_for_status()
        data = response.content
    else:
        with open(path_or_url, "rb") as f:
            data = f.read()
    return base64.b64encode(data).decode("utf-8")


def generate_image(api_token, prompt, image_url, template_base64):
    """Send request to ContentGecko API and return response."""
    headers = {
        "Authorization": f"Bearer {api_token}",
        "Content-Type": "application/json",
    }

    payload = {
        "prompt": prompt,
        "image": {
            "url": image_url
        },
        "referenceImage": {
            "base64": template_base64,
            "mimeType": "image/jpeg"
        },
        "returnUrl": True
    }

    response = requests.post(API_ENDPOINT, headers=headers, json=payload, timeout=300)

    try:
        response_data = response.json()
    except Exception as e:
        raise Exception(
            f"Failed to parse response (status {response.status_code}): {str(e)}\n"
            f"Response text: {response.text[:200]}"
        )

    if "imageUrl" in response_data:
        if response.status_code != 200:
            print(
                f"Warning: Received status {response.status_code} but image URL is present, proceeding...",
                file=sys.stderr
            )
        return response_data

    if response.status_code != 200:
        error_msg = response_data.get("error", "Unknown error")
        raise Exception(f"API error ({response.status_code}): {error_msg}")

    return response_data


def main():
    parser = argparse.ArgumentParser(
        description="Generate a product image via ContentGecko API"
    )
    parser.add_argument(
        "product_image_url",
        help="URL of the product image to composite"
    )
    parser.add_argument(
        "--api-key",
        default=os.environ.get("CONTENTGECKO_API_KEY"),
        help="ContentGecko API key (or set CONTENTGECKO_API_KEY env var)"
    )
    parser.add_argument(
        "--template",
        default=os.environ.get("TEMPLATE_IMAGE"),
        help="Local path or URL to the template image (or set TEMPLATE_IMAGE env var)"
    )

    args = parser.parse_args()

    if not args.api_key:
        print(
            "Error: ContentGecko API key is required.\n"
            "Pass --api-key <key> or set the CONTENTGECKO_API_KEY environment variable.",
            file=sys.stderr
        )
        sys.exit(1)

    if not args.template:
        print(
            "Error: Template image is required.\n"
            "Pass --template <path_or_url> or set the TEMPLATE_IMAGE environment variable.",
            file=sys.stderr
        )
        sys.exit(1)

    product_image_url = args.product_image_url

    if not (product_image_url.startswith("http://") or product_image_url.startswith("https://")):
        print("Error: Product image must be a valid URL (http:// or https://)", file=sys.stderr)
        sys.exit(1)

    print(f"Processing product image: {product_image_url}", file=sys.stderr)
    print(f"Using template: {args.template}", file=sys.stderr)

    print("Encoding template image...", file=sys.stderr)
    try:
        template_base64 = get_image_base64(args.template)
    except Exception as e:
        print(f"Error loading template image: {str(e)}", file=sys.stderr)
        sys.exit(1)

    print("Sending request to ContentGecko API...", file=sys.stderr)
    try:
        response = generate_image(args.api_key, PROMPT, product_image_url, template_base64)

        s3_url = response["imageUrl"]
        print(s3_url)

        print(f"✓ Success! Generated image URL: {s3_url}", file=sys.stderr)
        print(f"Remaining credits: {response.get('remainingCredits', 'N/A')}", file=sys.stderr)
        sys.exit(0)

    except Exception as e:
        print(f"✗ Error: {str(e)}", file=sys.stderr)
        sys.exit(1)


if __name__ == "__main__":
    main()
