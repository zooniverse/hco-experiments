# Import data
path_import <- "D:\\Studium_GD\\Zooniverse\\Data\\export\\"
path_export <- "D:\\Studium_GD\\Zooniverse\\Results\\swap_metadata\\figures_seeing\\"
fname <- "subject_dat.csv"
dat <- read.csv(paste(path_import,fname,sep=""))
dat$gold_label <- as.factor(dat$gold_label)
dat$label <- as.factor(dat$label)

tpr <- sum(dat$gold_label==1) / dim(dat)[1]
ml_bias <- quantile(dat$machine_score,probs = 1-tpr)
swap_bias <- quantile(dat$score,probs = 1-tpr,na.rm = TRUE)
dat$mlabel <- ifelse(dat$machine_score>ml_bias,1,0)
dat$slabel<- ifelse(dat$score>swap_bias,1,0)

head(dat)

# load libararies
library(ggplot2)
library(reshape2)
library(dplyr)
library(plotRoc)

# analyse

# analyse seeing True positive vs True negative
ggplot(dat,aes(x=seeing,group=gold_label,fill=gold_label)) +
  geom_density(alpha=0.3) + theme_bw() +
  ggtitle("Seeing Density Distribution") +
  scale_fill_brewer(type = "qual")

# number of observations vs seeing
dat_agg <- dat
dat_agg$seeing_bin <- cut(dat_agg$seeing,breaks = quantile(dat_agg$seeing,probs = seq(0,1,0.05),na.rm = TRUE))
dat_agg <- filter(dat_agg,!is.na(seeing_bin))
pdf(file = paste(path_export,"seeing_vs_gold_label.pdf",sep=""),width = 7,height = 5)
ggplot(dat_agg,aes(x=seeing_bin,fill=gold_label)) + geom_bar(position="dodge") +
  theme_bw() +
  scale_fill_brewer(type="qual") +
  ggtitle("Seeing Bin vs Gold-Labels") +
  theme(axis.text=element_text(size=4))
dev.off()

# number of observations vs mag
dat_agg <- dat
dat_agg$mag_bin <- cut(dat_agg$mag,breaks = quantile(dat_agg$mag,probs = seq(0,1,0.05),na.rm = TRUE))
dat_agg <- filter(dat_agg,!is.na(mag_bin))
pdf(file = paste(path_export,"mag_vs_gold_label.pdf",sep=""),width = 7,height = 5)
ggplot(dat_agg,aes(x=mag_bin,fill=gold_label)) + geom_bar(position="dodge") +
  theme_bw() +
  scale_fill_brewer(type="qual") +
  ggtitle("Mag Bin vs Gold-Labels") +
  theme(axis.text=element_text(size=4))
dev.off()

# analyse machine score vs label
ggplot(dat,aes(x=machine_score,colour=gold_label)) + geom_density(lwd=1.5) +
  theme_bw() +
  ggtitle("Machine Score Distr. per Label") +
  scale_color_brewer(type = "qual")

# analyse machine score
pdf(file = paste(path_export,"machine_score_vs_gold_label.pdf",sep=""),width = 7,height = 5)
ggplot(dat,aes(x=machine_score,fill=gold_label)) + geom_histogram(position="dodge") +
  theme_bw() +
  ggtitle("Machine Score Hist")  +
  scale_fill_brewer(type = "qual") +
  theme(axis.text=element_text(size=8))
dev.off()

# analyse quality vs seeing
dat_agg <- dat
dat_agg$seeing_bin <- cut(dat_agg$seeing,breaks = quantile(dat_agg$seeing,probs = seq(0,1,0.05),na.rm = TRUE))

dat_agg <- filter(dat_agg,!is.na(seeing_bin)) %>% 
  group_by(seeing_bin) %>% 
  summarise(tp_swap=sum(slabel==1 & gold_label==1)/sum(gold_label==1),
            tn_swap=sum(slabel==0 & gold_label==0)/sum(gold_label==0),
            fp_swap=sum(slabel==1 & gold_label==0)/sum(gold_label==0),
            fn_swap=sum(slabel==0 & gold_label==1)/sum(gold_label==1),
            tp_machine=sum(mlabel==1 & gold_label==1)/sum(gold_label==1),
            tn_machine=sum(mlabel==0 & gold_label==0)/sum(gold_label==0),
            fp_machine=sum(mlabel==1 & gold_label==0)/sum(gold_label==0),
            fn_machine=sum(mlabel==0 & gold_label==1)/sum(gold_label==1),
            pos = sum(gold_label==1)/n()) %>%
  mutate(f1_swap = (2 * tp_swap)/ (2 * tp_swap + fp_swap + fn_swap),
         f1_machine = (2 * tp_machine)/ (2 * tp_machine + fp_machine + fn_machine))

