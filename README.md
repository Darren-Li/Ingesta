# 🚀 Data Generation & Validation Tool | 智能数据生成与校验工作台

<p align="center">
  <img src="https://img.shields.io/badge/Version-1.0.0-blue" alt="Version">
  <img src="https://img.shields.io/badge/License-MIT-green" alt="License">
  <img src="https://img.shields.io/badge/Python-3.x-yellow" alt="Python">
</p>

[![English](https://img.shields.io/badge/English-d9d9d9?style=for-the-badge)](README.md)
[![简体中文](https://img.shields.io/badge/简体中文-d9d9d9?style=for-the-badge)](docs/readme/zh-CN.md)


> **一站式解决测试数据痛点：从高质量模拟数据生成到严格的数据质量校验。**

## 💡 项目简介

在软件开发、ETL 测试及算法模型训练中，获取**真实且合规**的测试数据往往是一项耗时的工作。同时，如何快速验证上游数据的完整性与准确性也是数据工程师面临的挑战。

本项目是一个轻量级、可视化的 Web 工具集，包含两大核心模块：
1.  **Data Generation (数据生成)**：通过可视化配置快速生成海量、符合业务逻辑的 Mock 数据。
2.  **Data Validation (数据校验)**：基于 JSON Schema 定义规则，自动化校验上传文件的字段类型、枚举值及格式。

## ✨ 核心功能特性

### 1. 🎲 数据生成器 (Data Generator)
告别手写 SQL 或 Python 脚本造数，通过 GUI 界面即可定义复杂的数据结构。

- **可视化字段配置**：支持姓名、年龄、性别、时间序列等多种数据类型，支持自定义枚举值列表（如：抖音, 京东, 天猫）。
- **约束条件控制**：精确设置数值范围（Min/Max）、缺失率（Null Rate）以及显示格式。
- **模板化管理**：支持保存常用的数据结构为“模板”（如：电商用户表、订单表），一键加载复用，提升重复造数效率。
- **即时预览与导出**：实时预览生成的 Top 50 行数据，支持一键下载完整的 CSV 文件。

### 2. 🛡️ 数据校验器 (Data Validator)
确保入库数据的质量，防止脏数据污染下游系统。

- **JSON Schema 驱动**：采用业界标准的 JSON Schema 定义校验规则，支持 String, Integer, Enum, Format (Email) 等多种类型检查。
- **Excel 批量校验**：支持拖拽上传 `.xlsx` / `.xls` 文件，系统自动根据选定模板进行全量扫描。
- **详细的校验报告**：提供任务列表视图，清晰展示校验结果（Success/Failed）。针对失败的任务，可查看具体的错误详情，快速定位问题数据。
- **V2 版本构建器**：内置可视化的 Template Builder，无需手写代码即可构建复杂的校验逻辑。

## 📸 界面预览

### 数据生成模块
| 数据生成配置 | 模板管理 | 任务结果预览 |
| :---: | :---: | :---: |
| ![Generator Config](/docs/img/data_generation.png) | ![Template Manager](/docs/img/template_screenshot.png) | ![Task Result](/docs/img/task_screenshot.png) |
| *灵活配置字段类型与约束* | *保存并复用数据结构* | *查看生成结果并下载 CSV* |

### 数据校验模块
| 校验规则定义 | 校验任务列表 | 模板构建器 V2 |
| :---: | :---: | :---: |
| ![Validator Rule](/docs/img/validator_screenshot.png) | ![Task List](/docs/img/data_validation.png) | ![Builder V2](/docs/img/builder_screenshot.png) |
| *基于 JSON Schema 的规则引擎* | *清晰的 Pass/Fail 状态追踪* | *可视化构建校验逻辑* |

## 🚀 快速开始

### 环境准备
确保您的机器上安装了 Python 3.8+。

### 安装依赖
```bash
git clone https://github.com/your-username/data-gen-val-tool.git
cd data-gen-val-tool
pip install -r requirements.txt