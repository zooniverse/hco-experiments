# Import data
path_import <- "D:\\Studium_GD\\Zooniverse\\Data\\export\\"
path_export <- "D:\\Studium_GD\\Zooniverse\\Results\\swap_metadata\\figures_seeing\\"
fname <- "subject_meta_dat.csv"
dat <- read.csv(paste(path_import,fname,sep=""))
dat$gold_label <- as.factor(dat$gold_label)

# create mag and seeing bins
dat$mag_bin <- cut(dat$mag,breaks = c(13,18,19,20,23))
dat$seeing_bin <- cut(dat$seeing,breaks = c(2, 3, 3.5, 3.9,4.5, 14))

# ggplot(dat,aes(x=seeing_bin,y=seeing)) + geom_boxplot()

# load libararies
library(ggplot2)
library(reshape2)
library(dplyr)
library(pROC)
library(plotROC)




# Plot ROC curve over all subjects but different SWAP processing 
dat_agg <- filter(dat,gold_label %in% c(0,1))
dat_agg$gold_label <- factor(dat_agg$gold_label)
dat_agg$gold_label <- as.numeric(levels(dat_agg$gold_label)[dat_agg$gold_label])
dat_agg <- melt(dat_agg,id.vars=c("X","gold_label","mag_err","mag","seeing","mag_bin","seeing_bin"))

gg <- ggplot(dat_agg,aes(d = gold_label, m = value, color=variable)) + 
  geom_roc(labels=FALSE,n.cuts = 0) + theme_bw() +
  style_roc() +
  ggtitle("ROC Curve Full Dataset - Different Processing")
auc_vals <- calc_auc(gg)
auc_labels <- paste(levels(dat_agg$variable),"(AUC: ",round(auc_vals$AUC,digits=2),")",sep="")
gg2 <- gg + scale_color_brewer(labels = auc_labels,type = "div") + 
  xlab("False Positive (%)") +
  ylab("True Positive (%)")

pdf(file = paste(path_export,"ROC_different_swap_all_subjects.pdf",sep=""),width =10,height = 8)
gg2
dev.off()

# Plot ROC curve over all subjects but different SWAP processing 
gg <- ggplot(filter(dat_agg,!is.na(mag_bin)),aes(d = gold_label, m = value, color=variable)) + 
  geom_roc(labels=FALSE,n.cuts = 0) + theme_bw() + facet_wrap("mag_bin") +
  style_roc() +
  ggtitle("ROC Curve Mag Splits - Different Processing")
gg2 <- gg + scale_color_brewer(type = "div") + 
  xlab("False Positive (%)") +
  ylab("True Positive (%)")

pdf(file = paste(path_export,"ROC_different_swap_mag_splits.pdf",sep=""),width = 10,height = 8)
gg2
dev.off()


# Plot ROC curve over all subjects but different SWAP processing 
gg <- ggplot(filter(dat_agg,!is.na(seeing_bin)),aes(d = gold_label, m = value, color=variable)) + 
  geom_roc(labels=FALSE,n.cuts = 0) + theme_bw() + facet_wrap("seeing_bin") +
  style_roc() +
  ggtitle("ROC Curve Seeing Splits - Different Processing")
gg2 <- gg + scale_color_brewer(type = "div") + 
  xlab("False Positive (%)") +
  ylab("True Positive (%)")

pdf(file = paste(path_export,"ROC_different_swap_seeing_splits.pdf",sep=""),width = 10,height = 8)
gg2
dev.off()


# Plot ROC curve over all subjects but different SWAP processing 
gg <- ggplot(filter(dat_agg,!is.na(mag_bin)),aes(d = gold_label, m = value, color=variable)) + 
  geom_roc(labels=FALSE,n.cuts = 0) + theme_bw() + facet_grid(mag_bin~seeing_bin) +
  style_roc() +
  ggtitle("ROC Curve Mag Splits - Different Processing")
gg2 <- gg + scale_color_brewer(type = "div") + 
  xlab("False Positive (%)") +
  ylab("True Positive (%)")

pdf(file = paste(path_export,"ROC_different_swap_full_splits.pdf",sep=""),width = 14,height = 12)
gg2
dev.off()




# Plot ROC curve over all subjects but different SWAP processing 
gg <- ggplot(filter(dat_agg,!is.na(seeing_bin)),aes(d = gold_label, m = value, color=variable)) + 
  geom_roc(labels=FALSE,n.cuts = 0) + theme_bw() + facet_wrap("seeing_bin") +
  style_roc() +
  ggtitle("ROC Curve Seeing Splits - Different Processing")
gg2 <- gg + scale_color_brewer(type = "div") + 
  xlab("False Positive (%)") +
  ylab("True Positive (%)") +
  xlim(c(0,0.1))

pdf(file = paste(path_export,"ROC_different_swap_seeing_splits_zoom.pdf",sep=""),width = 10,height = 8)
gg2
dev.off()


# Plot ROC curve over all subjects but different SWAP processing 
gg <- ggplot(filter(dat_agg,!is.na(mag_bin)),aes(d = gold_label, m = value, color=variable)) + 
  geom_roc(labels=FALSE,n.cuts = 0) + theme_bw() + facet_grid(mag_bin~seeing_bin) +
  style_roc() +
  ggtitle("ROC Curve Mag Splits - Different Processing")
gg2 <- gg + scale_color_brewer(type = "div") + 
  xlab("False Positive (%)") +
  ylab("True Positive (%)")  +
  xlim(c(0,0.1))

pdf(file = paste(path_export,"ROC_different_swap_full_splits_zoom.pdf",sep=""),width = 14,height = 12)
gg2
dev.off()



# Plot ROC curve over all subjects but different SWAP processing 
gg <- ggplot(filter(dat_agg,!is.na(mag_bin)),aes(d = gold_label, m = value, color=variable)) + 
  geom_roc(labels=FALSE,n.cuts = 0) + theme_bw() + facet_wrap("mag_bin") +
  style_roc() +
  ggtitle("ROC Curve Mag Splits - Different Processing")
gg2 <- gg + scale_color_brewer(type = "div") + 
  xlab("False Positive (%)") +
  ylab("True Positive (%)") +
  xlim(c(0,0.1))

pdf(file = paste(path_export,"ROC_different_swap_mag_splits_zoom.pdf",sep=""),width = 10,height = 8)
gg2
dev.off()


