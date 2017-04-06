######################## -
# load libraries ----
######################## -

library(ggplot2)
library(reshape2)
library(dplyr)

######################## -
# Import data ----
######################## -

path_import <- "D:\\Studium_GD\\Zooniverse\\Data\\export\\"
path_export <- "D:\\Studium_GD\\Zooniverse\\Results\\swap_metadata\\figures_magnitude\\"
fname <- "user_performance_meta.csv"
dat <- read.csv(paste(path_import,fname,sep=""))
str(dat)

# check some users
filter(dat,tp>1000)

######################## -
# User Classification ----
######################## -

# define power users
mega_users <- filter(dat,n>=500) %>%
  group_by(user) %>% summarise(n_bins=n()) %>%
  filter(n_bins==4) %>% mutate(user_type = "1) mega") %>%
  select(user,user_type)

# define power users
power_users <- filter(dat,n>=100) %>%
  group_by(user) %>% summarise(n_bins=n()) %>%
  filter(n_bins==4) %>% mutate(user_type = "2) power") %>%
  select(user,user_type)

# define frequent users
frequent_users <- filter(dat,n>=30) %>%
  group_by(user) %>% summarise(n_bins=n()) %>%
  filter(n_bins==4) %>% mutate(user_type = "3) frequent") %>%
  select(user,user_type)

# define frequent users
casual_users <- filter(dat,n>=10) %>%
  group_by(user) %>% summarise(n_bins=n()) %>%
  filter(n_bins==4) %>% mutate(user_type = "4) casual") %>%
  select(user,user_type)

# define frequent users
rare_users <- filter(dat,n<10) %>%
  group_by(user) %>% summarise(n_bins=n()) %>% mutate(user_type = "5) rare") %>%
  select(user,user_type)

# join user types
user_types <- rbind(mega_users,power_users,frequent_users,casual_users,rare_users)
user_types <- group_by(user_types,user) %>% summarise(user_type=min(user_type))
dat <- left_join(dat,user_types,by="user")

######################## -
# Calculate Stats ----
######################## -

# calculate p(1|real), p(0|bogus)
dat <- mutate(dat,p_tp = tp/pos,p_tn=tn/(n-pos))

# normalize skill levels
dat_norm <- group_by(dat,user) %>% summarise(p_tp_mean=mean(p_tp,na.rm=TRUE),
                                             p_tn_mean=mean(p_tn,na.rm=TRUE))

# normalize skill levels by mag bin and user type
dat_norm_mag <- group_by(dat,mag_bin,user_type) %>% summarise(p_tp_mean_meta=mean(p_tp,na.rm=TRUE),
                                                              p_tn_mean_meta=mean(p_tn,na.rm=TRUE))

dat <- left_join(dat,dat_norm,by="user") %>%
  left_join(dat_norm_mag,by=c("mag_bin","user_type")) %>%
  mutate(p_tp_rel = p_tp - p_tp_mean,
         p_tn_rel = p_tn - p_tn_mean,
         p_tp_rel_meta = p_tp - p_tp_mean_meta,
         p_tn_rel_meta = p_tn - p_tn_mean_meta) %>%
  filter(!is.na(user_type))

# re-shape data set
dat2 <- melt(dat,id.vars = c("user","mag_bin","user_type"),measure.vars = c("p_tp_rel","p_tn_rel"),variable.name = c("Real_Bogus"))
dat3 <- melt(dat,id.vars = c("user","mag_bin","user_type"),measure.vars = c("p_tp","p_tn"),variable.name = c("Real_Bogus"))

dat4 <- melt(dat,id.vars = c("user","mag_bin","user_type"),measure.vars = c("p_tp_rel_meta","p_tn_rel_meta"),variable.name = c("Real_Bogus"))


######################## -
# Visualizations ----
######################## -

lab_sw <- c(
  p_tp = "P(1|Real)",
  p_tn = "P(0|Bogus)"
)

