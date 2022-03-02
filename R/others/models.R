all = as.data.frame(read.csv("E:/Project/Data/NewData/allLabelledData.csv",header = T, sep = ","))
index = (all$gmc>median(all$gmc))&(all$gv<mean(all$gv))
dt = all[index,c(5,6,7,10,11)]

scaled.dt = as.data.frame(scale(dt))

hist(all$gmc,breaks = 100,xlim = c(0,400))
mingmc = quantile(all$gmc,0.4)
abline(v = quantile(all$gmc,0.3))

hist(all$gv,breaks = 100,xlim = c(0,80))
maxgv = quantile(all$gv,0.5)
abline(v = quantile(all$gv,0.5))

hist(all$gsd,breaks = 100,xlim = c(0,25))
quantile(all$gsd,0.5)
mean(all$gsd)

lmd = lm(gsd~.,data = scaled.dt)
summary(lmd)
plot(lmd)
plot(lmd$residuals~scaled.dt$c_lat)
plot(lmd$residuals~scaled.dt$c_long)
plot(lmd$residuals~scaled.dt$depth)
plot(lmd$residuals~scaled.dt$rugosity)


library(e1071)
#Regression with SVM
modelsvm = svm(gsd~.,scaled.dt)
#Predict using SVM regression
predYsvm = predict(modelsvm, data)

#Overlay SVM Predictions on Scatter Plot
points(data$X, predYsvm, col = "red", pch=16)