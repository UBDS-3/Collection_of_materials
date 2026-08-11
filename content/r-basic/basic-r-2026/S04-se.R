## SummarizedExperiment


install.packages("BiocManager") ## CRAN

## Install Bioconductor packages
BiocManager::install("SummarizedExperiment")

library(SummarizedExperiment)

count_matrix <- read.csv("data/count_matrix.csv",
         row.names = 1) |> 
  as.matrix()

class(count_matrix)
dim(count_matrix)

count_matrix[1:5, 1:3]

sample_metadata <- read.csv("data/sample_metadata.csv")

class(sample_metadata)
dim(sample_metadata)

sample_metadata


gene_metadata <- read.csv("data/gene_metadata.csv")

dim(gene_metadata)

nrow(count_matrix) == nrow(gene_metadata)
ncol(count_matrix) == nrow(sample_metadata)

identical(rownames(count_matrix),
          gene_metadata$gene)

identical(colnames(count_matrix), 
          sample_metadata$sample)


se <- SummarizedExperiment(
  assays = count_matrix,
  colData = sample_metadata,
  rowData = gene_metadata
)


se

se2 <- se[1:5, 1:3]

assay(se2)
colData(se2)
rowData(se2)

saveRDS(se, file = "data/se.rds")

se <- readRDS("data/se.rds")
se

##-------------------------------

version
BiocManager::version()


package.version("tidyverse")

.libPaths()


ip <- installed.packages()

class(ip)
dim(ip)

ip[1:5, ]

rownames(ip)
