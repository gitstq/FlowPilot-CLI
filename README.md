# 🚀 FlowPilot-CLI

<div align="center">

[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![License](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Platform](https://img.shields.io/badge/Platform-Linux%20%7C%20macOS%20%7C%20Windows-lightgrey.svg)]()

**Lightweight Terminal Workflow Orchestration Engine**

[English](#english) | [简体中文](#简体中文) | [繁體中文](#繁體中文)

</div>

---

## 🌐 Language Selection | 语言选择

- **[English](#english)** - For international users
- **[简体中文](#简体中文)** - 面向中文用户
- **[繁體中文](#繁體中文)** - 面向繁體中文用戶

---

<a name="english"></a>
# 🇺🇸 English

## 🎉 Introduction

**FlowPilot-CLI** is a lightweight, zero-dependency terminal workflow orchestration engine that helps developers automate complex tasks through simple YAML configuration files.

### Why FlowPilot?

- 🚀 **Zero Dependencies** - Only requires Python 3.8+ and PyYAML
- 📋 **YAML-Driven** - Define workflows in simple, readable YAML
- 🎯 **Task Dependencies** - Automatically resolves and executes task dependencies
- 📊 **TUI Dashboard** - Real-time monitoring of workflow execution
- 🧩 **Template System** - Built-in templates for common scenarios
- 🔧 **Highly Extensible** - Easy to extend with custom functionality

## ✨ Core Features

| Feature | Description |
|---------|-------------|
| **Dependency Management** | Define task dependencies, FlowPilot executes them in correct order |
| **Parallel Execution** | Support for parallel task execution |
| **Variable Substitution** | Template variables with `${{ }}` syntax |
| **Environment Variables** | Global and per-step environment variable support |
| **Retry Logic** | Automatic retry with configurable attempts and delays |
| **Conditionals** | Conditional task execution with `if` statements |
| **Error Handling** | Continue on error or fail fast options |
| **TUI Monitoring** | Beautiful terminal UI for real-time monitoring |

## 🚀 Quick Start

### Installation

```bash
# Install from PyPI (coming soon)
pip install flowpilot-cli

# Or install from source
git clone https://github.com/gitstq/FlowPilot-CLI.git
cd FlowPilot-CLI
pip install -e .
```

### Your First Workflow

Create a file named `hello.yml`:

```yaml
name: hello-world
version: "1.0"
description: My first FlowPilot workflow

tasks:
  greet:
    steps:
      - run: echo "Hello, FlowPilot!"
  
  celebrate:
    depends_on: [greet]
    steps:
      - run: echo "🎉 Workflow completed!"
```

Run it:

```bash
flowpilot run hello.yml
```

## 📖 Usage Guide

### CLI Commands

```bash
# Run a workflow
flowpilot run workflow.yml

# Run with variables
flowpilot run workflow.yml -v KEY=value

# Validate workflow syntax
flowpilot validate workflow.yml

# Create from template
flowpilot init my-workflow -t basic

# List available templates
flowpilot list

# Monitor with TUI
flowpilot monitor workflow.yml

# Export to other formats
flowpilot export workflow.yml json
```

### Workflow Syntax

```yaml
name: my-workflow
version: "1.0"
description: A sample workflow

# Global environment variables
env:
  GLOBAL_VAR: value

# Workflow variables
vars:
  greeting: "Hello"

tasks:
  # Task with dependencies
  build:
    description: Build the project
    steps:
      - name: clean
        run: rm -rf build/
      - name: compile
        run: make build
        timeout: 300
        retry: 3
  
  test:
    description: Run tests
    depends_on: [build]
    steps:
      - run: make test
        ignore_error: true
  
  deploy:
    description: Deploy to production
    depends_on: [test]
    steps:
      - run: make deploy
        if: "${{ env.DEPLOY_ENV }} == 'production'"
```

## 💡 Design Philosophy

FlowPilot was designed with the following principles:

1. **Simplicity First** - Easy to learn, easy to use
2. **Unix Philosophy** - Do one thing well
3. **Developer Experience** - Clear error messages and helpful defaults
4. **Zero Dependencies** - Minimal installation requirements
5. **Extensibility** - Easy to customize and extend

## 📦 Templates

FlowPilot includes built-in templates for common scenarios:

- **basic** - Simple workflow template
- **ci-cd** - CI/CD pipeline template
- **backup** - Automated backup workflow
- **deploy** - Deployment workflow
- **data-pipeline** - Data processing pipeline

## 🤝 Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'feat: Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## 📄 License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

---

<a name="简体中文"></a>
# 🇨🇳 简体中文

## 🎉 项目介绍

**FlowPilot-CLI** 是一款轻量级、零依赖的终端工作流编排引擎，帮助开发者通过简单的 YAML 配置文件自动化复杂任务。

### 为什么选择 FlowPilot？

- 🚀 **零依赖** - 仅需 Python 3.8+ 和 PyYAML
- 📋 **YAML 驱动** - 使用简单、可读的 YAML 定义工作流
- 🎯 **任务依赖** - 自动解析并执行任务依赖关系
- 📊 **TUI 监控** - 实时监控工作流执行的终端界面
- 🧩 **模板系统** - 内置常见场景的模板
- 🔧 **高度可扩展** - 易于扩展自定义功能

## ✨ 核心特性

| 特性 | 描述 |
|------|------|
| **依赖管理** | 定义任务依赖，FlowPilot 按正确顺序执行 |
| **并行执行** | 支持任务并行执行 |
| **变量替换** | 使用 `${{ }}` 语法的模板变量 |
| **环境变量** | 支持全局和每步环境变量 |
| **重试机制** | 可配置重试次数和延迟的自动重试 |
| **条件执行** | 使用 `if` 语句的条件任务执行 |
| **错误处理** | 出错继续或快速失败选项 |
| **TUI 监控** | 美观的终端界面实时监控 |

## 🚀 快速开始

### 安装

```bash
# 从 PyPI 安装（即将推出）
pip install flowpilot-cli

# 或从源码安装
git clone https://github.com/gitstq/FlowPilot-CLI.git
cd FlowPilot-CLI
pip install -e .
```

### 您的第一个工作流

创建一个名为 `hello.yml` 的文件：

```yaml
name: hello-world
version: "1.0"
description: 我的第一个 FlowPilot 工作流

tasks:
  greet:
    steps:
      - run: echo "Hello, FlowPilot!"
  
  celebrate:
    depends_on: [greet]
    steps:
      - run: echo "🎉 工作流执行完成！"
```

运行：

```bash
flowpilot run hello.yml
```

## 📖 使用指南

### CLI 命令

```bash
# 运行工作流
flowpilot run workflow.yml

# 使用变量运行
flowpilot run workflow.yml -v KEY=value

# 验证工作流语法
flowpilot validate workflow.yml

# 从模板创建
flowpilot init my-workflow -t basic

# 列出可用模板
flowpilot list

# TUI 监控模式运行
flowpilot monitor workflow.yml

# 导出为其他格式
flowpilot export workflow.yml json
```

### 工作流语法

```yaml
name: my-workflow
version: "1.0"
description: 示例工作流

# 全局环境变量
env:
  GLOBAL_VAR: value

# 工作流变量
vars:
  greeting: "Hello"

tasks:
  # 带依赖的任务
  build:
    description: 构建项目
    steps:
      - name: clean
        run: rm -rf build/
      - name: compile
        run: make build
        timeout: 300
        retry: 3
  
  test:
    description: 运行测试
    depends_on: [build]
    steps:
      - run: make test
        ignore_error: true
  
  deploy:
    description: 部署到生产环境
    depends_on: [test]
    steps:
      - run: make deploy
        if: "${{ env.DEPLOY_ENV }} == 'production'"
```

## 💡 设计理念

FlowPilot 遵循以下设计原则：

1. **简洁优先** - 易于学习，易于使用
2. **Unix 哲学** - 做好一件事
3. **开发者体验** - 清晰的错误消息和有用的默认值
4. **零依赖** - 最小化安装要求
5. **可扩展性** - 易于定制和扩展

## 📦 模板

FlowPilot 包含常见场景的内置模板：

- **basic** - 简单工作流模板
- **ci-cd** - CI/CD 流水线模板
- **backup** - 自动备份工作流
- **deploy** - 部署工作流
- **data-pipeline** - 数据处理流水线

## 🤝 贡献指南

欢迎贡献！请随时提交 Pull Request。

1. Fork 本仓库
2. 创建您的功能分支 (`git checkout -b feature/AmazingFeature`)
3. 提交您的更改 (`git commit -m 'feat: 添加某个 AmazingFeature'`)
4. 推送到分支 (`git push origin feature/AmazingFeature`)
5. 打开 Pull Request

## 📄 开源协议

本项目采用 MIT 协议开源 - 查看 [LICENSE](LICENSE) 文件了解详情。

---

<a name="繁體中文"></a>
# 🇹