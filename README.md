# Reproducible Research Workflows

## Core components

- Project organization
- Version controlling with Git/GitHub
- Package dependency management (uv/renv)
- Literate programming with [Quarto](https://quarto.org)


## Slides

[Reproducible Research Wokflows](https://eyayaw.github.io/rrw/index.html), source [index.qmd](./index.qmd)

## Requirements

To rerun this project, install the following requirements


### R

1. R programming language

```sh
brew install --cask r
```

2. Required R Packages

```sh
Rscript -e 'install.packages(c("data.table", "ggplot2", "sf", "fixest", "knitr"))'
```

### Python

```sh
# first, install uv
# https://docs.astral.sh/uv/getting-started/installation/
curl -LsSf https://astral.sh/uv/install.sh | sh
# then, install python
# if you don't have it on your system
# uv python install

# run the following to install required dependencies
uv sync
```


### Quarto

On MacOS, for Windows/Linux read the installation [guide](https://quarto.org/docs/get-started/).

```sh
brew install quarto

# Or using uv
# uv tool install quarto
```

## The WOZ demo

The demo source lives in [`demo/woz_analysis.qmd`](./demo/woz_analysis.qmd).
Click on [demo/woz_analysis.html](https://eyayaw.github.io/rrw/demo/woz_analysis.html) to see the rendered version.

You can render it via the following command:

```sh
# from the root dir (./repdoucible-research-workflows)
cd demo && quarto render woz_analysis.qmd && cd -


# if you want to generate a word document
quarto render demo/woz_analysis.qmd --to docx -M echo:false
```