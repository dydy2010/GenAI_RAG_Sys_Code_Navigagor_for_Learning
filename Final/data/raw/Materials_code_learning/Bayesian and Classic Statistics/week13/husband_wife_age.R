library(rstan)
library(bayestestR)
library(latex2exp)
rstan_options(auto_write = TRUE)


plot_posterior <- function(params, Rope = c(.4,.5)){
  dens <- density(params$mu)
  max_dens <- max(dens$y)
  hdi_l <- as.numeric(hdi(params$mu)[2])
  hdi_r <- as.numeric(hdi(params$mu)[3])
  
  plot(dens,main="Posterior",col="darkseagreen", TeX("$\\mu$"))
  
  lines(c(hdi_l,hdi_r),c(.12*max_dens,.12*max_dens),col="orange")
  text(hdi_l,.15*max_dens,round(hdi_l,3),cex=.6)
  text(hdi_r,.15*max_dens,round(hdi_r,3),cex=.6)
  text((hdi_l+hdi_r)/2,.15*max_dens,"95% HDI",cex=.6,col="orange")
  
  lines(c(Rope[1],Rope[2]),c(.08*max_dens,.08*max_dens),col="blue")
  text(Rope[1],.05*max_dens,Rope[1],cex=.6)
  text(Rope[2],.05*max_dens,Rope[2],cex=.6)
  text((Rope[1]+Rope[2])/2,.05*max_dens,"ROPE",cex=.6, col="blue")
  
}




data = read.csv("husband_wife.csv")
head(data)
View(data)

diff = data[,"age.husband"] - data[,"age.wife"]
head(diff)


dens = density(diff)
plot(dens)

par(mfrow=c(1,1))
qqnorm(diff)
qqline(diff)

female_height = data[data["gender"]== "Female","height"][0:50]

head(female_height)

dens = density(female_height)
plot(dens)

sd_diff = sd(diff)
sd_diff




modelString = "
data {
  int n;
  real y[n];
}

parameters {
  real<lower=-10,upper=10> mu; # mu的range
  real<lower=4,upper=4.1> sigma; # sigma的range
}

model {
  for (i in 1:n)
    y[i] ~ normal(mu,sigma);
}
" # close quote for modelString

model <- stan_model(model_code=modelString)

n     = length(diff)
y     = diff


stanFit = sampling( object=model , data=list( y = y , n = n ))

params = rstan::extract(stanFit)

plot_posterior(params, Rope=c(-2,2))




