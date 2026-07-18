# 律盾（LawShield）数字法务系统 - 后端内核

本项目为“律盾（LawShield）”—— 基于 Agent Loop 架构、弹性路由与决策溯源的跨企业级数字法务专家系统后端代码库。

## 🛠️ 技术选型
*   **API 框架**: Python 3.11+ & FastAPI (高效异步并发，基于 Pydantic v2 进行强类型校验)
*   **状态化编排**: LangGraph (多智能体 Agent Loop 状态流转与 HITL 中断控制)
*   **数据底座**: PostgreSQL + PGVector (业务流水与向量法条检索一库合并)
*   **高性能缓存**: Redis (提供公共标准条款的语义缓存与防伪 CSRF state 校验)
*   **核心辅助库**:
    *   `pyahocorasick`: 基于 C 底层的 AC 自动机多模式匹配高险熔断网关
    *   `networkx`: DAG 拓扑排序算法，用于法理效力位阶强消解
    *   `weasyprint`: 异步 PDF 免责合同渲染引擎
    *   `prometheus-fastapi-instrumentator` & `loguru`: 本地化监控与诊断

---

## 📁 目录架构设计
```
E:\UGit\Law-Agent-backend\
├── app/
│   ├── __init__.py
│   ├── main.py             # FastAPI 应用入口，挂载全局件与 Prometheus 监控
│   ├── core/               # 基础核心配置
│   │   ├── config.py       # Pydantic-settings 动态加载环境变量 (.env)
│   │   ├── database.py     # SQLAlchemy 异步引擎及 Session 纳管
│   │   └── security.py     # JWT Pass 通行证签发、验证与当前用户注入
│   ├── models/             # SQLAlchemy 实体关系模型
│   │   ├── user.py         # 用户模型 (GitHub 映射)
│   │   ├── contract.py     # 合同主体预存表
│   │   ├── audit.py        # 人类签字防篡改审计日志表
│   │   └── token.py        # Token 消耗计量明细流水表
│   ├── schemas/            # Pydantic 接口契约规范 (Request/Response)
│   │   ├── auth.py
│   │   ├── contract.py
│   │   ├── audit.py
│   │   └── metrics.py
│   ├── routers/            # 路由网关控制器
│   │   ├── auth.py         # 三方 GitHub 鉴权登录
│   │   ├── contracts.py    # 合同接收校验、前置 5 层敏感词防护护栏
│   │   ├── agent.py        # SSE 流式多智能体对审思考链
│   │   ├── audit.py        # HITL 人类签字防篡改存证与反馈接收
│   │   └── reports.py      # Weasyprint 免责 PDF 导出及 Token 计量看板
│   └── services/           # 核心业务服务层
│       ├── extractor.py    # Markdown 拓扑标题提取及层次化切片 (室友 C 负责)
│       ├── gateway.py      # 单例模式 AC 自动机高险拦截与分流路由 (室友 B 负责)
│       ├── agent_engine.py # LangGraph 节点图流转及效力位阶 DAG 剪枝消解 (队长负责)
│       ├── memory.py       # PGVector 增量进化热记忆回填管道 (室友 C 负责)
│       ├── metrics.py      # 本地 Token 计量折算器 (室友 B 协助)
│       ├── pdf_generator.py# weasyprint 异步 PDF 水印渲染
│       └── notification.py # WebSocket 站内弹窗与异步 SMTP 告警 (室友 A/B 负责)
├── .env.example            # 配置样板
├── requirements.txt        # 依赖清单
└── README.md
```

---

## 👥 团队分工与文件归属

为了避免多人协作产生 Git 冲突，本系统进行了极高内聚的解耦设计，各成员专注开发各自负责的文件：

### 1. 队长 (技术负责人 & 全栈架构师)
*   **主控文件**: 
    *   [app/main.py](file:///E:/UGit/Law-Agent-backend/app/main.py)
    *   [app/services/agent_engine.py](file:///E:/UGit/Law-Agent-backend/app/services/agent_engine.py) (LangGraph 流程流转 & NetworkX 效力位阶拓扑排序消解)
*   **任务**: 全局架构把控，编写最核心的智能体消解逻辑。

### 2. AI 开发工程师 (室友 B 协助)
*   **主控文件**: 
    *   [app/services/gateway.py](file:///E:/UGit/Law-Agent-backend/app/services/gateway.py) (AC 自动机初始化与动态路由)
    *   [app/routers/agent.py](file:///E:/UGit/Law-Agent-backend/app/routers/agent.py) (SSE 流式输出接口)

### 3. 后端开发工程师 (室友 B & 室友 A 协助)
*   **主控文件**: 
    *   [app/routers/auth.py](file:///E:/UGit/Law-Agent-backend/app/routers/auth.py) (GitHub OAuth 鉴权及 JWT 签发)
    *   [app/routers/audit.py](file:///E:/UGit/Law-Agent-backend/app/routers/audit.py) (HITL 签字存证、SHA-256 签名)
    *   [app/services/metrics.py](file:///E:/UGit/Law-Agent-backend/app/services/metrics.py) (Token 计量流水落库)
    *   [app/services/notification.py](file:///E:/UGit/Law-Agent-backend/app/services/notification.py) (WebSocket + SMTP 邮件告警)

### 4. 数据治理工程师 (室友 C)
*   **主控文件**: 
    *   [app/services/extractor.py](file:///E:/UGit/Law-Agent-backend/app/services/extractor.py) (Markdown 归一化与层级标题反向路径拼接)
    *   [app/services/memory.py](file:///E:/UGit/Law-Agent-backend/app/services/memory.py) (PGVector 专属热记忆自进化反馈插入)

---

## 🚀 启动与部署

### 1. 创建并激活虚拟环境
```bash
python -m venv venv
# Windows 激活
.\\venv\\Scripts\\activate
# macOS/Linux 激活
source venv/bin/activate
```

### 2. 安装依赖
```bash
pip install -r requirements.txt
```

### 3. 配置环境变量
复制样板并填入真实密钥：
```bash
copy .env.example .env
```

### 4. 运行服务
```bash
uvicorn app.main:app --reload --port 8000
```
启动后可访问 Swagger API 交互式文档: [http://localhost:8000/docs](http://localhost:8000/docs)
