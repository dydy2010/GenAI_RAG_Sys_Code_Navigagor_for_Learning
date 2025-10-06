# exercises week 13 last class
library(rstan)
library(bayestestR)
library(latex2exp)
rstan_options(auto_write = TRUE)
plot_posterior <- function(params, Rope = c(-100,.-99)){
  dens <- density(params$mu)
  max_dens <- max(dens$y)
  hdi_l <- as.numeric(hdi(params$mu)[2])
  hdi_r <- as.numeric(hdi(params$mu)[3])
  plot(dens, main="Posterior", col="darkseagreen", TeX("$\\mu$"), lwd=2)
  lines(c(hdi_l,hdi_r), c(.12*max_dens,.12*max_dens), col="orange", lwd=2)
  text(hdi_l, .15*max_dens, round(hdi_l,3), cex=.8)
  text(hdi_r, .15*max_dens, round(hdi_r,3), cex=.8)
  text((hdi_l+hdi_r)/2, .15*max_dens, "95% HDI", cex=.8, col="orange")
  lines(c(Rope[1],Rope[2]), c(.08*max_dens, .08*max_dens), col="blue", lwd=2)
  text(Rope[1], .05*max_dens,Rope[1], cex=.8)
  text(Rope[2], .05*max_dens,Rope[2], cex=.8)
  text((Rope[1]+Rope[2])/2, .05*max_dens, "ROPE", cex=.8, col="blue")
}
# above code is provided

# Problem 13.1
# A wine merchant claims that the wine bottles he fills contain 70 centilitres. However,
# a sceptical consumer suspects that the wine merchant does not fill the bottles with
# enough wine and wants to “check” this claim. Therefore, he buys 12 bottles of wine
# and measures their contents. He finds:
#  71, 69, 67, 68, 73, 72, 71, 71, 68, 72, 69, 72 (in centiliters)
# First, assume that the standard deviation of the bottling is known in advance. It is
# σ = 1.5 centilitres.

# a) Check whether a normal distribution assumption is justified. Justify your an-swer!
wine<-c(71, 69, 67, 68, 73, 72, 71, 71, 68, 72, 69, 72)
mean_wine<-mean(wine)
sd_wine<-1.5
quantile(wine,prob=0.05)
qnorm(p=0.05,mean_wine,sd_wine)
# The empirical quantile from the data.
# The theoretical quantile assuming a normal distribution with the same mean and standard deviation.
qqnorm(wine)
qqline(wine)
# qqnorm(wine):
# Plots the quantiles of your data (wine) against the theoretical quantiles of a normal distribution.
# qqline(wine): Adds a reference line (based on a normal distribution with the same mean and sd as wine) to the Q-Q plot.

# b) We choose a uniform prior distribution and express a high degree of uncertainty
# because we do not trust the wine merchant. How would you choose the boundaries of the uniform distribution?
# my answer: I would choose a smaller value for the boundaries a and b, because we
# don't trust wine merchant, with high uncerntainty. Uniform(65,75)

# c) Determine the 95 %-HDI and the mode of the data.
density_wine <- density(wine)
mode_estimate <- density_wine$x[which.max(density_wine$y)]
plot(density_wine)
mode_estimate
# install.packages("HDInterval")  # If not already installed
library(HDInterval)
hdi_95 <- hdi(mean_wine, credMass = 0.95)
print(hdi_95)

#next part is totally gpt






#d) We know that the wine bottles are filled with very high accuracy.Choose appropriate ROPE.
# answer: Rope is then maybe 90-98, it is a region that is less than 5% possible for the wine packaging.

# e) how would you interpret the result


