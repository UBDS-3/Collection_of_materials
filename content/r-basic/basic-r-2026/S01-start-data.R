download.file(url = "https://github.com/carpentries-incubator/bioc-intro/raw/main/episodes/data/rnaseq.csv",
              destfile = "data/rnaseq.csv")


rna <- read.csv("data/rnaseq.csv")

class(rna)

?read.csv

rna

dim(rna)
nrow(rna)
ncol(rna)

head(rna)
tail(rna)

View(rna)

summary(rna)

## Subsetting rna[, ]

rna[c(3, 7, 12), ]

rna[c(3, 7, 12), 1:3]

class(rna[c(3, 7, 12), 1:3])

names(rna)
colnames(rna) # same as names
rownames(rna)

rna[c(3, 7, 12), c("gene", "expression")]

rna[, "expression"]

rna[, "gene"]

mean(rna$expression)

class(rna$expression)

## Ex:
## Combine nrow() with the - notation 
## above to reproduce the behavior of 
## head(rna), keeping just the first
## 6 rows of the rna dataset.

head(rna)

rna[-(7:nrow(rna)), ]


## Factors

sex <- c("M", "M", "F", "M", "F")

sex

sex <- factor(sex)

sex

factor(c("M", "M", "F", "M", "F", NA))


