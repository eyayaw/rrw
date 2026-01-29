# Download gemeente boundaries from PDOK (CBS Wijken en Buurten 2024)
# This script downloads Dutch municipality boundaries for mapping

library(sf)

download_gemeente_boundaries = function() {
# PDOK WFS endpoint for gemeente boundaries
url = paste0(
  "https://service.pdok.nl/cbs/wijkenbuurten/2024/wfs/v1_0",
  "?request=GetFeature",
  "&service=WFS",
  "&version=2.0.0",
  "&typeName=wijkenbuurten:gemeenten",
  "&outputFormat=json"
)

output_dir = file.path("demo", "data", "geodata")
if (!dir.exists(output_dir)) {
  dir.create(output_dir, recursive = TRUE)
}
output_path = file.path(output_dir, "gemeenten_2024.gpkg")

# Download and read the GeoJSON
message("Downloading gemeente boundaries from PDOK...")
if (file.exists(output_path)) {
  message("Output file already exists. No download needed.")
  return(output_path)
}
gemeenten = st_read(url, quiet = TRUE)

# Save as GeoPackage
st_write(gemeenten, output_path, append = TRUE)

message("Saved gemeente boundaries to: ", output_path)
message("Number of gemeenten: ", nrow(gemeenten))
return (output_path)
}

if (sys.nframe() == 0) {
  # Run as script
  download_gemeente_boundaries()
}
