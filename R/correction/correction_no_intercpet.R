library(rstan)
library(shinystan)
setwd("F:/Project/Code/R/Correction/")
#------------------------- load and prepare data ---------------------------#
all_data = read.csv("F:/Project/Data/Correction/correction_data.csv")

X <- as.matrix(all_data[,c(3,5)])      # pollution + overfishing
#X <- as.matrix(cbind(1, all_data[,3]))            # pollution
y_pred <- all_data[, 4]
y_cpue <- all_data[, 2]
dist <- 100/all_data[, 6]

#-------------------------- Set parameters of priors --------------------------#
N = length(y_pred)

# Generally include pollution and overfishing ======================================
P = 2                             # number of regression coefficients, generally, pollution and overfishing
uB = c(0,0)                 # mean vector in the Gaussian prior of beta
VB = diag(c(1,1))                      # covariance matrix in the Gaussian prior of beta

# Only include pollution for red snapper ===========================================
#P = 1                             # there is only pollution effective for red snapper.
#uB = c(0,0)                 # mean vector in the Gaussian prior of beta
#VB = diag(c(1,1))                      # covariance matrix in the Gaussian prior of beta

sr = 0.5                  # scale parameter in the normal prior of sigma 
sc = 0.5                # scale parameter in the normal prior of tau     
sk = 1
#------------------------------ NNGP response ---------------------------------#
options(mc.cores = 1)
data <- list(N = N, P = P, X = X, uB = uB, VB = VB, Y_i_pred = y_pred, Dinv_i = dist, Y_i_cpue = y_cpue, sr = sr, sc = sc, sk = sk)

#myinits <-list(list(beta = c(0,0,0), tau = 0.5, sigma = 1, k = 2),
#               list(beta = c(0.5,0.5,0.5), tau = 0.2, sigma = 0.2957, k = 10),
#               list(beta = c(0,0,0), tau = 0.5, sigma = 1, k = 5))

myinits <-list(list(beta = c(0,0), tau = 0.5, sigma = 1, k = 1, resi_cpue=rep(0,N)))
#myinits <-list(list(beta = c(0,0), tau = 0.5, sigma = 1, k = 1, resi_cpue=rep(0,N)))

parameters <- c("beta", "sigmasq", "tausq", "k")
samples <- stan(
  file = "correction_no_intercpet.stan",
  data = data,
  init = myinits,
  pars = parameters,
  iter = 10000,
  chains = 1,
  thin = 1,
  seed = 123,
  control = list(adapt_delta = 0.995)
)

#save(samples, file = "correction_rs_all.rda")
#save(samples, file = "correction_rs_pollution.rda")
#save(samples, file = "correction_rs_nointercept.rda")

load(file = "F:/Project/Code/R/Correction/correction_rs_pollution.rda")
load(file = "F:/Project/Code/R/Correction/correction_rs_all.rda")
load(file = "F:/Project/Code/R/Correction/correction_rs_nointercept.rda")

launch_shinystan(samples)
