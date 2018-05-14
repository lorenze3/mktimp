#Titanic intro to machine learning from Kaggle -- heavily relying on kernels

setwd("C:\\Users\\TeamLorenzen\\Documents\\KaggleTitanic")
train <- read.csv("train.csv")

#ok, impute mode as missing values for all columns except cabin

#first create a function to replace NAs in a column ith th emodel

Impute<-function(v1){
  q <- mode(v1,na.rm=TRUE)
  v1[is.na(v1)]<- q
  return v1
}


train2<-sapply(train,Impute)