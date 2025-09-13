# Basic smoke test: health, create products, list products.
$ErrorActionPreference = "Stop"

function JPost($url, $obj) {
  $json = $obj | ConvertTo-Json -Depth 8
  Invoke-RestMethod -Method Post -Uri $url -Body $json -ContentType "application/json"
}
function JGet($url) {
  Invoke-RestMethod -Method Get -Uri $url
}

# 1) Health checks
Write-Host "==> API health"
$health = JGet "http://localhost:8000/health"
$health

# 2) Seed a few products (DISABLE_AUTH=true in backend .env allows admin routes)
Write-Host "==> Create sample products"
$base = "http://localhost:8000/products"
$products = @(
  @{
    title="Widget A"; description="Alpha widget"; images=@(); price="19.99"; sku="WIDGET-A"; inventory=50; is_active=$true
  },
  @{
    title="Widget B"; description="Beta widget"; images=@(); price="29.50"; sku="WIDGET-B"; inventory=35; is_active=$true
  },
  @{
    title="Widget C"; description="Gamma widget"; images=@(); price="39.00"; sku="WIDGET-C"; inventory=10; is_active=$true
  }
)

foreach ($p in $products) {
  try {
    $r = JPost $base $p
    Write-Host "Created id=$($r.id) sku=$($r.sku)"
  } catch {
    Write-Warning "Create failed: $($_.Exception.Message)"
  }
}

# 3) List products
Write-Host "==> List products"
$list = JGet "$base?limit=50"
$list | Format-Table id, title, sku, price, inventory

Write-Host "`nSmoke test complete. Frontend at http://localhost:3000"
