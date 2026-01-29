library(data.table)

FILE_PATTERN = '^kwb-(\\d{4})-woz-koopwoningen-huurwoningen-woningvoorraad[.]csv$'
MEASURES = c(
  "woz" = "M001642", # Gemiddelde WOZ-waarde van woningen
  "koopwoningen" = "1014800_1", # Koopwoningen (owner-occupied)
  "huurwoningen" = "1014850_2", # Huurwoningen totaal
  "woningvoorraad" = "M000297" # Housing stock
)
NA_STRINGS = c("None", "")

# Load raw data
load_cbs_data = function(paths) {
  paths = setNames(paths, sub(FILE_PATTERN, "\\1", basename(paths))) # Extract year from filename
  dfs = lapply(paths, \(path) fread(path, na.strings = NA_STRINGS))
  data = rbindlist(dfs, use.names = TRUE, fill = TRUE, idcol = "year")
  return(data)
}


# Get all files
paths = dir("demo/data/raw/cbs", FILE_PATTERN, full.names = TRUE)
data = load_cbs_data(paths)

# Clean CBS data
clean_cbs_data = function(data) {
  setnames(data, tolower)
  # ValueAttribute and StringValue are empty
  if ("valueattribute" %in% names(data) && data[, all(is.na(valueattribute))]) {
    data[, valueattribute := NULL]
  }
  if ("stringvalue" %in% names(data) && data[, all(is.na(stringvalue))]) {
    data[, stringvalue := NULL]
  }

  # Combine region codes (one is always NA)
  data[, region := fcoalesce(wijkenenbuurten, regios)]

  # Region type: NL=national, GM=gemeente, WK=wijk, BU=buurt
  data[,
    region_type := fcase(
      region %like% "^NL","national",
      region %like% "^GM", "gemeente",
      region %like% "^WK", "wijk",
      region %like% "^BU", "buurt"
    )
  ]

  # Pivot wider - one row per region-year
  data_wide = dcast(
    data,
    year + region + region_type ~ measure,
    value.var = "value"
    #, fun.aggregate = \(x) mean(x, na.rm=TRUE) # in case of duplicates
)

# Rename columns
setnames(data_wide, MEASURES, names(MEASURES))

# Convert NaN to NA
for (col in names(MEASURES)) {
  set(data_wide, which(is.nan(data_wide[[col]])), col, NA_real_)
}

# Sort
setorder(data_wide, year, region_type, region)

return(data_wide)
}


if (sys.nframe() == 0) {
  # Run as script
  paths = dir("data/raw/cbs", FILE_PATTERN, full.names = TRUE)
  data = load_cbs_data(paths)
  data_clean = clean_cbs_data(data)

  # Save
  out_dir = "data/processed"
  dir.create(out_dir, showWarnings = FALSE, recursive = TRUE)
  fwrite(data_clean, file.path(out_dir, "kwb_housing.csv"))

  message("Saved ", nrow(data_clean), " rows to data/processed/kwb_housing.csv")
}
