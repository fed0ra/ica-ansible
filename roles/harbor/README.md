## 一、访问Harbor Web界面
需为harbor配置代理，将域名harbor.my.com绑定到代理服务器

| 访问地址 | 账号 | 密码 |
| ---- | ---- | ---- |
| http://harbor.my.com:180 | admin | Admin2024$% |

## 二、上传下载Harbor镜像
```
# 配置http镜像仓库可信任
# 如果不添加此配置，login时会报Error response from daemon: Get https://harbor.my.com/v2/: dial tcp 192.168.1.1:443: connect: connection refused

# 编辑docker daemon.json文件
vim /etc/docker/daemon.json
{
"insecure-registries": ["harbor.my.com:180"]
}

# 重启docker
systemctl restart docker
systemctl status docker
cat ~/.docker/config.json

# 登录仓库
docker login http://harbor.my.com:180
Username: admin
Password: 
WARNING! Your password will be stored unencrypted in /root/.docker/config.json.
Configure a credential helper to remove this warning. See
https://docs.docker.com/engine/reference/commandline/login/#credentials-store

Login Succeeded

# 下载镜像
docker pull alpine
# 打标签
docker tag alpine:latest harbor.my.com:180/library/alpine:latest
# 推送到harbor仓库
docker push harbor.my.com:180/library/alpine:latest
```