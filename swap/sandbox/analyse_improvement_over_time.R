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
path_export <- "D:\\Studium_GD\\Zooniverse\\Results\\SN\\figures_user_skill_development\\"
fname <- "classifications_dat.csv"
dat <- read.csv(paste(path_import,fname,sep=""))

# remove -1 labels
dat <- filter(dat,!gold_label %in% c(-1))

#dat <- select(dat,-X)
str(dat)


############################# -
# Enumerate Classifications  ----
# according to temporal
# occurrence for each user
# and group users
############################## -

dat_r <- arrange(dat,user_name,X) %>% 
  group_by(user_name) %>%
  mutate(rank=row_number(),x_correct = ifelse(annotation==gold_label,1,0)) 

dat_r <- left_join(dat_r,group_by(dat_r,user_name) %>% 
                     summarize(n_class = max(rank)),by="user_name") %>%
  mutate(user_type = cut(n_class,right = TRUE,breaks=c(0,10,50,500,Inf),
                         labels=c("Rare","Casual","Regular","Power"),
                         ordered_result = TRUE)) %>%
  mutate(ml_score = cut(machine_score,right = TRUE,breaks=c(0,0.25,0.5,0.75,1),
                         labels=c("Q1 - ML Score","Q2 - ML Score","Q3 - ML Score","Q4 - ML Score"),
                         ordered_result = TRUE))  

# create rank buckets to pool enough TP in certian ranks
brks <- c(seq(0,100,10),seq(100,max(dat_r$rank),100))
brks <- unique(brks)

brks <- c(seq(0,500,30),Inf)
dat_r <- mutate(dat_r,rank_bucket = cut(rank,breaks = brks))

######################## -
# Analyse Improvement over time ----
######################## -

# group over type and rank
# dat_r2 <- group_by(dat_r,user_type,gold_label,rank) %>%
#   summarize(n=n(),n_correct=sum(x_correct))
# 
# dat_r3 <- group_by(dat_r2,user_type,gold_label) %>%
#   mutate(n_total = cumsum(n),n_total_correct = cumsum(n_correct), lag.sum = lag(n_total),
#          delta_total = n_total - lag.sum)
  

# group over ranks
dat_r2 <- group_by(dat_r,gold_label,rank_bucket) %>%
  summarize(p_correct = sum(x_correct)/n(), support = n()) %>%
  filter(support >=50) 



gg <- ggplot(dat_r2,aes(x=factor(rank_bucket),y=p_correct,colour=factor(gold_label),group=gold_label)) +
  geom_line() +
  #facet_wrap("ml_score",scales = "free") +
  theme_bw()+
  xlab("Classification number of each volunteer") +
  ylab("% correct") +
  ggtitle("User Skill development over time") +
  theme(axis.text=element_text(size=6))
gg
pdf(file = paste(path_export,"User_Skill_dev_over_time_pooled.pdf",sep=""),width =10,height = 5)
gg
dev.off()

dat_r2 <- group_by(dat_r,gold_label,rank_bucket,ml_score) %>%
  summarize(p_correct = sum(x_correct)/n(), support = n()) %>%
  filter(support >=50) 
gg <- ggplot(dat_r2,aes(x=factor(rank_bucket),y=p_correct,colour=factor(gold_label),group=gold_label)) +
  geom_line() +
  facet_wrap("ml_score",scales = "free") +
  theme_bw()+
  xlab("Classification number of each volunteer") +
  ylab("% correct") +
  ggtitle("User Skill development over time - along ML score buckets") +
  theme(axis.text=element_text(size=6))
gg
pdf(file = paste(path_export,"User_Skill_dev_over_time_ml_score.pdf",sep=""),width =10,height = 5)
gg
dev.off()




# create rank buckets to pool enough TP in certian ranks
brks <- c(seq(0,10,2),seq(10,100,10),seq(100,max(dat_r$rank),1000),seq(1000,max(dat_r$rank),10000))
brks <- unique(brks)
dat_r <- mutate(dat_r,rank_bucket = cut(rank,breaks = brks))
dat_r2 <- group_by(dat_r,gold_label,rank_bucket,user_type) %>%
  summarize(p_correct = sum(x_correct)/n(), support = n()) %>%
  filter(support >=50) 

gg <- ggplot(dat_r2,aes(x=factor(rank_bucket),y=p_correct,colour=factor(gold_label),group=gold_label)) +
  geom_line() +
  facet_wrap("user_type",scales = "free") +
  theme_bw()+
  xlab("Classification number of each volunteer") +
  ylab("% correct") +
  ggtitle("User Skill development over time") +
  theme(axis.text=element_text(size=6))
gg
pdf(file = paste(path_export,"User_Skill_dev_over_time_user_types.pdf",sep=""),width =10,height = 5)
gg
dev.off()




# create rank buckets to pool enough TP in certian ranks
brks <- c(seq(0,10,2),seq(10,100,10),seq(100,max(dat_r$rank),1000),seq(1000,max(dat_r$rank),20000))
brks <- unique(brks)
dat_r <- mutate(dat_r,rank_bucket = cut(rank,breaks = brks))
dat_r2 <- group_by(dat_r,gold_label,rank_bucket,user_type) %>%
  summarize(p_correct = sum(x_correct)/n(), support = n(),n_users = n_distinct(user_name)) %>%
  filter(support >=50 & n_users >=20) 

gg <- ggplot(dat_r2,aes(x=factor(rank_bucket),y=p_correct,colour=factor(gold_label),group=gold_label)) +
  geom_line() +
  facet_wrap("user_type",scales = "free_x") +
  theme_bw()+
  xlab("Classification number of each volunteer") +
  ylab("% correct") +
  ggtitle("User Skill development over time - with restrictions") +
  theme(axis.text=element_text(size=6))
gg
pdf(file = paste(path_export,"User_Skill_dev_over_time_user_types_restrictions.pdf",sep=""),width =10,height = 5)
gg
dev.off()




# create rank buckets to pool enough TP in certian ranks
brks <- c(seq(0,10,2),seq(10,100,10),seq(100,max(dat_r$rank),1000),seq(1000,max(dat_r$rank),20000))
brks <- unique(brks)
dat_r <- mutate(dat_r,rank_bucket = cut(rank,breaks = brks))
dat_r2 <- group_by(dat_r,rank_bucket,user_type) %>%
  summarize(precision = sum((x_correct * gold_label)/n()), 
            recall_pos = sum((x_correct * gold_label)/sum(gold_label)),
            recall_neg = sum((x_correct * (gold_label==0))/sum(gold_label==0)),
            accuracy = sum(x_correct) / n(),
            support = n(),n_users = n_distinct(user_name)) %>%
  filter(support >=50 & n_users >=20) %>% 
  mutate(f1 = 2* (precision * recall_pos)/(precision + recall_pos))


library(reshape2)
dat_r3 <- melt(id.vars=c("rank_bucket","user_type","support","n_users"),data=dat_r2)

gg <- ggplot(dat_r3,aes(x=factor(rank_bucket),y=value,colour=variable,group=variable)) +
  geom_line() +
  facet_wrap("user_type",scales = "free_x") +
  theme_bw()+
  xlab("Classification number of each volunteer") +
  ylab("% correct") +
  ggtitle("User Skill development over time") +
  theme(axis.text=element_text(size=6))
gg
pdf(file = paste(path_export,"User_Skill_dev_over_time_user_types_measures.pdf",sep=""),width =10,height = 5)
gg
dev.off()




