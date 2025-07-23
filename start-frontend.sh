#!/bin/bash

# 启动前端服务脚本，禁用代理设置
cd "$(dirname "$0")/frontend"

# 清除代理环境变量
unset http_proxy https_proxy ALL_PROXY no_proxy HTTP_PROXY HTTPS_PROXY

# 启动前端开发服务器
npm run dev