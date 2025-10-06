library(rstan)
library(bayestestR)
library(latex2exp)
rstan_options(auto_write = TRUE)


plot_posterior <- function(params, Rope = c(.4,.5)){
  dens <- density(params$theta)
  max_dens <- max(dens$y)
  hdi_l <- as.numeric(hdi(params$theta)[2])
  hdi_r <- as.numeric(hdi(params$theta)[3])
  
  plot(dens,main="Posterior",col="darkseagreen", TeX("$\\theta$"))
  
  lines(c(hdi_l,hdi_r),c(.12*max_dens,.12*max_dens),col="orange")
  text(hdi_l,.15*max_dens,round(hdi_l,3),cex=.6)
  text(hdi_r,.15*max_dens,round(hdi_r,3),cex=.6)
  text((hdi_l+hdi_r)/2,.15*max_dens,"95% HDI",cex=.6,col="orange")
  
  lines(c(Rope[1],Rope[2]),c(.08*max_dens,.08*max_dens),col="blue")
  text(Rope[1],.05*max_dens,Rope[1],cex=.6)
  text(Rope[2],.05*max_dens,Rope[2],cex=.6)
  text((Rope[1]+Rope[2])/2,.05*max_dens,"ROPE",cex=.6, col="blue")

}

modelString = "
data{
int<lower=0> N ;
int y[N] ; // y is a length-N vector of integers
}
parameters {
real<lower=0,upper=1> theta ;
}
model {
theta ~ beta(2,4) ;
y ~ bernoulli(theta) ;
}
" # close quote for modelString

model <- stan_model(model_code=modelString)



N = 50 
z = 10 
y = c(rep(1,z),rep(0,N-z))


stanFit = sampling( object=model , data=list( y = y , N = N ) , chains=3 , iter=10000 , warmup=200)

params = rstan::extract(stanFit)


plot_posterior(params, Rope=c(.6,.8))


