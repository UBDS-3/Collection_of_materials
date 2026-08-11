x <- read_csv("data/seOnco-UBDS3-2026.csv")

res <- x |> 
  group_by(sample, oncoGene, patient) |> 
  summarise(mean = mean(expression)) |> 
  mutate(oncoGene = paste0("onco", oncoGene)) |> 
  pivot_wider(names_from = oncoGene, 
              values_from = mean) |> 
  mutate(oncoFC = oncoTRUE - oncoFALSE)


res |> 
  group_by(patient) |> 
  summarise(min = min(oncoFC), 
            max = max(oncoFC))

threshold <- 0.72

res |> 
  mutate(diagnostic = oncoFC > threshold)

res |> 
  ggplot(aes(x = sample, 
             y = oncoFC, 
             colour = patient)) +
  geom_point() +
  geom_hline(yintercept = threshold)
