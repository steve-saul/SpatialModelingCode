#============================
# 7/31
# Gom.SSS Results analysis
#============================


# Part 1
#============================
# Helper functions
#============================
# function: catch rate summary
catch_rate_summary <- function(data,pd){
  nrows = (dim(data))[1]
  nhomes = (dim(data))[2]/pd
  nlds = (dim(data))[3]
  # storage variables
  catch_rate = array(dim = c(nhomes,3,nlds))
  
  for(i in 1:nlds){
    for(j in 1:nhomes){
      catch_rate[j,1,i] = sum(data[,(((j-1)*pd)+1),i])/nrows
      catch_rate[j,2,i] = sum(data[,(((j-1)*pd)+2),i])/nrows
      catch_rate[j,3,i] = catch_rate[j,1,i]+catch_rate[j,2,i]
    }
  }
  return(catch_rate)
}

# function: empirical likelihood for real survey data
empirical_likelihood <- function(real_catched,sample_size,nsim,data,period,nhomes){
  # real_catched: the number of real catched fishes you want to study, assigned by the user.
  # sample_size: how many times in the samplings catched the "real_catched" number of fishes, assigned by the user.
  # nsim: number of re-sampling
  # data: data
  # period: number of cols for each "nhomes"
  # nhomes: max possible number of homes
  
  # number of rows of the data
  ndata = (dim(data))[1]
  
  # Store results for each home
  pnh = numeric(length = nhomes)
  
  for(j in 1:nhomes){
    # storage for nsim times sampling
    matched = integer(length = nsim)
    for(i in 1:nsim){
      # do sampling without replacement, sample the index. do nsim times.
      sampled_index = sample(1:ndata,sample_size)
      # for each sampling, calculate if the simulation result exact matching with the real survey, yes, set 1, no, set 0.
      if(sum(data[sampled_index,(((j-1)*period)+1)])+sum(data[sampled_index,(((j-1)*period)+2)])==real_catched){
        matched[i] = 1
      }
      else{
        matched[i] =0
      }
    }
    # calculate the empirical probability for each number of home.
    pnh[j] = sum(matched)/nsim
  }
  return(pnh)
}


E:\Project\Data\NewData\SSSdata\OriginalSimData

# Part 2
#============================
# Load data
re = read.csv("E:/Project/Data/Simulation data/2017.7.31/res_main10.csv",header = F)
# in each simulation, the number of cols and rows
re_rows = dim(re)[1]
re_cols = dim(re)[2]
# number of lmds
nlmds = 11
# Variable for data storage, 3 dimensional array
res = array(dim = c(dim(re),11))
for(i in 0:10){
  if (i == 10){
    filepath = "E:/Project/Data/Simulation data/2017.7.31/res_main20.csv"
  } else{
    filepath = paste0("E:/Project/Data/Simulation data/2017.7.31/res_main1",toString(i),".csv")
  }
  #print(filepath)
  re = read.csv(filepath,header = F)
  res[,,(i+1)] = data.matrix(re)
}
# Delete variable re
remove(re)

# Part 3
#============================
# Analysis
#============================
# 3.1 Parameters
# number of cols for each number of home
period = 2
# max possible homes
n = re_cols/period
# x line for plot
x_h = 1:n
x_lmd = seq(0.10,0.20,by = 0.01)
# number of re-sampling in the empirical likelihood analysis
nsim = 5000
# re-sampling size in the empirical likelihood analysis
n_resampling = 20
# max number of fish in the empirical likelihood analysis
nfish_ela = 5

#===========================
# 3.2 Do analysis
#===========================
# 3.2.1 Catch rate analysis
crs = catch_rate_summary(res,period)

#===========================
# plot
par(mfrow=c(2,2))
for(i in c(1,4,8,11)){
  if(i==11){
    plot(x_h,crs[,3,i],type = "o",xlab = "Number of Homes",ylab = "Detect Rate",main = "Detection rate of different home number, lmd=0.20")
  }else{
    plot(x_h,crs[,3,i],type = "o",xlab = "Number of Homes",ylab = "Detect Rate",main = paste0("Detection rate of different home number, lmd=0.1",toString(i-1)))
  }
  
  lines(x_h,crs[,1,i],type = "o",col = "red")
  lines(x_h,crs[,2,i],type = "o",col = "blue")
  legend("topleft", legend = c("Total","Camera","Bait"), col=c(1,2,4), pch=1, cex = 0.75)
}

layout(matrix(c(1,1,2,3), 2, 2, byrow = TRUE))
# plot total catch rate changing with lambda
plot(x_lmd,crs[112,3,],type = "o",col = 5,ylim = c(0,0.3),xlab = "lmd",ylab = "Total Detect Rate",main = "Total catch rate changing with lambda")
for(i in 1:4){
  lines(x_lmd,crs[i*20,3,],type = "o",col = i)
}
legend("topright", legend = c("Homes:20","Homes:40","Homes:60","Homes:80","Homes:112"), col=1:5, pch=0.5, cex = 0.7)
# plot camera catch rate changing with lambda
plot(x_lmd,crs[112,1,],type = "o",col = 5,ylim = c(0,0.020),xlab = "lmd",ylab = "Camera Detect Rate",main = "Camera catch rate changing with lambda")
for(i in 1:4){
  lines(x_lmd,crs[i*20,1,],type = "o",col = i)
}
legend("topleft", legend = c("Homes:20","Homes:40","Homes:60","Homes:80","Homes:112"), col=1:5, pch=0.5, cex = 0.7)
# plot bait catch rate changing with lambda
plot(x_lmd,crs[112,2,],type = "o",col = 5,ylim = c(0,0.3),xlab = "lmd",ylab = "Bait Detect Rate",main = "Bait catch rate changing with lambda")
for(i in 1:4){
  lines(x_lmd,crs[i*20,2,],type = "o",col = i)
}
legend("topright", legend = c("Homes:20","Homes:40","Homes:60","Homes:80","Homes:112"), col=1:5, pch=0.5, cex = 0.7)

