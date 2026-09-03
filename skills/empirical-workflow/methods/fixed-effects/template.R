# Plain panel fixed-effects reference implementation.
# Adapted from ericluo04/claude-academic-workflow commit
# 8958cc246e65cdf7c36604f397a1c1719b7e2c14.

library(fixest)

required <- c("unit", "period", "y", "d", "assignment_cluster")
stopifnot(all(required %in% names(panel)))
stopifnot(!anyDuplicated(panel[c("unit", "period")]))

within_var <- tapply(panel$d, panel$unit, function(z) var(z, na.rm = TRUE))
variation_audit <- c(
  units = length(within_var),
  no_within_variation = sum(is.na(within_var) | within_var == 0)
)
print(variation_audit)

pooled <- feols(y ~ d, data = panel, cluster = ~assignment_cluster)
within <- feols(
  y ~ d | unit + period,
  data = panel,
  cluster = ~assignment_cluster
)
etable(pooled, within)
sessionInfo()
