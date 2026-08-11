## install.packages("tidyverse")

library(tidyverse)

rna <- read_csv("data/rnaseq.csv")

class(rna)

rna

dim(rna)
head(rna)

names(rna)
colnames(rna)
rownames(rna)

dfr <- data.frame(
  x = 1:3,
  y = LETTERS[1:3]
)

dfr

rownames(dfr) <- c("R1", "R2", "R3")

dfr
colnames(dfr)
rownames(dfr)

as_tibble(dfr)
as_tibble(dfr, rownames = "rnames")

## Select columns/variables

select(rna, gene, expression, sample)

select(rna, -tissue, -expression)

## Filter rows/observations

filter(rna, sex == "Female")

table(rna$infection)

filter(rna, sex == "Female" & 
         infection == "InfluenzaA")

filter(rna, sex == "Female",
       infection == "InfluenzaA")

View(filter(rna, sex == "Female",
       infection != "InfluenzaA"))

## Ex

## Create a new tibble called rna2 containing male 
## mice at time point 0, (that do not have a missing 
## homolog in humans), and only columns gene, expression, 
## chromosome and time.


rna2 <- filter(rna, sex == "Male",
               time == 0,
               !is.na(hsapiens_homolog_associated_gene_name))

rna2 <- select(rna2, gene, expression,  chromosome_name, time)

# rna2 <- select(
#   filter(rna, sex == "Male",
#          time == 0,
#          !is.na(hsapiens_homolog_associated_gene_name)),
#   gene, expression,  chromosome_name, time)
       
## Pipes: |>  %>%
  
rna3 <- rna |> 
  filter(sex == "Male", 
         time == 0,
         !is.na(
           hsapiens_homolog_associated_gene_name)) |> 
  select(gene, expression,  
         chromosome_name, time)

identical(rna2, rna3)

# Ex:

# Using pipes, subset the rna data to keep 
# observations in female mice at time 0, where 
# the gene has an expression higher than 50000, 
# and retain only the columns gene, sample, 
# time, expression and age.

rna |> 
  filter(sex == "Female",
         time == 0,
         expression > 50000) |> 
  select(gene, sample, time, 
         expression, age)
  

## Mutate

rna |> 
  mutate(time_hours = time * 24) |> 
  select(gene, time, time_hours)
  
  
rna |> 
  mutate(time = time * 24) |> 
  select(gene, time)

rna |> 
  mutate(time_hours = time * 24,
         time_min = time_hours * 60) |> 
  select(gene, time, time_hours,
         time_min)

  
# Create a new data frame from the rna
# data that meets the following 
# criteria: contains only the gene, 
# chromosome_name, phenotype_description, 
# sample, and expression columns. The 
# expression values should be 
# log-transformed. This data frame must 
# only contain genes located on sex 
# chromosomes, associated with a 
# phenotype_description, and with a 
# log expression higher than 5.
# 
# Hint: think about how the commands 
# should be ordered to produce this data
# frame!

## table(rna$chromosome_name %in% c("X", "Y"))

rna |> 
  mutate(expression = log(expression)) |> 
  filter(expression > 5,
         chromosome_name %in% c("X", "Y"),
         !is.na(phenotype_description)) |> 
  select(gene, chromosome_name, 
         phenotype_description, 
         sample, expression)

## Split-apply-combine

rna |> 
  group_by(sex)

rna |> 
  group_by(gene)

rna |> 
  group_by(gene, sex)


rna |> 
  group_by(gene) |> 
  summarise(mean = mean(expression))


rna |> 
  group_by(gene, sex, time) |> 
  summarise(mean = mean(expression))

rna |> 
  group_by(gene, sex, time) |> 
  summarise(mean = mean(expression)) |> 
  ungroup()

rna |> 
  group_by(time, gene, sex) |> 
  summarise(mean = mean(expression))


rna |> 
  filter(sex == "Female", 
         time == 0,
         gene == "AI504432") |> 
  select(gene, time, sex, expression) |> 
  pull(expression) |> 
  mean()