# user absolute skills
gg <- ggplot() +
  geom_boxplot(data=dat3,aes(x=factor(mag_bin),y=value,colour=Real_Bogus)) +
  theme_bw() +
  facet_grid(user_type~Real_Bogus,labeller = labeller(user_type = label_value,Real_Bogus=lab_sw)) +
  xlab("Magnitude Bin") +
  geom_line(data=dat3,aes(x=factor(mag_bin),y=value,group=user,colour=Real_Bogus),alpha=0.3)
gg

pdf(file = paste(path_export,"Mag_vs_UserTypes_Pabsolute.pdf",sep=""),width =10,height = 8)
gg
dev.off()


# relative skill
ggplot(dat,aes(x=factor(mag_bin),y=p_tp_rel,group=user)) +
  geom_line(alpha=0.5,colour="red") +
  theme_bw() +
  facet_grid(user_type~.)


# relative skill tn tp
ggplot(dat2,aes(x=factor(mag_bin),y=value,group=user,colour=Real_Bogus)) +
  geom_line(alpha=0.5) +
  theme_bw() +
  facet_grid(user_type~Real_Bogus)

ggplot(dat2,aes(x=factor(mag_bin),y=value,colour=Real_Bogus)) +
  geom_boxplot() +
  theme_bw() +
  facet_grid(user_type~Real_Bogus) +
  xlab("Magnitude Bin")

lab_sw <- c(
  p_tp_rel = "P(1|Real) - Relative to user mean",
  p_tn_rel = "P(0|Bogus) - Relative to user mean"
)

gg <- ggplot() +
  geom_line(data=dat2,aes(x=factor(mag_bin),y=value,group=user,colour=Real_Bogus),alpha=0.2) +
  theme_bw() +
  geom_boxplot(data=dat2,aes(x=factor(mag_bin),y=value,colour=Real_Bogus)) +
  facet_grid(user_type~Real_Bogus,labeller = labeller(user_type = label_value,Real_Bogus=lab_sw)) +
  xlab("Magnitude Bins")
gg
pdf(file = paste(path_export,"Mag_vs_UserTypes_Prel.pdf",sep=""),width =10,height = 8)
gg
dev.off()
  
# 
# gg <- ggplot() +
#   geom_line(data=dat4,aes(x=factor(mag_bin),y=value,group=user,colour=Real_Bogus),alpha=0.2) +
#   theme_bw() +
#   geom_boxplot(data=dat4,aes(x=factor(mag_bin),y=value,colour=Real_Bogus)) +
#   facet_grid(user_type~Real_Bogus,labeller = labeller(user_type = label_value,Real_Bogus=lab_sw)) +
#   xlab("Magnitude Bins") +
#   ggtitle("Mag-Relative deviations from skill")
# gg
# pdf(file = paste(path_export,"Mag_vs_UserTypes_Prel_Meta.pdf",sep=""),width =10,height = 8)
# gg
# dev.off()
# 



######################## -
# Binomial Model ----
######################## -

# binomial model
m2 <- glm(cbind(pos,tp)~ mag_bin * user,data=filter(dat,user_type %in% c("1) mega","2) power","3) frequent")),family="binomial")
summary(m2)
anova(m2,test="Chisq")
AIC(m2)
drop1(m2,test="Chisq")

m2 <- glm(cbind((n-pos),tn)~ mag_bin * user,data=filter(dat,user_type %in% c("1) mega","2) power","3) frequent")),family="binomial")
summary(m2)
anova(m2,test="Chisq")
AIC(m2)
drop1(m2,test="Chisq")



######################## -
# K-means Clustering ----
######################## -

# clustering
datk <- filter(dat2,user_type %in% c("1) mega","2) power","3) frequent","4) casual") & Real_Bogus == "p_tp_rel")
# datk <- filter(dat2,user_type %in% c("1) mega","2) power") & Real_Bogus == "p_tp_rel")
# datk <- filter(dat4,user_type %in% c("1) mega","2) power","3) frequent","4) casual") & Real_Bogus == "p_tp_rel_meta")

