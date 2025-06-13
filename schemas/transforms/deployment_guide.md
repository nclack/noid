# Spatial Transform Vocabulary Deployment Guide

## File Structure

Your vocabulary should be deployed with the following structure:

```
spatial-transforms/
├── vocabulary.ttl          # Turtle format (RDF)
├── vocabulary.jsonld       # JSON-LD format (full vocabulary)
├── context.jsonld         # JSON-LD context only
├── terms.json            # Simple list of valid terms
├── schema.json           # JSON Schema for validation (optional)
└── index.html            # Human-readable documentation (optional)
```

## Content Negotiation

Configure your web server to serve the appropriate format based on the `Accept` header:

### Apache (.htaccess)
```apache
RewriteEngine On

# Redirect base URL to appropriate format
RewriteCond %{HTTP_ACCEPT} text/turtle [OR]
RewriteCond %{HTTP_ACCEPT} application/x-turtle
RewriteRule ^$ vocabulary.ttl [L]

RewriteCond %{HTTP_ACCEPT} application/ld\+json [OR]
RewriteCond %{HTTP_ACCEPT} application/json
RewriteRule ^$ vocabulary.jsonld [L]

# Default to HTML
RewriteRule ^$ index.html [L]
```

### Nginx
```nginx
location /spatial-transforms/ {
    # Content negotiation
    if ($http_accept ~* "text/turtle|application/x-turtle") {
        rewrite ^/$ /vocabulary.ttl last;
    }
    if ($http_accept ~* "application/ld\+json|application/json") {
        rewrite ^/$ /vocabulary.jsonld last;
    }
    # Default to HTML
    rewrite ^/$ /index.html last;
}
```

## CORS Headers

Enable CORS to allow cross-origin access:

### Apache
```apache
Header set Access-Control-Allow-Origin "*"
Header set Access-Control-Allow-Methods "GET, HEAD, OPTIONS"
```

### Nginx
```nginx
add_header Access-Control-Allow-Origin "*";
add_header Access-Control-Allow-Methods "GET, HEAD, OPTIONS";
```

## Usage Examples

### 1. In Croissant Dataset
```json
{
  "@context": {
    "st": "https://example.org/spatial-transforms/"
  },
  "field": [{
    "name": "transform_type",
    "dataType": "st:TransformType"
  }]
}
```

### 2. Fetching the Vocabulary
```javascript
// Get JSON-LD
fetch('https://example.org/spatial-transforms/vocabulary.jsonld')
  .then(r => r.json())
  .then(vocab => console.log(vocab));

// Get simple terms list
fetch('https://example.org/spatial-transforms/terms.json')
  .then(r => r.json())
  .then(terms => console.log(terms));
```

### 3. Validating Data
```python
import requests

# Get valid terms
response = requests.get('https://example.org/spatial-transforms/terms.json')
valid_terms = set(response.json())

# Validate
if transform_type not in valid_terms:
    raise ValueError(f"Invalid transform type: {transform_type}")
```

## Testing Your Deployment

```bash
# Test content negotiation
curl -H "Accept: text/turtle" https://example.org/spatial-transforms/
curl -H "Accept: application/ld+json" https://example.org/spatial-transforms/
curl -H "Accept: text/html" https://example.org/spatial-transforms/

# Test direct file access
curl https://example.org/spatial-transforms/vocabulary.ttl
curl https://example.org/spatial-transforms/vocabulary.jsonld
curl https://example.org/spatial-transforms/terms.json

# Test CORS
curl -I https://example.org/spatial-transforms/terms.json
```

## GitHub Pages Deployment

For GitHub Pages, create a repository structure:

```
spatial-transforms-vocab/
├── vocabulary.ttl
├── vocabulary.jsonld
├── context.jsonld
├── terms.json
├── index.html
└── _config.yml
```

`_config.yml`:
```yaml
plugins:
  - jekyll-redirect-from

# CORS headers via meta tags in HTML
```

## CDN Deployment

For better performance, deploy through a CDN:

1. **jsDelivr** (from GitHub):
   ```
   https://cdn.jsdelivr.net/gh/username/spatial-transforms-vocab@main/vocabulary.jsonld
   ```

2. **Unpkg** (from npm):
   ```
   https://unpkg.com/@example/spatial-transforms-vocab/vocabulary.jsonld
   ```

## Versioning Strategy

Include version in the path for breaking changes:
```
https://example.org/spatial-transforms/v1/vocabulary.jsonld
https://example.org/spatial-transforms/v2/vocabulary.jsonld
```

Or use version negotiation:
```
https://example.org/spatial-transforms/vocabulary.jsonld?version=1.0
```