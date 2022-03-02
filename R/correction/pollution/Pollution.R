library(lubridate)
library(rstan)
#library(shinystan)
library(spNNGP)

setwd("/home/lxt/Documents/Code/R/Project/csv")
#setwd(getwd())
temp = list.files(pattern="*.csv")
myfiles = lapply(temp, read.delim, header = T, sep = ",")
cnames = colnames(myfiles[[1]])

for (i in 1:length(myfiles)) {
  colnames(myfiles[[i]])<-cnames
}

alldata = Reduce(function(x, y) merge(x, y, all=TRUE), myfiles)

# unified date
mdy <- mdy(alldata$DATE) 
dmy <- dmy(alldata$DATE) 
mdy[is.na(mdy)] <- dmy[is.na(mdy)] # some dates are ambiguous, here we give 
alldata$DATE <- mdy
#write.table(alldata[,c(1,2,3)],"datafile.txt",sep=" ",row.names=FALSE,col.names = FALSE)
write.table(alldata[,c(1,2,3)],"pollution_datafile.csv",sep=",",row.names=FALSE,col.names = TRUE)

alldata=read.csv("/home/lxt/Documents/Code/R/Project/csv/pollution_datafile.csv",header = T)

longi_0_1= (alldata$LONGITUDE-min(alldata$LONGITUDE))/(max(alldata$LONGITUDE)-min(alldata$LONGITUDE))
lati_0_1 = (alldata$LATITUDE-min(alldata$LATITUDE))/(max(alldata$LATITUDE)-min(alldata$LATITUDE))
pos = as.matrix(cbind(lati_0_1,longi_0_1))
colnames(pos) <- c('lati','longi')
D_pos <- as.matrix(dist(pos))

#---------------------- Build neighbor index by NNMatrix --------------------#
source("NNMatrix.R")
M = 15                 # Number of Nearest Neighbors
NN.matrix <- NNMatrix(coords = pos, n.neighbors = M, n.omp.threads = 2)
#str(NN.matrix)
#par(mfrow=c(1,1))
#Check_Neighbors(NN.matrix$coords.ord, n.neighbors = M, NN.matrix, ind = 3000)

#
y <- alldata$OXMGL
y_bar = mean(y)
y0 = y - y_bar
Y = y0
#-------------------------- Set parameters of priors --------------------------#
N = length(y)

ss = 3 * sqrt(2)                  # scale parameter in the normal prior of sigma 
st = 3 * sqrt(0.1)                # scale parameter in the normal prior of tau     
ap = 3; bp = 0.5                  # shape and rate parameters in the Gamma prior of phi 
#------------------------------ NNGP response ---------------------------------#
options(mc.cores = 3)
data <- list(N = N, M = M, Y = Y[NN.matrix$ord],
             NN_ind = NN.matrix$NN_ind, NN_dist = NN.matrix$NN_dist,
             NN_distM = NN.matrix$NN_distM,
             ss = ss, st = st, ap = ap, bp = bp)

myinits <-list(list(sigma = 1, tau = 0.5, phi = 50),
               list(sigma = 0.2957, tau = 0.2, phi = 5),
               list(sigma = 5, tau = 5, phi = 5))

parameters <- c("sigmasq", "tausq", "phi")
sfit <- stan(
  file = "pollution_response.stan",
  data = data,
  init = myinits,
  pars = parameters,
  iter = 1000,
  chains = 3,
  thin = 1,
  seed = 123
)

save(sfit, file = "sfit.rda")

load(file = "F:/Project/Data/Hypoxia-Stations/csv/sfit.rda")

srmcoefs = summary(sfit)
coefinfo = srmcoefs$summary
#launch_shinystan(sfit)


sigmsq=2.011481
phi=1.018358
tausq = 1.552042

n = length(y)

KM<-function(D){
  return(sigmsq*exp(-1*phi*D))
}
Kn = KM(D_pos)
Knt = Kn+tausq*diag(n)
invKnt = solve(Knt)

invKnty = invKnt%*%y0

allx = read.csv("/home/lxt/Documents/Data/Project/Correction/AllX.csv",header = T)

pollution_location = allx[,c(1,14,13)]

longi_test = (pollution_location$c_long_4236-min(alldata$LONGITUDE))/(max(alldata$LONGITUDE)-min(alldata$LONGITUDE))
lati_test = (pollution_location$c_lat_4326-min(alldata$LATITUDE))/(max(alldata$LATITUDE)-min(alldata$LATITUDE))
pos_test = as.matrix(cbind(lati_test,longi_test))
colnames(pos_test) <- c('lati','longi')

#fmatrix = rbind(pos, pos_test)

N = dim(pos_test)[1]
gp_pred = numeric(N)

e_dist <- function(x0){
  return (sqrt((x0[1]-pos[,1])^2 + (x0[2]-pos[,2])^2))
}

for (i in 1:N) {
  ki = KM(e_dist(pos_test[i,]))
  gp_pred[i] = ki%*%invKnty
}

gp_pred = gp_pred+y_bar

df_gp_pred = as.data.frame(gp_pred)

pollution_pred = cbind(pollution_location,df_gp_pred)

colnames(pollution_pred)<-c("id","longi","lati","pollution_pred")

write.csv(pollution_pred, file = "/home/lxt/Documents/Data/Project/Correction/pollution_pred.csv",sep = ",",row.names = FALSE)
