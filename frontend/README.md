# 前端项目

本项目是绝缘子缺陷检测系统的前端部分，基于Vue 3和Vite开发，用于与后端YOLOv11目标检测模型进行交互，提供用户友好的界面进行绝缘子缺陷检测。

## 推荐的IDE设置

[VS Code](https://code.visualstudio.com/) + [Vue (Official)](https://marketplace.visualstudio.com/items?itemName=Vue.volar)（并禁用Vetur）。

## 推荐的浏览器设置

- 基于Chromium的浏览器（Chrome, Edge, Brave等）：
  - [Vue.js devtools](https://chromewebstore.google.com/detail/vuejs-devtools/nhdogjmejiglipccpnnnanhbledajbpd)
  - [在Chrome DevTools中启用自定义对象格式化器](http://bit.ly/object-formatters)
- Firefox：
  - [Vue.js devtools](https://addons.mozilla.org/en-US/firefox/addon/vue-js-devtools/)
  - [在Firefox DevTools中启用自定义对象格式化器](https://fxdx.dev/firefox-devtools-custom-object-formatters/)

## TypeScript对`.vue`导入的类型支持

TypeScript默认无法处理`.vue`导入的类型信息，因此我们使用`vue-tsc`替代`tsc` CLI进行类型检查。在编辑器中，我们需要[Volar](https://marketplace.visualstudio.com/items?itemName=Vue.volar)使TypeScript语言服务能够识别`.vue`类型。

## 自定义配置

请参考[Vite配置参考](https://vite.dev/config/)。

## 项目结构

```
frontend/
├── src/                 # 源代码
│   ├── views/           # 页面组件
│   │   ├── AboutView.vue        # 关于页面
│   │   ├── HistoryView.vue      # 历史记录页面 - 查看和管理检测记录
│   │   ├── LoginView.vue        # 登录页面
│   │   ├── RecordDetailView.vue # 记录详情页面 - 查看检测结果详情
│   │   ├── RegisterView.vue     # 注册页面
│   │   ├── UploadView.vue       # 图片上传检测页面 - 上传图片进行缺陷检测
│   │   └── VideoDetect.vue      # 视频/摄像头检测页面 - 视频文件或实时摄像头检测
│   ├── components/      # 通用组件
│   │   ├── DeviceSelector.vue   # 设备选择组件 - 切换CPU/GPU设备
│   │   ├── NavBar.vue           # 导航栏组件 - 应用顶部导航
│   │   └── 其他辅助组件
│   ├── router/          # 路由配置
│   ├── utils/           # 工具函数
│   ├── App.vue          # 应用根组件
│   └── main.ts          # 应用入口文件
├── package.json         # 项目配置
└── vite.config.ts       # Vite配置
```

## 项目设置

```sh
npm install
```

### 开发环境编译和热重载

```sh
npm run dev
```

### 类型检查、编译和生产环境构建

```sh
npm run build
```

### 使用[Vitest](https://vitest.dev/)运行单元测试

```sh
npm run test:unit
```

### 使用[Playwright](https://playwright.dev)运行端到端测试

```sh
# 首次运行时安装浏览器
npx playwright install

# 在CI上测试时，必须先构建项目
npm run build

# 运行端到端测试
npm run test:e2e
# 仅在Chromium上运行测试
npm run test:e2e -- --project=chromium
# 运行特定文件的测试
npm run test:e2e -- tests/example.spec.ts
# 在调试模式下运行测试
npm run test:e2e -- --debug
```

### 使用[ESLint](https://eslint.org/)进行代码检查

```sh
npm run lint
```

## 主要功能

- **图片上传检测**：支持上传图片文件进行绝缘子缺陷检测
- **视频文件检测**：支持上传视频文件进行绝缘子缺陷检测
- **实时摄像头检测**：支持使用本地摄像头进行实时绝缘子缺陷检测
- **历史记录管理**：查看、筛选和管理检测记录
- **检测结果详情**：查看详细的检测结果，包括缺陷类型、置信度等
- **设备管理**：支持在CPU和GPU之间切换，优化检测性能
- **系统状态监控**：显示后端连接状态和模型状态

## 技术栈

- **前端框架**：Vue 3.5.26
- **TypeScript**：5.9.3
- **UI组件库**：Element Plus 2.13.0
- **构建工具**：Vite 7.3.0
- **状态管理**：Pinia 3.0.4
- **路由管理**：Vue Router 4.6.4
- **HTTP客户端**：Axios 1.13.2
- **数据可视化**：Chart.js 4.5.1
