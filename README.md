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
