# officeaanglist  
   可以在AList获得对onlyoffice的支持，含用户权限，支持多人编辑  
   下载docker-compose.yml更改其中的数据库密码，路径等等，
## FROM
   onlyoffice  
   aria2  
   AriaNg  
   AList  
   quart_auth   
## USE     
   docker-compose:  
   执行  
   ```
   git clone https://github.com/Sincejunly/officeaanglist.git
   cd officeaanglist
   touch /path/to/officeaanglist/redis/redis.conf
   sudo docker-compsoe up -d
   ```
   [docker-cli](https://github.com/Sincejunly/officeaanglist/blob/github/docker.md)  
   pdf扩展：  
   ```
   docker exec -it officeaanglist apt-get update
   docker exec -it officeaanglist apt install -y ghostscript
   ```
   pdf转换启动后等待完成会在同级目录下生成新的pdf文件。  
   启动后要等待很长时间，  
   ```   
   ds:docservice: stopped  
   ds:docservice: started  
   ds:converter: stopped  
   ds:converter: started  
   * Reloading nginx configuration nginx  
      ...done.  
   ```  
   出现以上内容代表成功
   删除映射目录app中的文件，以及数据库目录然后可以达到对容器重置的效果。
   然后访问，  
   AList: https://example.com/AList/  
   AriaNg: https://example.com/AriaNg/  
   aria2: https://example.com/aria2/  
   Edier：https://example.com/viewer/  
   AriaNg配置：https://example.com/aria2/jsonrpc  秘钥：QQ943384135
   AList相同  
   AList，Editer账号，通常情况下Editer会和AList同步  
   注：AList，Editer账号本质上没有关联，只是有一定同步关系。
   删除AList账号或者Editer账号不会删除对方的账号。  
   账号：admin
   密码：admin  
   对于AList注册的用户，含有上传文件权限的用户可以访问Editer编辑功能，只启用的用户可以访问Editer但不能编辑  
   对于Editer注册的用户，自动注册AList未启用的账户，需要管理员手动开启用户  
   编写了外部alist逻辑，暂未测试  
   使用时需要将doc后缀文件改为docx后缀
![image](https://github.com/Sincejunly/officeaanglist/assets/96775034/c3967404-9047-48a9-ad7f-7ef28c1314e5)
![image](https://github.com/Sincejunly/officeaanglist/assets/96775034/57504316-98a9-4569-848a-ac76016e1272)  

# TODO  
- [x] 多人协作  
- [ ] onlyoffice多人历史标注支持   
- [ ] hexo博客支持  






