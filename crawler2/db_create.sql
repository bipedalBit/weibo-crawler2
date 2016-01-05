CREATE DATABASE  IF NOT EXISTS `crawl_result` /*!40100 DEFAULT CHARACTER SET utf8 COLLATE utf8_bin */;
USE `crawl_result`;
-- MySQL dump 10.13  Distrib 5.5.46, for debian-linux-gnu (x86_64)
--
-- Host: 127.0.0.1    Database: crawl_result
-- ------------------------------------------------------
-- Server version	5.5.46-0ubuntu0.14.04.2

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `weibo`
--

DROP TABLE IF EXISTS `weibo`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `weibo` (
  `id` int(11) NOT NULL AUTO_INCREMENT COMMENT '微博数据ID',
  `weibo_id` varchar(20) COLLATE utf8_bin NOT NULL COMMENT '微博UUID即唯一标识',
  `weibo_user` varchar(45) COLLATE utf8_bin NOT NULL COMMENT '微博po主',
  `weibo_user_url` varchar(45) COLLATE utf8_bin NOT NULL COMMENT '微博po主主页链接',
  `datetime` datetime NOT NULL COMMENT '微博时间',
  `client` varchar(45) COLLATE utf8_bin NOT NULL COMMENT '微博客户端',
  `content` varchar(280) COLLATE utf8_bin NOT NULL COMMENT '微博正文',
  `image_url` varchar(45) COLLATE utf8_bin DEFAULT NULL COMMENT '微博图片链接',
  `attitude_cnt` int(11) NOT NULL COMMENT '微博点赞数',
  `repost_cnt` int(11) NOT NULL COMMENT '微博转发数',
  `comment_cnt` int(11) NOT NULL COMMENT '微博评论数',
  `comment_url` varchar(64) COLLATE utf8_bin NOT NULL COMMENT '微博评论链接',
  `repost_flag` int(11) NOT NULL COMMENT '是否为转发',
  `org_weibo_user` varchar(45) COLLATE utf8_bin DEFAULT NULL COMMENT '微博原po主',
  `org_weibo_user_url` varchar(45) COLLATE utf8_bin DEFAULT NULL COMMENT '微博原po主主页链接',
  `repost_reason` varchar(280) COLLATE utf8_bin DEFAULT NULL COMMENT '转发理由',
  PRIMARY KEY (`id`),
  UNIQUE KEY `id_UNIQUE` (`id`),
  UNIQUE KEY `weibo_id_UNIQUE` (`weibo_id`)
) ENGINE=InnoDB AUTO_INCREMENT=131 DEFAULT CHARSET=utf8 COLLATE=utf8_bin;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2015-12-24 16:27:59