rna |> 
  group_by(time, gene, sex) |> 
  summarise(mean = mean(expression), 
            med = median(expression))

## Ex
## Calculate the mean expression level of 
## gene “Dok3” by timepoints.

rna |> 
  filter(gene == "Dok3") |> 
  group_by(time) |> 
  summarise(mean_exp = mean(expression))

rna |> 
  group_by(time, gene) |> 
  summarise(mean_exp = mean(expression)) |> 
  filter(gene == "Dok3")


rna |> 
  count(infection)


rna |> 
  group_by(infection) |> 
  summarise(n = n())


rna |> 
  count(infection, time)

rna |> 
  count(infection, time) |> 
  arrange(time)

rna |> 
  count(infection, time) |> 
  arrange(desc(time))


# 1. How many genes were analysed in each sample?

rna |> 
  count(sample)

# 2. Use group_by() and summarise() to 
#    evaluate the sequencing depth 
#    (the sum of all counts) in each sample. 
#    Which sample has the highest sequencing 
#    depth?

rna |> 
  group_by(sample) |> 
  summarise(seq_depth = sum(expression)) |> 
  arrange(desc(seq_depth))

rna |> 
  group_by(sample) |> 
  summarise(seq_depth = sum(expression)) |> 
  filter(seq_depth == max(seq_depth))


# 3. Pick one sample and evaluate the number 
#    of genes by biotype.

rna |> 
  filter(sample == "GSM2545350") |> 
  count(gene_biotype)

# 4. Identify genes associated with the 
#    “abnormal DNA methylation” phenotype 
#    description, and calculate their mean 
#    expression (in log) at time 0, time 4 and 
#    time 8.

rna |> 
  filter(phenotype_description == "abnormal DNA methylation") |> 
  group_by(gene, time) |> 
  summarise(mean_exp = mean(log(expression)))

## Reshaping data

rna_exp <- rna |> 
  select(gene, sample, expression)

rna_exp



rna_wide <- rna_exp |> 
  pivot_wider(names_from = sample,
              values_from = expression)


rna_long <- rna_wide |> 
  pivot_longer(names_to = "sample",
               values_to = "expression", 
               -gene)

rna_long


rna_wide |> 
  pivot_longer(names_to = "sample",
               values_to = "expression", 
               starts_with("GSM"))


## Ex:

rna |> 
  filter(chromosome_name %in% c("X", "Y")) |> 
  group_by(chromosome_name, sex) |> 
  summarise(mean = mean(expression)) |> 
  pivot_wider(names_from = sex, 
              values_from = mean)


rna_time <- rna |> 
  group_by(gene, time) |> 
  summarise(mean = mean(expression)) |> 
  pivot_wider(names_from = time, 
              values_from = mean)

rna_time |> 
  mutate(t0 = `0`,
         t4 = `4`,
         t8 = `8`)

rna_time <- rna_time |> 
  rename("t0" = `0`,
         "t4" = `4`,
         "t8" = `8`)

## Add 2 new columns containing 
## fold-changes between time 8 
## and 0, and time 4 and 0, by dividing
## the respective average expressions.

rna_time |> 
  mutate(fc4 = t4 / t0,
         fc8 = t8 / t0)

## Convert this table into a long-format 
## table gathering the fold-changes
## calculated above.

rna_fc <- rna_time |> 
  mutate(fc4 = t4 / t0,
         fc8 = t8 / t0) |> 
  select(gene, fc4, fc8) |> 
  pivot_longer(names_to = "foldchange",
               values_to = "value",
               -gene) 

rna_time |> 
  mutate(fc4 = t4 / t0,
         fc8 = t8 / t0) |> 
  pivot_longer(names_to = "foldchange",
               values_to = "value",
               c(fc4, fc8))


# rna_time |> 
#   mutate(fc4 = t4 / t0,
#          fc8 = t8 / t0) |> 
#   pivot_longer(names_to = "metric",
#                values_to = "value",
#                -gene)

rna_fc

write_csv(rna_fc, "data/rna_fc.csv")