datk_w <- dcast(data = datk,formula = user~mag_bin + Real_Bogus,value.var = "value",fill = 0)

# k-means clustering
km <- kmeans(datk_w[,-1],centers=3)

# assign clusters to observations
datk_w$cluster <- factor(km$cluster)
datk <- left_join(datk,select(datk_w,user,cluster),by="user")

# plot clusters
lab_sw <- c(
  p_tp_rel = "P(1|Real) - Relative to user mean",
  p_tn_rel = "P(0|Bogus) - Relative to user mean"
)
gg <- ggplot() +
  geom_line(data=datk,aes(x=factor(mag_bin),y=value,group=user,colour=cluster),alpha=0.2) +
  theme_bw() +
  geom_boxplot(data=datk,aes(x=factor(mag_bin),y=value,colour=cluster)) +
  facet_grid(user_type~.,scales="free") +
  xlab("Magnitude Bins") +
  ggtitle("K-Means Clustering of Users - P(1|Real) - Relative to user mean")
gg

pdf(file = paste(path_export,"Mag_vs_UserTypes_vs_Clusters_PrelTP.pdf",sep=""),width =10,height = 8)
gg
dev.off()


# clustering
# datk <- filter(dat2,user_type %in% c("1) mega","2) power","3) frequent","4) casual") & Real_Bogus == "p_tp_rel")
# datk <- filter(dat2,user_type %in% c("1) mega","2) power") & Real_Bogus == "p_tp_rel")
datk <- filter(dat4,user_type %in% c("1) mega","2) power","3) frequent") & Real_Bogus == "p_tp_rel_meta")

datk_w <- dcast(data = datk,formula = user~mag_bin + Real_Bogus,value.var = "value",fill = 0)

# k-means clustering
km <- kmeans(datk_w[,-1],centers=3)

# assign clusters to observations
datk_w$cluster <- factor(km$cluster)
datk <- left_join(datk,select(datk_w,user,cluster),by="user")

gg <- ggplot() +
  geom_line(data=datk,aes(x=factor(mag_bin),y=value,group=user,colour=cluster),alpha=0.2) +
  theme_bw() +
  geom_boxplot(data=datk,aes(x=factor(mag_bin),y=value,colour=cluster)) +
  facet_grid(user_type~.,scales="free") +
  xlab("Magnitude Bins") +
  ggtitle("K-Means Clustering of Users - P(1|Real) - Relative to Mag Bin")
gg

pdf(file = paste(path_export,"Mag_vs_UserTypes_vs_Clusters_PrelTP_meta.pdf",sep=""),width =10,height = 8)
gg
dev.off()




datk <- filter(dat2,user_type %in% c("1) mega","2) power","3) frequent","4) casual") & Real_Bogus == "p_tn_rel")
datk_w <- dcast(data = datk,formula = user~mag_bin + Real_Bogus,value.var = "value",fill = 0)

# k-means clustering
km <- kmeans(datk_w[,-1],centers=3)

# assign clusters to observations
datk_w$cluster <- factor(km$cluster)
datk <- left_join(datk,select(datk_w,user,cluster),by="user")

# plot clusters
lab_sw <- c(
  p_tp_rel = "P(1|Real) - Relative to user mean",
  p_tn_rel = "P(0|Bogus) - Relative to user mean"
)
gg <- ggplot() +
  geom_line(data=datk,aes(x=factor(mag_bin),y=value,group=user,colour=cluster),alpha=0.2) +
  theme_bw() +
  geom_boxplot(data=datk,aes(x=factor(mag_bin),y=value,colour=cluster)) +
  facet_grid(user_type~.,scales="free") +
  xlab("Magnitude Bins") +
  ggtitle("K-Means Clustering of Users - P(0|Bogus) - Relative to user mean")
gg
pdf(file = paste(path_export,"Mag_vs_UserTypes_vs_Clusters_PrelTN.pdf",sep=""),width =10,height = 8)
gg
dev.off()
