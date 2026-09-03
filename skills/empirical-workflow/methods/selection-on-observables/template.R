# Selection-on-observables reference implementation.
# Adapted from ericluo04/claude-academic-workflow commit
# 8958cc246e65cdf7c36604f397a1c1719b7e2c14.

library(grf)
library(sensemakr)

required <- c("y", "d", "x1", "x2", "x3", "assignment_cluster")
stopifnot(all(required %in% names(df)))
stopifnot(all(df$d %in% c(0, 1)))

X <- as.matrix(df[c("x1", "x2", "x3")])
set.seed(42)
fit <- causal_forest(
  X, df$y, df$d,
  num.trees = 2000,
  clusters = df$assignment_cluster,
  seed = 42
)

hist(fit$W.hat, xlim = c(0, 1))
print(mean(fit$W.hat < 0.10 | fit$W.hat > 0.90))
print(average_treatment_effect(fit, target.sample = "all"))
print(average_treatment_effect(fit, target.sample = "overlap"))

ols <- lm(y ~ d + x1 + x2 + x3, data = df)
sensitivity <- sensemakr(
  model = ols,
  treatment = "d",
  benchmark_covariates = "x1",
  kd = 1:3
)
print(summary(sensitivity))
sessionInfo()
