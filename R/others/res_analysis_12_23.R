#============================
# 7/31
# Gom.SSS Results analysis
#============================

#============================
# Part 1
# Core Function: empirical likelihood for real survey data
#============================

empirical_likelihood<-function(nsim,catch_ratio_step,catch_ratio_max,data){
  # nsim: number of re-sampling 
  # catch_ratio_step: e.g. 0.01 we can set the survey number to 100. 0.02 set survey number to 50.
  # catch_ratio_max: the max catch ratio that you want to study
  # data: the SSS results of one perticular number of fish homes which include two cols. one is catched by camera, another is catched by bait.
  
  # number of rows of the data
  ndata = (dim(data))[1]
  # resample size
  n_sample = as.integer(1/catch_ratio_step)
  # the number of catch ratios
  ncr  = as.integer(catch_ratio_max/catch_ratio_step)
  # probabilities for each catch ratio
  pcr = numeric(length = ncr+1)
  
  for(j in 0:ncr){
    # storage for nsim times sampling
    matched = integer(length = nsim)
    for(i in 1:nsim){
      # do sampling without replacement, sample the index. do nsim times.
      sampled_index = sample(1:ndata,n_sample)
      # for each sampling, calculate if the simulation result exact matching with the real survey, yes, set 1, no, set 0.
      if(sum(data[sampled_index,1])+sum(data[sampled_index,2])==j){
        matched[i] = 1
      }
      else{
        matched[i] =0
      }
    }
    # calculate the empirical probability for each catch ratio.
    pcr[j+1] = sum(matched)/nsim
  }
  return(pcr)
}


#============================
# Part 2
# Load data and do re-sampling parallelly.
#============================

# Parameter setting
# number of re-sampling 
nsim = 5000
# catch_ratio_step: e.g. 0.01 we can set the survey number to 100. 0.02 set survey number to 50.
catch_ratio_step = 0.01
# catch_ratio_max: the max catch ratio that you want to study
catch_ratio_max = 2

n_pcr = as.integer(catch_ratio_max/catch_ratio_step) + 1

homes = read.csv("E:/Project/Data/NewData/SSSdata/OriginalSimData/homes.csv",header = F)

for(i in 0:24){
  filepath = paste0("E:/Project/Data/NewData/SSSdata/OriginalSimData/res_main10_",toString(i),".csv")
  re = read.csv(filepath,header = F)
  home = homes[i+1,]
  n = dim(re)[2]/2
  mtrx = matrix(0,ncol=n,nrow=(n_pcr+1))
  for(j in n){
    sim_data = re[,(2*j-1):(2*j)]
    pcr = empirical_likelihood(nsim,catch_ratio_step,catch_ratio_max,sim_data)
    col = c(home[[1]],pcr)
    mtrx[,j] = col
  }
  # convert matrix to csv
  strfn = paste0("pcr",toString(i),".csv")
  write.table(mtrx,file=strfn,sep = ",",col.names = F,row.names = F)
}

#============================
# Part 3
# calculate the empirical function which y is max likelihood and x is the number of fish homes
#============================

# Load data
filepath = "F:/Project/Data/NewData/results.csv"
result = read.csv(filepath,header = F)
a = numeric(length = dim(result)[1]-1)

for(i in 2:dim(result)[1]){
  catch_ratio = (i-2)/100
  max_index = tail(which(result[i,]==max(result[i,])),1)
  # Row max value
  max_probability_by_cr = result[i,max_index]
  # Row max value corresponds to number of homes
  max_probability_by_cr_to_nhomes = result[1,max_index]
  # Column max value
  max_probability_by_nhomes = max(result[-1,max_index])
  if(max_probability_by_cr==max_probability_by_nhomes){
    a[i-1]=1
    #print("yes")
    #print(max_probability_by_cr_to_nhomes)
  }
  else{
    a[i-1]=0
    #print("no")
    #print(max_probability_by_cr_to_nhomes)
  }
}

nHomeWithMaxCred = matrix(0,ncol=3,nrow=dim(result)[2])
for(j in 1:dim(result)[2]){
  nHomeWithMaxCred[j,1] = result[1,j]
  # store the catch ratio * 1000
  id = tail(which(result[-1,j]==max(result[-1,j])),1)
  nHomeWithMaxCred[j,2] = id-1
  # store the max credibility
  nHomeWithMaxCred[j,3] = result[id+1,j]
}

orderByhomes = nHomeWithMaxCred[order(nHomeWithMaxCred[,1]),]
plot(orderByhomes[,1],orderByhomes[,2])
plot(orderByhomes[,3],orderByhomes[,2])
plot(orderByhomes[,1],orderByhomes[,3])
plot(orderByhomes[,3],orderByhomes[,1])

x = orderByhomes[,2]/100
y = orderByhomes[,1]*2.5

plot(x,y,xlab = "Catch Ratio (CR)",ylab = "Empirical maximum likelihood density (EMLD)")

lmd = lm(y~x)
pr.lm <- predict(lmd)
#plot(x,pr.lm)
lines(pr.lm~x, col="red", lwd=2)

ndata <- data.frame(x=c(0.5))
predict(lmd,ndata)

#plot the pmf of fish home is 22, at col 262; fish home is 19 at col 225; fish home is 16 at col 188
pmf16_prob = result[,188][2:15]
pmf16_cr = seq(0,length(pmf16_prob)-1)*0.01
plot(pmf16_cr,pmf16_prob,type="h",col=2,main="Fish homes: 16",xlab="Catch Ratio: x",ylab="pmf:p(x)")
points(pmf16_cr,pmf16_prob,col=2);abline(h=0,col=1)
segments(0.05,0,0.05,0.159,col = 2,lwd = 3.5)

pmf19_prob = result[,225][2:19]
pmf19_cr = seq(0,length(pmf19_prob)-1)*0.01
plot(pmf19_cr,pmf19_prob,type="h",col=4,main="Fish homes: 19",xlab="Catch Ratio: x",ylab="pmf:p(x)")
points(pmf19_cr,pmf19_prob,col=4);abline(h=0,col=1)
segments(0.05,0,0.05,0.1832,col = 4,lwd = 3.5)


pmf22_prob =  result[,262][2:17]
pmf22_cr = seq(0,length(pmf22_prob)-1)*0.01
plot(pmf22_cr,pmf22_prob,type="h",col=3,main="Fish homes: 22",xlab="Catch Ratio: x",ylab="pmf:p(x)")
points(pmf22_cr,pmf22_prob,col=3);abline(h=0,col=1)
segments(0.05,0,0.05,0.1742,col = 3,lwd = 3.5)

# empirical likelihood function cr=0.05
elf_data = as.matrix(result[c(1,7),result[7,]>0])
plot(elf_data[1,],elf_data[2,],type="h",col=1,main="Empirical likelihood function: CR=0.05",xlab="Fish homes: n",ylab="Empirical likelihood: ELF(n)")
points(elf_data[1,],elf_data[2,],col=1);abline(h=0,col=1)
points(19,0.1832,col=4,pch=16)
points(19,0.178,col=4,pch=15)
points(16,0.159,col=2,lwd = 2.5)
points(22,0.1742,col=3,lwd = 2.5)
segments(16,0,16,0.159,col = 2,lwd = 2.5)
segments(19,0,19,0.1832,col = 4,lwd = 2.5)
segments(22,0,22,0.1742,col = 3,lwd = 2.5)

smoothingSpline = smooth.spline(elf_data[1,], elf_data[2,], spar=0.35)
lines(smoothingSpline,col=1,lwd = 1.5)
