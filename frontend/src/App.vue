<template>
  <div id="app">
    <el-container>
      <el-header>
        <div class="header-content">
          <h1>LogWatcher 日志监控系统</h1>
          <nav class="nav-container">
            <router-link to="/dashboard" class="nav-item" :class="{ active: $route.path === '/dashboard' }">
              📊 仪表盘
            </router-link>
            <router-link to="/news" class="nav-item" :class="{ active: $route.path === '/news' }">
              📰 新闻收集
            </router-link>
            <router-link to="/cursor" class="nav-item" :class="{ active: $route.path === '/cursor' }">
              🎯 Cursor 更新
            </router-link>
          </nav>
        </div>
      </el-header>
      <el-main>
        <router-view />
      </el-main>
    </el-container>
  </div>
</template>

<script>
export default {
  name: 'App'
}
</script>

<style>
#app {
  font-family: 'Avenir', Helvetica, Arial, sans-serif;
  -webkit-font-smoothing: antialiased;
  -moz-osx-font-smoothing: grayscale;
  color: #2c3e50;
}

.header-content {
  display: flex;
  align-items: center;
  justify-content: space-between;
  height: 100%;
  width: 100%;
}

.header-content nav {
  flex: 1;
  display: flex;
  justify-content: center;
  min-width: 500px;
}

.header-content h1 {
  margin: 0;
  color: #409eff;
}

.el-header {
  background-color: #fff;
  box-shadow: 0 2px 4px rgba(0, 0, 0, 0.1);
}

.el-main {
  background-color: #f5f5f5;
  min-height: calc(100vh - 60px);
}

/* 自定义导航样式 */
.nav-container {
  display: flex;
  gap: 0;
  align-items: center;
  justify-content: center;
}

.nav-item {
  display: flex;
  align-items: center;
  justify-content: center;
  padding: 0 20px;
  height: 60px;
  color: #606266;
  text-decoration: none;
  font-size: 14px;
  font-weight: 500;
  border-bottom: 2px solid transparent;
  transition: all 0.3s ease;
}

.nav-item:hover {
  color: #409eff;
  background-color: #f5f7fa;
}

.nav-item.active {
  color: #409eff;
  border-bottom-color: #409eff;
}
</style> 