dat_agg <- melt(dat_agg,id.vars = "seeing_bin")
dat_agg <- filter(dat_agg,!variable %in% c("fn_swap","fn_machine"))
dat_agg <- filter(dat_agg,!variable %in% c("fp_swap","fn_swap","fp_machine","fn_machine"))
ggplot(dat_agg,aes(x=seeing_bin,y=value,group=variable,colour=variable)) + 
  geom_line(lwd=1.5) + theme_bw() +
  ggtitle("Seeing Bins vs TP/TN from SWAP/Machine")

# analyse quality vs magnitude
dat_agg <- dat
dat_agg$mag_bin <- cut(dat_agg$mag,breaks = quantile(dat_agg$mag,probs = seq(0,1,0.05),na.rm = TRUE))

dat_agg <- filter(dat_agg,!is.na(mag_bin)) %>% 
  group_by(mag_bin) %>% 
  summarise(tp_swap=sum(slabel==1 & gold_label==1)/sum(gold_label==1),
            tn_swap=sum(slabel==0 & gold_label==0)/sum(gold_label==0),
            fp_swap=sum(slabel==1 & gold_label==0)/sum(gold_label==0),
            fn_swap=sum(slabel==0 & gold_label==1)/sum(gold_label==1),
            tp_machine=sum(mlabel==1 & gold_label==1)/sum(gold_label==1),
            tn_machine=sum(mlabel==0 & gold_label==0)/sum(gold_label==0),
            fp_machine=sum(mlabel==1 & gold_label==0)/sum(gold_label==0),
            fn_machine=sum(mlabel==0 & gold_label==1)/sum(gold_label==1),
            pos = sum(gold_label==1)/n()) %>%
  mutate(f1_swap = (2 * tp_swap)/ (2 * tp_swap + fp_swap + fn_swap),
         f1_machine = (2 * tp_machine)/ (2 * tp_machine + fp_machine + fn_machine))

dat_agg <- melt(dat_agg,id.vars = "mag_bin")
dat_agg <- filter(dat_agg,!variable %in% c("fn_swap","fn_machine"))
dat_agg <- filter(dat_agg,!variable %in% c("fp_swap","fn_swap","fp_machine","fn_machine"))
ggplot(dat_agg,aes(x=mag_bin,y=value,group=variable,colour=variable)) + 
  geom_line(lwd=1.5) + theme_bw() +
  ggtitle("mag Bins vs TP/TN from SWAP/Machine")



# analyse quality vs seeing
dat_agg <- dat
dat_agg$seeing_bin <- cut(dat_agg$seeing,breaks = quantile(dat_agg$seeing,probs = seq(0,1,0.05),na.rm = TRUE))
dat_agg <- group_by(dat_agg,seeing_bin) %>% summarise(tp_m=sum(mlabel==1 & gold_label==1)/sum(gold_label==1),
                                                      tn_m=sum(mlabel==0 & gold_label==0)/sum(gold_label==0),
                                                      pos = sum(gold_label==1)/n())
dat_agg <- melt(dat_agg,id.vars = "seeing_bin")
ggplot(dat_agg,aes(x=seeing_bin,y=value,group=variable,colour=variable)) + 
  geom_line() + theme_bw() +
  ggtitle("Seeing Bins vs TP/TN from SWAP")


# analyse quality vs magnitude
dat_agg <- dat
dat_agg$mag_bin <- cut(dat_agg$mag,breaks = quantile(dat_agg$mag,probs = seq(0,1,0.05),na.rm = TRUE))
dat_agg <- group_by(dat_agg,mag_bin) %>% summarise(tp=sum(label==1 & gold_label==1)/sum(gold_label==1),
                                                   tn=sum(label==0 & gold_label==0)/sum(gold_label==0),
                                                   pos = sum(gold_label==1)/n())
dat_agg <- melt(dat_agg,id.vars = "mag_bin")
ggplot(dat_agg,aes(x=mag_bin,y=value,group=variable,colour=variable)) + 
  geom_line() + theme_bw() +
  ggtitle("Mag Bins vs TP/TN SWAP")

# Plot ROC curves
library(pROC)
dat_agg <- dat
dat_agg$seeing_bin <- cut(dat_agg$seeing,breaks = quantile(dat_agg$seeing,probs = seq(0,1,0.1),na.rm = TRUE))

dat_agg <- filter(dat_agg,!is.na(seeing_bin)) %>% 
  group_by(seeing_bin) %>% 
  summarise(auc_swap = auc(gold_label,score),
            auc_ml = auc(gold_label,machine_score))

dat_agg <- melt(dat_agg,id.vars="seeing_bin")

pdf(file = paste(path_export,"auc_seeing_bin_swap_ml.pdf",sep=""),width = 7,height = 5)
ggplot(dat_agg,aes(x=seeing_bin,y=value,colour=variable,group=variable)) + geom_line(lwd=1.5) +
  theme_bw() + ggtitle("AUC for different Seeing (SWAP/ML)") +
  scale_color_brewer(type = "qual") +
  theme(axis.text=element_text(size=8))
dev.off()