# 3.2.2 Empirical likelihood analysis
# storage
ela_res = array(0,dim = c((nfish_ela+1),n,nlmds))
# calculation
for(i in 1:nlmds){
  for(j in 0:nfish_ela){
    ela_res[j+1,,i]=empirical_likelihood(j,n_resampling,nsim,res[,,i],period,n)
  }
}

ela_lmd = array(-1,dim = c(2,(nfish_ela+1),nlmds))
for(j in 1:nlmds){
  for(i in 1:(nfish_ela+1)){
    smoothingSpline = smooth.spline(x_h, ela_res[i,,j], spar=0.7)
    psmth = predict(smoothingSpline, x_h)
    ela_lmd[1,i,j] = psmth$x[which.max( psmth$y )]
    ela_lmd[2,i,j] = psmth$y[which.max( psmth$y )]
  }
}

#===========================
par(mfrow=c(2,2))
# plot
# lmd = 0.10
plot(x_h,ela_res[2,,1],ylim = c(0,0.4),type = "o",xlab = "Number of Homes",ylab = "Probability",main = paste0(toString(n_resampling)," surveys, with lmd=0.10"),col = 1)
for(i in 2:(nfish_ela+1)){
  smoothingSpline = smooth.spline(x_h, ela_res[i,,1], spar=0.7)
  lines(smoothingSpline,col=i,lwd = 2.5)
}
legend("topright", legend = c("Catch:1","Catch:2","Catch:3","Catch:4","Catch:5"), col=2:6, pch=1, cex = 0.5)
# lmd = 0.13
plot(x_h,ela_res[2,,4],ylim = c(0,0.4),type = "o",xlab = "Number of Homes",ylab = "Probability",main = paste0(toString(n_resampling)," surveys, with lmd=0.13"),col = 1)
for(i in 2:(nfish_ela+1)){
  smoothingSpline = smooth.spline(x_h, ela_res[i,,4], spar=0.7)
  lines(smoothingSpline,col=i,lwd = 2.5)
}
legend("topright", legend = c("Catch:1","Catch:2","Catch:3","Catch:4","Catch:5"), col=2:6, pch=1, cex = 0.5)
# lmd = 0.16
plot(x_h,ela_res[2,,7],ylim = c(0,0.4),type = "o",xlab = "Number of Homes",ylab = "Probability",main = paste0(toString(n_resampling)," surveys, with lmd=0.16"),col = 1)
for(i in 2:(nfish_ela+1)){
  smoothingSpline = smooth.spline(x_h, ela_res[i,,7], spar=0.7)
  lines(smoothingSpline,col=i,lwd = 2.5)
}
legend("topright", legend = c("Catch:1","Catch:2","Catch:3","Catch:4","Catch:5"), col=2:6, pch=1, cex = 0.5)
# lmd = 0.20
plot(x_h,ela_res[2,,11],ylim = c(0,0.4),type = "o",xlab = "Number of Homes",ylab = "Probability",main = paste0(toString(n_resampling)," surveys, with lmd=0.20"),col = 1)
for(i in 2:(nfish_ela+1)){
  smoothingSpline = smooth.spline(x_h, ela_res[i,,11], spar=0.7)
  lines(smoothingSpline,col=i,lwd = 2.5)
}
legend("topright", legend = c("Catch:1","Catch:2","Catch:3","Catch:4","Catch:5"), col=2:6, pch=1, cex = 0.5)

par(mfrow=c(1,1))
plot(x_lmd,ela_lmd[1,2,],ylim = c(0,115),type = "o",ylab = "Number of Homes",xlab = "Lambdas",main = "Number of homes changing with lmds",col = 2)
for(i in 3:(nfish_ela+1)){
  if(i==4){
    lines(x_lmd[1:7],ela_lmd[1,i,][1:7],type = "o",col = i)
  }else if(i==5){
    lines(x_lmd[1:4],ela_lmd[1,i,][1:4],type = "o",col = i)
  }else if(i==6){
    lines(x_lmd[1:2],ela_lmd[1,i,][1:2],type = "o",col = i)
  }else{
    lines(x_lmd,ela_lmd[1,i,],type = "o",col = i)
  }
}
legend("bottomright", legend = c("Catch:1","Catch:2","Catch:3","Catch:4","Catch:5"), col=2:6, pch=1, cex = 0.8)

plot(1:nfish_ela,ela_lmd[1,,1][2:(nfish_ela+1)],ylim = c(0,115),type = "o",ylab = "Number of Homes",xlab = "Catched fishes",main = "Number of homes changing with catched fishes",col = 1)
for(i in 2:4){
  if(i==4){
    lines(1:(nfish_ela-1),ela_lmd[1,,i][2:nfish_ela],type = "o",col = i)
  }else{
    lines(1:nfish_ela,ela_lmd[1,,i][2:(nfish_ela+1)],type = "o",col = i)
  }
}
legend("bottomright", legend = c("lmd:0.10","lmd:0.11","lmd:0.12","lmd:0.13"), col=1:4, pch=1, cex = 0.8)
