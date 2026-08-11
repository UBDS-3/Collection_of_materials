library(tidyverse)

rna <- read_csv("data/rnaseq.csv")

ggplot(data)


ggplot(data = rna)

ggplot(data = rna, 
       mapping = aes(x = expression))

## histograms

ggplot(data = rna, 
       mapping = aes(x = expression)) +
  geom_histogram()

ggplot(data = rna, 
       mapping = aes(x = expression)) +
  geom_boxplot()

ggplot(data = rna, 
       mapping = aes(y = expression)) +
  geom_boxplot()


## If we now draw the histogram of the 
## log2-transformed expressions + 1, the 
## distribution is indeed closer to a 
## normal distribution.

ggplot(data = rna, 
       mapping = aes(x = log2(expression + 1))) +
  geom_histogram()

rna |> 
  mutate(expression = log2(expression + 1)) |> 
  ggplot(mapping = aes(x = expression)) +
  geom_histogram()

## Scatterplots

rna_fc <- rna |> 
  mutate(expression_log = log2(expression + 1)) |> 
  select(gene, time, 
         expression_log, 
         gene_biotype) |> 
  group_by(gene, time, gene_biotype) |> 
  summarise(mean = mean(expression_log)) |> 
  pivot_wider(names_from = time, 
              values_from = mean) |> 
  rename("t0" = `0`,
         "t4" = `4`,
         "t8" = `8`) |> 
  mutate(lfc4 = t4 - t0,
         lfc8 = t8 - t0)


## Boxplots

rna_fc |> 
  ggplot(aes(x = lfc4, 
             y = lfc8)) + 
  geom_point(colour = "blue")


rna_fc |> 
  ggplot(aes(x = lfc4, 
             y = lfc8,
             colour = gene_biotype)) + 
  geom_point()


rna |> 
  ggplot(aes(x = sample,
             y = log2(expression + 1))) +
  geom_boxplot()
  

rna |> 
  ggplot(aes(x = sample,
             y = log2(expression + 1))) +
  geom_boxplot() + 
  geom_point()


rna |> 
  ggplot(aes(x = sample,
             y = log2(expression + 1))) +
  geom_boxplot() + 
  geom_jitter(alpha = 0.1)

  
rna |> 
  ggplot(aes(x = sample,
             y = log2(expression + 1))) +
  geom_jitter(alpha = 0.1) + 
  geom_boxplot() 


rna |> 
  ggplot(aes(x = sample,
             y = log2(expression + 1))) +
  geom_jitter(alpha = 0.1) + 
  geom_boxplot(aes(colour = "magenta")) 

rna |> 
  ggplot(aes(x = sample,
             y = log2(expression + 1))) +
  geom_jitter(alpha = 0.1) + 
  geom_boxplot(aes(fill = "magenta")) 


rna |> 
  ggplot(aes(x = sample,
             y = log2(expression + 1))) +
  geom_jitter(alpha = 0.1) + 
  geom_boxplot(aes(fill = factor(time)))


rna |> 
  ggplot(aes(x = sample,
             y = log2(expression + 1))) +
  geom_jitter(alpha = 0.1) + 
  geom_violin(aes(fill = factor(time)))


## Lineplots


genes_selected <- rna_fc |> 
  arrange(desc(lfc8)) |> 
  head(10) |> 
  pull(gene)

genes_selected


rna_exp_time <- rna |> 
  filter(gene %in% genes_selected) |> 
  group_by(gene, time) |> 
  summarise(exp = mean(log2(expression + 1)))


rna_exp_time |> 
  ggplot(aes(x = time,
             y = exp, 
             group = gene)) +
  geom_line()
  

rna_exp_time |> 
  ggplot(aes(x = time,
             y = exp, 
             colour = gene)) +
  geom_line()


rna_exp_time |> 
  ggplot(aes(x = time,
             y = exp, 
             colour = gene)) +
  geom_line() +
  facet_wrap(~ gene)

rna_exp_time |> 
  ggplot(aes(x = time,
             y = exp)) +
  geom_line() +
  facet_wrap(~ gene)


## Ex:

rna_exp_time_sex <- rna |> 
  filter(gene %in% genes_selected) |> 
  group_by(gene, time, sex) |> 
  summarise(exp = mean(log2(expression + 1)))

rna_exp_time_sex |> 
  ggplot(aes(x = time,
             y = exp,
             colour = sex)) +
  geom_line() +
  facet_wrap(~ gene)


ggsave(filename = "figs/exp_time_sex.png")
