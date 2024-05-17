
## 一、配置prometheus，添加监控任务

prometheus安装好后用的是官方的默认配置，并没有监控应用服务器，因此要修改配置，使之从应用服务器采取监控数据，前提被监控服务器已经安装node_exporter

1. 修改配置文件/opt/prometheus/prometheus.yml，添加一个监控任务，在文件尾部增加以下内容

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

2. 重启prometheus
```
systemctl restart prometheus
systemctl status prometheus
```

## 二、配置prometheus告警规则

每个告警规则有五部分组成：名称（alert）、触发条件（expr）、持续时间（for）、标签（labels）、注解（annotations）

告警的三种状态：Incative、Pending、Firing

Incative：状态正常

Pending：规则匹配成功，但持续时间在规定时间内

Firing：Pending规则匹配超过持续时间后，触发告警

1. 新建告警规则文件
```
mkdir /opt/prometheus/rules
cat /opt/prometheus/rules/cpu.rules
# 告警规则分组，每一个组下有多个告警规则
groups:
# 组名
- name: cpuAlertGroup
  # 告警规则数组
  rules:
  # 下面是一个具体的告警规则，名为hostCPUUsageTooHigh
  - alert: hostCPUUsageTooHigh
    # 基于PromQL的具体规则，这里是CPU使用率高于50%
    expr: (1 - sum(increase(node_cpu_seconds_total{mode="idle"}[1m])) by (instance) / sum(increase(node_cpu_seconds_total[1m])) by (instance) ) * 100 > 50
    # 持续时间，实际情况满足expr后，规则从inactive
    for: 30s
    # 给规则自身设置标签，不能用减号(-)但是能用下划线(_)
    labels:
      biz_type: cpu_usage
    annotations:
      # 告警内容摘要，可以用表达式获取变量的值
      summary: "Instance {{ $labels.instance }} CPU usgae high"
      # 告警内容详情，可以用表达式获取变量的值
      description: "{{ $labels.instance }} CPU usage above 50% (current : {{ $value }})"
```

2. 修改prometheus的配置文件prometheus.yml，通过配置rule_files参数的值，告诉prometheus在何处加载告警规则配置文件
```
vim /opt/prometheus/prometheus.yml
...
rule_files:
  # - "first_rules.yml"
  # - "second_rules.yml"
  # 包括指定目录下所有rules后缀的文件
  - "/opt/prometheus/rules/*.rules"
...
```

3. 重启prometheus，打开prometheus的web UI的Alerts标签，可以看到告警规则已加载成功
```
systemctl restart prometheus
systemctl status prometheus
```

## 三、配置prometheus告警通知，使告警到达alertmanager

1. alertmanager安装好后，prometheus还不知道alertmanager服务已就绪，需要修改prometheus的配置文件prometheus.yml，让它知道alertmanager在哪里

```
vim /opt/prometheus/prometheus.yml
...
alerting:
  alertmanagers:
    - static_configs:
      - targets: [192.168.133.151:9093]   # 增加alertmanager的地址
          # - alertmanager:9093
...
```

2. 重启prometheus
```
systemctl restart prometheus
systemctl status prometheus
```

## 四、配置alertmanager，使通知到达web服务

当配置完第三步，现在prometheus的告警可以到达alertmanager了，然后要考虑的是alertmanager如何处理这个告警，按照最初的目标，就是alertmanager会发起webhook，于是就需要在alertmanager上做配置，让它知道收到告警后该怎么做

alertmanager的告警通知配置共有以下五部分：

a. 全局配置(global)：一些通用的全局参数

b. 模板(templates)：告警通知用的模板

c. 告警路由(route)：指定特定的告警去特定的通知目标，例如A告警走webhook，B告警走邮件通知

d. 通知接受者(receivers)：定义通知目标，例如webhook、邮件等

e. 抑制规则(inhibit_rules)：对告警进行收敛的规则，避免产生无用告警

1. 修改alertmanager的配置文件alertmanager.yml
```
vim /opt/alertmanager/alertmanager.yml
global:
  # 全局配置，收到告警后，如果持续10分钟都没再收到告警，就把告警状态标记为resolved（已解决）
  resolve_timeout: 10m
route:
  # 分组，处于同一组的告警会被合并为同一个通知
  # 这里设置的是alertname相同的告警会被合并为同一个通知
  group_by: ['alertname']
  # 30秒是个时间窗口，这个窗口内，同一个分组的所有消息会被合并为同一个通知
  group_wait: 30s
  # 同一个分组发送一次合并消息之后，每隔1分钟检查一次告警，判断是否要继续对此告警做操作
  group_interval: 1m	# 5m
  # 按照group_interval的配置，每隔1每分钟检查一次，等到第六次时，1*6=6，大于repeat_interval的5m，此时就会在再次发送告警
  repeat_interval: 5m	# 1h
  # 指定具体的通知方式
  # 简单起见，这里只配置了顶级路由，没有针对故障的标签进行细分
  receiver: 'web.hook'
receivers:
  - name: 'web.hook'
    webhook_configs:
      # alertmanager发起web请求的地址
      - url: 'http://192.168.133.151:8888/webhook'
# 告警抑制规则，可以有多条
inhibit_rules:
  # 这个规则的意思是：一旦收到critical级别的告警，那么再收到低级别(warning)的告警就没必要通知了，
  # 还有一处非常重要的比较，就是低级别告警的node标签的值，要和critical级别告警的node标签的值要相等，也就是确保两个告警的来源相同
  - source_match:
      severity: 'critical'
    target_match:
      severity: 'warning'
    equal: ['node']	# ['alertname', 'dev', 'instance']
```

上面配置的webhook_configs，地址是http://192.168.133.151:8888/webhook，这是自己写的一个web服务，只要alertmanager收到prometheus发来的告警，就会调用这个web接口，需要自己写服务实现

2. 重启alertmanager
```
systemctl restart alertmanager
systemctl status alertmanager
```

3. 虽然配置了webhook，但是webhook的地址是个不存在的服务，alertmanager的告警通知则会发生调用失败，通过日志确认
```
# 查看alertmanager的进程ID
ps -ef | grep alertmanager | grep -v grep
prometh+ 1457375       1  0 08:50 ?        00:00:08 /opt/alertmanager/alertmanager --config.file=/opt/alertmanager/alertmanager.yml --storage.path=/data/alertmanager/data

# 用命令journalctl _PID=xxx查看alertmanager日志
journalctl _PID=1457375

# 内容如下所示，可见alertmanager确实根据配置向http://192.168.133.151:8888/webhook发起了web调用，遇到了connection refused错误
May 17 10:55:18 hdss133-151.host.com alertmanager[1521304]: ts=2024-05-17T02:55:18.186Z caller=notify.go:848 level=warn component=dispatcher receiver=web.hook integration=webhook[0] aggrGroup="{}:{alertname=\"hostCPUUsageTooHigh\"}" msg="Notify attempt failed, will retry later" attempts=1 err="Post \"<redacted>\": dial tcp 192.168.133.151:8888: connect: connection refused"
```

webhook服务项目地址：my/golang/alertmanager-webhook

