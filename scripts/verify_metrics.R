# Verify the metrics thru R
suppressPackageStartupMessages({
  library(PerformanceAnalytics)
  library(xts)
})

args <- commandArgs(trailingOnly = TRUE)
csv_path <- ifelse(length(args) > 0, args[1], "data/SPY.csv")


df <- read.csv(csv_path, row.names = 1)

# Creating an xts series and calculating returns
prices <- xts(df$Close, order.by = as.Date(rownames(df)))
returns <- Return.calculate(prices)
returns <- na.omit(returns)

# Calculation of Risk Metrics
cvar_95 <- ES(returns, p = 0.95, method = "historical")
sharpe <- SharpeRatio(returns, Rf = 0.02 / 252, FUN = "StdDev") * sqrt(252)

cat(sprintf("R_CVAR95:%.6f\n", as.numeric(cvar_95)))
cat(sprintf("R_SHARPE:%.6f\n", as.numeric(sharpe[1])))