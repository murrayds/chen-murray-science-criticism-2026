# The order of labels to use
venue_levels <- function() {
  c(
    "Geology",
    "JCP",
    "EST",
    "NEJM"
  )
}

venue_levels_all <- function() {
  c(
    "Geology",
    "JCP",
    "EST",
    "NEJM"
  )
}

field_values <- function() {
  c(
    `142362112` = "art",
    `185592680` = "chemistry",
    `71924100` = "medicine",
    `192562407` = "materials science",
    `144024400` = "sociology",
    `17744445` = "political science",
    `39432304` = "environmental science",
    `127413603` = "engineering",
    `41008148` = "computer science",
    `205649164` = "geography",
    `15744967` = "psychology",
    `127313418` = "geology",
    `144133560` = "business",
    `162324750` = "economics",
    `138885662` = "philosophy",
    `33923547` = "mathematics",
    `86803240` = "biology",
    `121332964` = "physics",
    `95457728` = "history"
  )
}

venue_colors <- function() {
  c(
    "Geology" = "brown",
    "JCP" = "cyan",
    "EST" = "lightgreen",
    "NEJM" = "red"
  )
}