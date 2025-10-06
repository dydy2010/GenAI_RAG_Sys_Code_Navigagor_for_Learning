# https://chatgpt.com/share/6826185f-4914-8000-ab38-ef188efa8fc3

# remove.packages("RcppEigen")
# install.packages("RcppEigen", type = "source")

#library(rstan)
#example(stan_model, run.dontrun = TRUE)  # Should now compile


# Remove old installations
# remove.packages(c("rstan", "StanHeaders", "RcppEigen"))

# Reinstall with correct SDK path
# install.packages("StanHeaders", type = "source")
# install.packages("RcppEigen", type = "source")
# install.packages("rstan", repos = "https://mc-stan.org/r-packages/", type = "source")

# Install rstan (Stan for R) from a Stan-specific repository
# install.packages("rstan", repos = "https://mc-stan.org/r-packages/")

# Problem 13.1
# Use the file stan_beta_compare.R to check the approximation of the posterior
# distribution by stan. The top figure is the approximated distribution and the bottom
# figure is the exact posterior distribution we know in this case.
# Play with the options iter=. . . (number of steps after tune-in) and warmup=. . . (The
# first steps that are ignored) around. What can you say about the HDI and mode compared to the exact distribution?
  
library(rstan)
example(stan_model, run.dontrun = TRUE)  # Runs a demo model

library(rstan)
library(bayestestR)
library(latex2exp)

rstan_options(auto_write = TRUE)
modelString = "
data{
int<lower=0> N ;
int y[N] ; // y is a length-N vector of integers
}
parameters {
real<lower=0,upper=1> theta ;
}
model {
theta ~ beta(5,2) ;
y ~ bernoulli(theta) ;
}
" 
# close quote for modelString

model <- stan_model(model_code=modelString)

N = 20
z = 16 
y = c(rep(1,z),rep(0,N-z))

stanFit = sampling( object=model , data=list( y = y , N = N ) , chains=3 , iter=1000 , warmup=100)

params = rstan::extract(stanFit)

dens <- density(params$theta)
plot(dens,
     main = "Posterior",
     col = "darkseagreen",
     xlim = c(0, 1),
     xlab = TeX("$\\theta$"))
max_dens <- max(dens$y)
lines(c(hdi(params$theta)[2],hdi(params$theta)[3]),c(.1*max_dens,.1*max_dens))
x <- seq(0,1,.001)
y <- dbeta(x,5+z,N-z+2)
lines(x,y,col="orange")

#	HDI gives the shortest interval containing X% (e.g., 95%) of the posterior mass.,
# In the exact posterior, you can get this from:
qbeta(c(0.025, 0.975), 21, 6)
hdi(params$theta)
# interpretation: “There is a 95% probability that the true value of θ lies between 0.606 and 0.910, 
# given the prior and observed data.”

# summary of result
#          Method Lower bound

# qbeta (exact)   0.606.  0.910
# hdi() (approx.) 0.620.  0.920
# Stan’s sampled posterior matches the theoretical posterior well — both in shape and in HDI. 
# The small difference (e.g., 0.606 vs. 0.620) is due to sampling variation, HDI is not always symmetric
# ,and the precision of numerical estimation








