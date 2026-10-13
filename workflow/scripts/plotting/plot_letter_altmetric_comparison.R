library(tidyverse)
library(grid)
library(gridExtra)

source("scripts/plotting/theme.R")
source(snakemake@config[["venues_file"]])
source("scripts/common.R")

letters <- read_csv(snakemake@input[[1]])

features <- read_csv(snakemake@input[[2]]) %>%
  select(id, Tweet_Count, Newsfeed_Count)

orig1 <- letters %>%
  select(original_id, letter_id) %>%
  left_join(features, by = c("original_id" = "id")) %>%
  rename(`original_tweets` = "Tweet_Count") %>%
  left_join(features, by = c("letter_id" = "id")) %>%
  rename(`letter_tweets` = "Tweet_Count") %>%
  select(original_id, letter_id, original_tweets, letter_tweets) %>%
  mutate(
    original_tweets = cut(
      original_tweets,
      breaks = c(0, 0.1, 1, 10, 50, 100, 1000),
      labels = c("0", "1", "1-10", "10-50", "50-100", "100-1000"),
      include.lowest = TRUE
    ),
    letter_tweets = cut(
      letter_tweets,
      breaks = c(0, 0.1, 1, 10, 50, 100, 1000),
      labels = c("0", "1", "1-10", "10-50", "50-100", "100-1000"),
      include.lowest = TRUE
    )
  )

plotdata_tweets <- orig1 %>%
  group_by(original_tweets, letter_tweets) %>%
  summarize(count = n()) %>%
  group_by(original_tweets) %>%
  mutate(
    prop = count / sum(count)
  ) %>%
  filter(
    !is.na(original_tweets),
    !is.na(letter_tweets)
  )

p1 <- plotdata_tweets %>%
  ggplot(aes(x = letter_tweets, y = original_tweets, fill = prop)) +
  geom_tile(color = "white") +
  geom_text(aes(label = paste0(round(prop * 100, 1), "%")), color = "white") +
  theme_minimal() +
  theme(
    panel.grid = element_blank(),
    legend.position = "none",
    plot.title = element_text(size = 14, face = "bold")
  ) +
  xlab("Tweets accumulated by critical letter") +
  ylab("Tweets accumulated by original paper") +
  ggtitle("(A)")


orig2 <- letters %>%
  select(original_id, letter_id) %>%
  left_join(features, by = c("original_id" = "id")) %>%
  rename(`original_news` = "Newsfeed_Count") %>%
  left_join(features, by = c("letter_id" = "id")) %>%
  rename(`letter_news` = "Newsfeed_Count") %>%
  select(original_id, letter_id, original_news, letter_news) %>%
  mutate(
    original_news = cut(
      original_news,
      breaks = c(0, 0.1, 1, 5, 10, 20, 100),
      labels = c("0", "1", "1-5", "5-10", "10-20", "20-100"),
      include.lowest = TRUE
    ),
    letter_news = cut(
      letter_news,
      breaks = c(0, 0.1, 1, 5, 10, 20, 100),
      labels = c("0", "1", "1-5", "5-10", "10-20", "20-100"),
      include.lowest = TRUE
    )
  )

plotdata_news <- orig2 %>%
  group_by(original_news, letter_news) %>%
  summarize(count = n()) %>%
  group_by(original_news) %>%
  mutate(
    prop = count / sum(count)
  ) %>%
  filter(
    !is.na(original_news),
    !is.na(letter_news)
  )

p2 <- plotdata_news %>%
  ggplot(aes(x = letter_news, y = original_news, fill = prop)) +
  geom_tile(color = "white") +
  geom_text(aes(label = paste0(round(prop * 100, 1), "%")), color = "white") +
  theme_minimal() +
  theme(
    panel.grid = element_blank(),
    legend.position = "none",
    plot.title = element_text(size = 14, face = "bold")
  ) +
  xlab("News mentions accumulated by critical letter") +
  ylab("News mentions accumulated by original paper") +
  ggtitle("(B)")

g <- grid.arrange(p1, p2, nrow = 1, widths = c(0.6, 0.4))

# Save the output
ggsave(
  g,
  filename = snakemake@output[[1]],
  width = 11,
  height = 5,
  bg = "white"
)

# Save the data underlying the plot, combining both panels
plotdata <- bind_rows(
  plotdata_tweets %>%
    rename(original_bin = original_tweets, letter_bin = letter_tweets) %>%
    mutate(panel = "(A) Tweets"),
  plotdata_news %>%
    rename(original_bin = original_news, letter_bin = letter_news) %>%
    mutate(panel = "(B) News mentions")
) %>%
  select(panel, original_bin, letter_bin, count, prop)

write_csv(plotdata, snakemake@output[[2]])
