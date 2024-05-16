
## 配置prometheus，添加监控任务

prometheus安装好后用的是官方的默认配置，并没有监控应用服务器，因此要修改配置，使之从应用服务器采取监控数据，前提被监控服务器已经安装node_exporter

修改配置文件/opt/prometheus/prometheus.yml，添加一个监控任务，在文件尾部增加以下内容

```
   # 新增任务，从应用服务器采集数据 
  - job_name: "192.168.133.152"
    # 抓取时间间隔，抓取间隔时间必须大于抓取超时时间
    scrape_interval: 15s
    # 抓取超时时间
    scrape_timeout: 10s
    # 抓取地址
    static_configs:
      - targets: ["192.168.133.152:9100"]
```

## 配置prometheus，使告警到达alertmanager

alertmanager安装好后，prometheus还不知道alertmanager服务已就绪，需要修改prometheus的配置文件prometheus.yml，让它知道alertmanager在哪里

```

```

## 重启prometheus
```
systemctl restart prometheus
systemctl status prometheus
```

