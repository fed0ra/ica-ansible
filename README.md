# ica-ansible
安装集群组件

适配centos7/ubuntu22，ubuntu22.04.3已测


## 前提
开通ansible管理机和其他被控端主机SSH互信

可通过SSH主机批量互信认证脚本：https://github.com/fed0ra/batch-sshkey

或者手动操作（ansible管理机上执行）

    # 生成秘钥，执行如下命令在/root/.ssh/目录下生成秘钥
    ssh-keygen -t rsa 

    # 复制主机端公钥到所有被控端
    ssh-copy-id -i /root/.ssh/id_rsa.pub root@<IP>
    ssh-copy-id -i /root/.ssh/id_rsa.pub root@<IP>
    ...

## 1. 修改hosts文件,根据规划修改对应IP和名称.

## 2. 修改group_vars/all.yml文件,自定义软件包目录等

## 3. 下载离线安装包
    # 授权
    chmod +x icadown 
    # 查看帮助
    ./icadown -h

    # 下载所有安装包
    ./icadown -D

    # 下载指定安装包
    ./icadown -P mysql

## 4. 部署
    # 授权
    chmod +x ica
    # 查看帮助
    ./ica -h

    # 部署Nginx:
    ./ica 01

    # 部署Keepalived:
    ./ica 02
