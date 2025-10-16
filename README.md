# 天翼云盘签到 - Docker版

基于Docker容器化部署的天翼云盘自动签到工具，支持Web界面管理和双推送服务。

## 功能特点

- 🐳 **Docker容器化部署**
- 🌐 **Web可视化界面**
- 📱 **多账号管理**
- 🔔 **双推送服务** (WxPusher + Server酱)
- 📊 **实时运行日志**
- ⚙️ **在线配置管理**

## 快速开始

### 方式一：使用Docker Compose（推荐）
```bash
直接使用Docker命令
# 创建项目目录
mkdir tianyi-docker && cd tianyi-docker

# 下载docker-compose.yml
curl -O https://raw.githubusercontent.com/your-username/tianyi-docker/main/docker-compose.yml

# 启动服务
docker-compose up -d

# 查看日志
docker-compose logs -f
```
### 方式二：直接使用Docker命令
```bash
# 创建数据目录
mkdir -p tianyi-data tianyi-logs

# 运行容器
docker run -d \
  --name tianyi-sign \
  -p 5000:5000 \
  -v $(pwd)/tianyi-data:/app/data \
  -v $(pwd)/tianyi-logs:/app/logs \
  yourusername/tianyi-docker:latest
```
方式三：从源码构建

```bash
# 克隆项目
git clone https://github.com/your-username/tianyi-docker.git
cd tianyi-docker

# 构建镜像
docker build -t tianyi-docker .

# 运行容器
docker run -d -p 5000:5000 -v $(pwd)/data:/app/data -v $(pwd)/logs:/app/logs tianyi-docker
```

访问Web界面

打开浏览器访问: http://localhost:5000

配置说明

环境变量

变量名 说明 默认值
HOST_PORT 宿主机端口 5000
TZ 时区设置 Asia/Shanghai

数据持久化

· 配置文件: ./data/config.json
· 日志文件: ./logs/tianyi.log

Web界面功能

1. 账号管理: 添加、删除天翼云盘账号
2. 推送配置: 配置WxPusher和Server酱推送
3. 任务执行: 手动触发签到任务
4. 运行状态: 查看运行统计和日志
5. 实时日志: 查看任务执行详情

推送服务配置

WxPusher配置

1. 访问 WxPusher官网
2. 创建应用获取AppToken
3. 关注公众号获取UID
4. 在Web界面中配置

Server酱配置

1. 访问 Server酱官网
2. 登录获取SendKey
3. 在Web界面中配置

定时执行

使用cron定时执行

```bash
# 进入容器
docker exec -it tianyi-sign bash

# 安装cron
apt update && apt install -y cron

# 添加定时任务（每天8点执行）
echo "0 8 * * * curl -X POST http://localhost:5000/api/run" >> /etc/crontab

# 启动cron服务
service cron start
```

使用宿主机的cron

```bash
# 在宿主机添加cron任务
crontab -e

# 添加以下内容（每天8点执行）
0 8 * * * docker exec tianyi-sign curl -X POST http://localhost:5000/api/run
```

更新说明

更新到最新版本

```bash
# 停止并删除旧容器
docker-compose down

# 拉取最新镜像
docker-compose pull

# 重新启动
docker-compose up -d
```

故障排除

1. 检查容器状态
   ```bash
   docker-compose ps
   ```
2. 查看日志
   ```bash
   docker-compose logs -f
   ```
3. 重启服务
   ```bash
   docker-compose restart
   ```

许可证

MIT License

贡献

欢迎提交Issue和Pull Request！

```

## 3. GitHub Actions自动化构建

### 设置GitHub Secrets

1. 在GitHub仓库中，进入 Settings → Secrets and variables → Actions
2. 点击 "New repository secret"
3. 添加以下secrets：
   - `DOCKERHUB_USERNAME`: 你的Docker Hub用户名
   - `DOCKERHUB_TOKEN`: 你的Docker Hub访问令牌

## 4. 部署使用

### 用户使用步骤

```bash
# 1. 创建项目目录
mkdir tianyi-sign && cd tianyi-sign

# 2. 下载docker-compose.yml
curl -O https://raw.githubusercontent.com/your-username/tianyi-docker/main/docker-compose.yml

# 3. 修改镜像名称（如果需要）
# 编辑docker-compose.yml，将yourusername替换为实际的Docker Hub用户名

# 4. 启动服务
docker-compose up -d

# 5. 访问Web界面
# 打开浏览器访问 http://localhost:5000
```

环境变量配置

创建 .env 文件自定义配置：

```bash
# .env
HOST_PORT=8080
DOCKERHUB_USERNAME=your-dockerhub-username
```

5. 发布到Docker Hub

手动发布

```bash
# 登录Docker Hub
docker login

# 构建镜像
docker build -t yourusername/tianyi-docker .

# 推送镜像
docker push yourusername/tianyi-docker:latest
```

通过GitHub Actions自动发布

每次向main分支推送代码或创建tag时，GitHub Actions会自动构建并推送镜像到Docker Hub
