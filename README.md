# 本地生活旅行综合演示原型系统 · 启动说明

> 《软件架构与应用开发实践》课程实训原型：仿大众点评 + 携程
> 架构：前后端分离（Vue 3 前端 + FastAPI 极简后端），**数据源为内存集合，不持久化**

---

## 一、环境要求

| 项目 | 本机实测版本 | 说明 |
| --- | --- | --- |
| Python | 3.12.2 | 基础解释器：`C:\Users\王一龙\AppData\Local\Programs\Python\Python312\python.exe` |
| Node.js | v26.4.0 | `D:\wxdev\node\node.exe`，全机唯一安装 |
| npm | 11.17.0 | 随 Node 提供 |

> 注意：系统 PATH 中的 `python` 是 Microsoft Store 的 0 字节占位符，**不要使用**，请一律使用项目虚拟环境内的解释器。

---

## 二、首次准备（已执行过，可跳过）

```powershell
# 1. 创建虚拟环境（仅后端使用；前端用 npm 管理依赖）
C:\Users\王一龙\AppData\Local\Programs\Python\Python312\python.exe -m venv D:\Ctrip\.venv

# 2. 安装后端依赖
D:\Ctrip\.venv\Scripts\python.exe -m pip install -r D:\Ctrip\requirements.txt

# 3. 安装前端依赖
cd D:\Ctrip\frontend
npm install
```

---

## 三、启动服务（两个终端，都要保持开启）

### 终端 1：启动后端

```powershell
cd D:\Ctrip\backend
D:\Ctrip\.venv\Scripts\python.exe -m uvicorn app.main:app --host 127.0.0.1 --port 8000
```

- 接口文档（Swagger）：http://127.0.0.1:8000/docs
- 健康探针：http://127.0.0.1:8000/api/health

### 终端 2：启动前端

```powershell
cd D:\Ctrip\frontend
npm run dev
```

- 访问地址：http://127.0.0.1:5173
- 前端通过 Vite 代理把 `/api` 转发到后端 `127.0.0.1:8000`，无需额外配置跨域

---

## 四、现场演示动线

1. 首页浏览（轮播 / 分类导航 / 推荐门店与酒店）
2. 搜索关键词，跳转搜索结果页
3. 本地生活：门店筛选、排序 → 门店详情 → 团购套餐 → 用户评论
4. 旅行住宿：日历选入住/退房 → 酒店筛选、排序 → 酒店详情 → 房型 → 酒店评价
5. 模拟预约下单（选套餐/房型 → 填姓名手机号 → 选时间 → 提交成功）
6. 个人中心：查看模拟订单列表 → 订单详情 → 模拟取消预约
7. 口头说明原型限制：数据存于内存，服务重启后新增订单与取消状态全部丢失；本原型无登录注册、无商家与管理后台

---

## 五、原型限制与注意事项（答辩必须主动说明）

1. **不持久化**：所有业务数据来自后端内存集合，服务重启后新增模拟订单全部丢失。
2. **无鉴权**：无用户注册登录，个人中心展示内存中的全部模拟订单。
3. **不做真实支付与消息通知**：下单与取消均只做内存数据变更与界面反馈。
4. **演示中途不要重启后端**，否则演示中新建的订单会消失。
5. 页面图片使用**离线生成的占位图**（CSS 渐变块），不依赖外网，断网也可正常演示。

---

## 六、运行环境说明（Node 26 的两个坑与规避方式，已实测）

本机 Node.js 为 **v26.4.0**（全机唯一安装、无 nvm）。在两个环节遇到 Windows 文件监听问题，均已规避：

| 现象 | 原因 | 规避方式 |
| --- | --- | --- |
| `npm run dev` 偶发崩溃退出：`EBUSY: resource busy or locked, watch ...App.vue.tmpdir/App.vue.tmp` | Node 26 原生文件监听撞上编辑器/工具写入产生的临时文件 | 已在 `frontend/vite.config.js` 改为**轮询监听**（`server.watch.usePolling = true`，忽略 `*.tmpdir`），多次改文件后 dev server 稳定存活 |
| `uvicorn --reload` 进程被杀死 | watchfiles 在 Windows 上会撞同类临时文件 | 后端**不带 `--reload` 启动**，改完后端代码后手动重启即可 |

> 若更换演示机仍出现兼容问题，可按 `REQUIREMENTS.md` 第七节预案回退到 Node.js 20/22 LTS。

---

## 七、自测与验收命令（每阶段均已实测通过）

### 后端（3 个自检脚本，需先启动后端服务）

```powershell
cd D:\Ctrip\backend
$env:PYTHONIOENCODING='utf-8'   # 避免 GBK 控制台下的中文与 ¥ 字符报错

D:\Ctrip\.venv\Scripts\python.exe scripts\selfcheck.py      # 数据层：28 项
D:\Ctrip\.venv\Scripts\python.exe scripts\check_api.py      # 接口 I1~I10：35 项
D:\Ctrip\.venv\Scripts\python.exe scripts\e2e_demo_flow.py  # 端到端演示流程：29 项
```

| 脚本 | 覆盖内容 |
| --- | --- |
| `scripts/selfcheck.py` | 内存数据规模下限、筛选/排序逻辑、详情数据、下单与取消的内存行为 |
| `scripts/check_api.py` | I1~I10 全部接口的返回结构、筛选排序效果、日历晚数、订单闭环、错误码 |
| `scripts/e2e_demo_flow.py` | 现场演示动线 7 步（首页→搜索→本地生活→旅行住宿→下单→个人中心→原型限制） |

### 前端（构建 + 渲染级测试）

```powershell
cd D:\Ctrip\frontend
npm run build     # 生产构建校验（8 个路由分包）
npm test          # 渲染级测试：16 项（vitest + happy-dom，挂载真实页面组件断言渲染内容）
```

### 验收结论（实测）

| 检查项 | 结果 |
| --- | --- |
| 数据层自检 | **28 / 28 通过** |
| 接口自检 I1~I10 | **35 / 35 通过** |
| 端到端演示流程 | **29 / 29 通过** |
| 前端渲染测试 | **16 / 16 通过** |
| 前端生产构建 | 通过（8 个路由分包） |
| 重启丢失实测 | 重启前 6 条订单 → 重启后回到 3 条预置订单，新建订单查询返回 404，**证明未持久化** |

---

## 八、代码仓库

- 远端：https://github.com/yyyJ8/local-travel-hub.git （分支 `main`）
- 已排除：`.venv/`、`node_modules/`、`dist/`（见 `.gitignore`）
- 提交约定：**每完成一个阶段即提交一次**，提交信息按「阶段N：内容」格式编写

